"""Read-only profiling of validate.records. Writes profile_report.md (no credentials).

Usage: python -m qc.profile [--out profile_report.md]
"""
import argparse

from qc.db import connect, get_schema

FIELDS = ["title", "abstract", "resource_type", "license", "language", "thumbnail",
          "publication_date", "resource_creation_date", "resource_updated_date",
          "spatial", "temporal_start", "temporal_end", "raw_metadata", "url"]


def table(rows, headers):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(str(c).replace("|", "\\|")[:120] for c in r) + " |" for r in rows]
    return out + [""]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="profile_report.md")
    args = ap.parse_args()
    s = get_schema()
    out = ["# Profile of records\n"]

    with connect() as conn, conn.cursor() as cur:
        cur.execute("SET statement_timeout = '60s'")
        q = lambda sqltext: (cur.execute(sqltext), cur.fetchall())[1]

        out.append("## approval_status")
        out += table(q(f"SELECT approval_status, count(*) FROM {s}.records GROUP BY 1 ORDER BY 2 DESC"),
                     ["value", "n"])

        out.append("## Missing / empty rates")
        total = q(f"SELECT count(*) FROM {s}.records")[0][0]
        exprs = ", ".join(
            f"count(*) FILTER (WHERE {f} IS NULL OR btrim({f}::text) IN ('', '{{}}', 'null'))" for f in FIELDS)
        row = q(f"SELECT {exprs} FROM {s}.records")[0]
        out += table([(f, n, f"{100*n/total:.1f}%") for f, n in zip(FIELDS, row)],
                     ["field", "missing", "pct"])

        for col in ["resource_type", "language", "license"]:
            out.append(f"## {col} (top 15)")
            out += table(q(f"SELECT {col}, count(*) FROM {s}.records GROUP BY 1 ORDER BY 2 DESC LIMIT 15"),
                         ["value", "n"])

        out.append("## Text length (abstract, chars)")
        out += table(q(f"""SELECT count(*) FILTER (WHERE length(abstract) < 50),
                                  count(*) FILTER (WHERE length(abstract) BETWEEN 50 AND 199),
                                  count(*) FILTER (WHERE length(abstract) >= 200),
                                  round(avg(length(abstract))), max(length(abstract))
                           FROM {s}.records WHERE abstract IS NOT NULL"""),
                     ["<50", "50-199", ">=200", "avg", "max"])

        out.append("## Date sanity")
        out += table(q(f"""SELECT
            count(*) FILTER (WHERE publication_date > now()),
            count(*) FILTER (WHERE publication_date < '1900-01-01'),
            count(*) FILTER (WHERE temporal_end < temporal_start),
            count(*) FILTER (WHERE resource_updated_date < resource_creation_date),
            count(*) FILTER (WHERE resource_creation_date > publication_date)
            FROM {s}.records"""),
            ["pub in future", "pub <1900", "temporal end<start", "updated<created", "created>published"])

        out.append("## Duplicates")
        out += table(q(f"""SELECT 'identifier', count(*) FROM (SELECT identifier FROM {s}.records
                             GROUP BY 1 HAVING count(*)>1) x
                           UNION ALL SELECT 'lower(title)', count(*) FROM (SELECT lower(btrim(title))
                             FROM {s}.records GROUP BY 1 HAVING count(*)>1) y
                           UNION ALL SELECT 'url', count(*) FROM (SELECT url FROM {s}.records
                             WHERE url IS NOT NULL GROUP BY 1 HAVING count(*)>1) z"""),
                     ["key", "duplicate groups"])

        out.append("## Short / odd titles")
        out += table(q(f"""SELECT count(*) FILTER (WHERE length(title) < 10),
                                  count(*) FILTER (WHERE length(title) > 250),
                                  count(*) FILTER (WHERE title = upper(title) AND length(title) > 10)
                           FROM {s}.records"""), ["<10 chars", ">250 chars", "ALL CAPS"])

        out.append("## Records per source")
        out += table(q(f"""SELECT so.*, count(rs.*) FROM {s}.sources so
                           LEFT JOIN {s}.record_source rs ON rs.source_id = so.id
                           GROUP BY so.id ORDER BY count(rs.*) DESC"""),
                     [d.name for d in cur.description])

        out.append("## Relations coverage (records with >=1)")
        parts = []
        for t in ["record_person", "record_organization", "record_project", "record_subject", "record_source"]:
            parts.append(f"SELECT '{t}', count(DISTINCT record_id) FROM {s}.{t}")
        out += table(q(" UNION ALL ".join(parts)), ["table", "records covered"])

        out.append("## Distributions")
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_schema=%s AND table_name='distributions'", (s,))
        out.append("columns: " + ", ".join(r[0] for r in cur.fetchall()) + "\n")

    open(args.out, "w", encoding="utf-8").write("\n".join(out))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
