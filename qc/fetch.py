from qc.db import connect, get_schema
from qc.models import Record

COLS = ["id", "identifier", "title", "abstract", "resource_type", "license", "language", "url",
        "publication_date", "resource_creation_date", "resource_updated_date",
        "temporal_start", "temporal_end", "spatial", "approval_status"]


def fetch_records(limit: int | None = None) -> list[Record]:
    s = get_schema()
    cols = ", ".join(f"r.{c}" for c in COLS)
    q = f"""
    SELECT {cols},
      (SELECT so.name FROM {s}.record_source rs JOIN {s}.sources so ON so.id = rs.source_id
         WHERE rs.record_id = r.id LIMIT 1),
      (SELECT count(*) FROM {s}.record_person x WHERE x.record_id = r.id),
      (SELECT count(*) FROM {s}.record_organization x WHERE x.record_id = r.id),
      (SELECT count(*) FROM {s}.record_subject x WHERE x.record_id = r.id),
      (SELECT count(*) FROM {s}.distributions x WHERE x.record_id = r.id)
    FROM {s}.records r ORDER BY r.created_at, r.id
    {"LIMIT " + str(int(limit)) if limit else ""}"""
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SET statement_timeout = '300s'")
        cur.execute(q)
        return [Record(str(r[0]), *r[1:]) for r in cur.fetchall()]
