"""Read-only schema discovery. Writes schema_report.md (contains no credentials).

Usage:
    python -m qc.discover [--samples N] [--out schema_report.md]
"""
import argparse

from psycopg import sql

from qc.db import connect, get_schema

MAX_CELL = 200


def fmt(v) -> str:
    s = str(v).replace("\n", " ").replace("|", "\\|")
    return s if len(s) <= MAX_CELL else s[:MAX_CELL] + "…"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=0, help="sample rows per table (default 0)")
    ap.add_argument("--out", default="schema_report.md")
    args = ap.parse_args()

    schema = get_schema()
    out = [f"# Schema report: `{schema}`\n"]

    with connect(readonly=True) as conn, conn.cursor() as cur:
        cur.execute("SET statement_timeout = '30s'")
        cur.execute(
            """SELECT table_name, table_type FROM information_schema.tables
               WHERE table_schema = %s ORDER BY table_name""",
            (schema,),
        )
        tables = cur.fetchall()
        out.append(f"{len(tables)} tables/views.\n")

        for name, ttype in tables:
            out.append(f"## {name} ({ttype.lower()})\n")

            try:
                cur.execute(sql.SQL("SELECT count(*) FROM {}.{}").format(
                    sql.Identifier(schema), sql.Identifier(name)))
                out.append(f"Rows: {cur.fetchone()[0]}\n")
            except Exception as e:
                conn.rollback()
                cur.execute("SET statement_timeout = '30s'")
                out.append(f"Rows: unavailable ({type(e).__name__})\n")

            cur.execute(
                """SELECT column_name, data_type, is_nullable
                   FROM information_schema.columns
                   WHERE table_schema = %s AND table_name = %s
                   ORDER BY ordinal_position""",
                (schema, name),
            )
            cols = cur.fetchall()
            out.append("| column | type | nullable |\n|---|---|---|")
            out += [f"| {c} | {t} | {n} |" for c, t, n in cols]
            out.append("")

            cur.execute(
                """SELECT kcu.column_name, ccu.table_schema, ccu.table_name, ccu.column_name
                   FROM information_schema.table_constraints tc
                   JOIN information_schema.key_column_usage kcu
                     ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
                   JOIN information_schema.constraint_column_usage ccu
                     ON tc.constraint_name = ccu.constraint_name
                   WHERE tc.constraint_type = 'FOREIGN KEY'
                     AND tc.table_schema = %s AND tc.table_name = %s""",
                (schema, name),
            )
            fks = cur.fetchall()
            if fks:
                out.append("Foreign keys: " + ", ".join(
                    f"{c} → {s}.{t}.{tc}" for c, s, t, tc in fks) + "\n")

            if args.samples > 0:
                cur.execute(sql.SQL("SELECT * FROM {}.{} LIMIT %s").format(
                    sql.Identifier(schema), sql.Identifier(name)), (args.samples,))
                names = [d.name for d in cur.description]
                out.append("Sample rows:\n")
                out.append("| " + " | ".join(names) + " |\n|" + "---|" * len(names))
                for row in cur.fetchall():
                    out.append("| " + " | ".join(fmt(v) for v in row) + " |")
                out.append("")

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
