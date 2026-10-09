from qc.db import connect, get_schema
from qc.models import Record

COLS = ["id", "identifier", "title", "abstract", "resource_type", "license", "language", "url",
        "publication_date", "resource_creation_date", "resource_updated_date",
        "temporal_start", "temporal_end", "spatial", "approval_status"]


def fetch_records(limit: int | None = None) -> list[Record]:
    s = get_schema()
    cols = ", ".join(f"r.{c}" for c in COLS)
    q = f"""
    WITH
      src AS (SELECT DISTINCT ON (rs.record_id) rs.record_id, so.name
              FROM {s}.record_source rs JOIN {s}.sources so ON so.id = rs.source_id
              ORDER BY rs.record_id, so.name),
      per AS (SELECT record_id, count(*) AS n FROM {s}.record_person GROUP BY record_id),
      org AS (SELECT record_id, count(*) AS n FROM {s}.record_organization GROUP BY record_id),
      sub AS (SELECT record_id, count(*) AS n FROM {s}.record_subject GROUP BY record_id),
      dis AS (SELECT record_id, count(*) AS n FROM {s}.distributions GROUP BY record_id)
    SELECT {cols}, src.name,
      coalesce(per.n, 0), coalesce(org.n, 0), coalesce(sub.n, 0), coalesce(dis.n, 0)
    FROM {s}.records r
      LEFT JOIN src ON src.record_id = r.id
      LEFT JOIN per ON per.record_id = r.id
      LEFT JOIN org ON org.record_id = r.id
      LEFT JOIN sub ON sub.record_id = r.id
      LEFT JOIN dis ON dis.record_id = r.id
    ORDER BY r.created_at, r.id
    {"LIMIT " + str(int(limit)) if limit else ""}"""
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SET statement_timeout = '900s'")
        cur.execute(q)
        return [Record(str(r[0]), *r[1:]) for r in cur.fetchall()]
