"""Relevance: embedding similarity to the SoilWise topic profile + keyword hits.

Batch API: score_all(records) -> {record_id: CheckResult}. The model is loaded lazily on CPU.
"""
import hashlib
import os

import numpy as np

from qc import config as C
from qc.db import connect, get_schema
from qc.models import CheckResult, Record
from qc.topics import KEYWORDS, SEEDS


def fetch_subject_text() -> dict[str, str]:
    s = get_schema()
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SET statement_timeout = '120s'")
        cur.execute(f"""SELECT rs.record_id, string_agg(sb.label, '; ')
                        FROM {s}.record_subject rs JOIN {s}.subjects sb ON sb.id = rs.subject_id
                        GROUP BY rs.record_id""")
        return {str(k): v for k, v in cur.fetchall()}


def _text(r: Record, subjects: dict[str, str]) -> str:
    parts = [r.title or "", (r.abstract or "")[:1200], subjects.get(r.id, "")[:300]]
    return ". ".join(p for p in parts if p)


def _keyword_hits(text: str) -> int:
    t = f" {text.lower()} "
    return sum(k in t for k in KEYWORDS)


CACHE = "out/emb_cache.npz"


def _encode_cached(model, texts: list[str], batch_size: int) -> np.ndarray:
    """Embeddings cached by text hash, so threshold/keyword tuning reruns are fast."""
    keys = [hashlib.md5(f"{C.EMBEDDING_MODEL}|{t}".encode()).hexdigest() for t in texts]
    cache = {}
    if os.path.exists(CACHE):
        z = np.load(CACHE, allow_pickle=False)
        cache = dict(zip(z["keys"].tolist(), z["vecs"]))
    missing = [i for i, k in enumerate(keys) if k not in cache]
    if missing:
        vecs = model.encode([texts[i] for i in missing], batch_size=batch_size,
                            normalize_embeddings=True, show_progress_bar=True)
        for i, v in zip(missing, vecs):
            cache[keys[i]] = v
        np.savez(CACHE, keys=np.array(list(cache)), vecs=np.stack(list(cache.values())))
    return np.stack([cache[k] for k in keys])


def score_all(records: list[Record], batch_size: int = 64) -> dict[str, CheckResult]:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(C.EMBEDDING_MODEL, device="cpu")
    model.max_seq_length = 256
    seeds = model.encode(SEEDS, normalize_embeddings=True)

    subjects = fetch_subject_text()
    texts = [_text(r, subjects) for r in records]
    emb = _encode_cached(model, texts, batch_size)

    sims = emb @ seeds.T                                   # (n, n_seeds)
    top = np.sort(sims, axis=1)[:, -3:].mean(axis=1)       # mean of 3 best-matching themes
    out = {}
    for r, text, sim in zip(records, texts, top):
        hits = _keyword_hits(text)
        emb_score = float(np.clip((sim - C.SIM_LOW) / (C.SIM_HIGH - C.SIM_LOW), 0, 1))
        kw_score = min(hits / 3, 1.0)
        score = 0.7 * emb_score + 0.3 * kw_score
        flags, major = [], []
        if score < C.OFFTOPIC_MAX and hits == 0:
            major.append("possibly_off_topic")
        elif score < C.WEAK_TOPIC_MAX:
            flags.append("weak_topic_match")
        thin = len((r.abstract or "").strip()) < C.SHORT_ABSTRACT_CHARS and not subjects.get(r.id)
        if thin:
            # Too little text for an embedding to mean anything: relevance is unknown, not off-topic.
            res = CheckResult("relevance", score, ["relevance_unknown_thin_text"], [], applies=False)
        else:
            res = CheckResult("relevance", score, flags, major)
        res.sim = float(sim); res.hits = hits          # for reporting
        out[r.id] = res
    return out
