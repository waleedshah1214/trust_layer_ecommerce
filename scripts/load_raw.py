import csv
import getpass
from pathlib import Path

import psycopg2

RAW_DIR = Path(r"D:\trust_layer_ecommerce\data\raw")
DB = dict(host="localhost", port=5433, dbname="olist", user="postgres")


def table_name(file: Path) -> str:
    # olist_orders_dataset.csv -> orders
    return file.stem.replace("olist_", "").replace("_dataset", "")


def main():
    password = getpass.getpass("Postgres password: ")
    conn = psycopg2.connect(password=password, **DB)
    cur = conn.cursor()
    cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")

    for file in sorted(RAW_DIR.glob("*.csv")):
        name = table_name(file)
        with open(file, encoding="utf-8-sig", newline="") as f:
            columns = next(csv.reader(f))

        # Every column is stored as text so the raw data stays untouched.
        col_defs = ", ".join(f'"{c}" TEXT' for c in columns)
        cur.execute(f'DROP TABLE IF EXISTS raw."{name}";')
        cur.execute(f'CREATE TABLE raw."{name}" ({col_defs});')

        with open(file, encoding="utf-8-sig", newline="") as f:
            cur.copy_expert(
                f"COPY raw.\"{name}\" FROM STDIN WITH (FORMAT csv, HEADER true)", f
            )

        cur.execute(f'SELECT COUNT(*) FROM raw."{name}";')
        print(f"{name}: {cur.fetchone()[0]:,} rows")

    conn.commit()
    cur.close()
    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()