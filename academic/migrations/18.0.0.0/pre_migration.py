from datetime import datetime

from odoo import SUPERUSER_ID


def migrate(cr, version):
    cr.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'academic_group' AND column_name = 'year'
    """)
    if not cr.fetchone():
        return

    cr.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'academic_group' AND column_name = 'year_id'
    """)
    if not cr.fetchone():
        cr.execute("ALTER TABLE academic_group ADD COLUMN year_id INTEGER")

    cr.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_name = 'academic_year'
    """)
    if not cr.fetchone():
        cr.execute("""
            CREATE TABLE academic_year (
                id SERIAL PRIMARY KEY,
                create_uid INTEGER,
                create_date TIMESTAMP,
                write_uid INTEGER,
                write_date TIMESTAMP,
                name VARCHAR,
                date_start DATE,
                date_end DATE,
                active BOOLEAN DEFAULT TRUE
            )
        """)

    cr.execute("SELECT DISTINCT year FROM academic_group WHERE year IS NOT NULL")
    years = [row[0] for row in cr.fetchall()]

    year_mapping = {}
    for year in years:
        cr.execute("SELECT id FROM academic_year WHERE name = %s", (f"Ciclo Lectivo {year}",))
        row = cr.fetchone()
        if row:
            year_id = row[0]
        else:
            cr.execute(
                """
                INSERT INTO academic_year (
                    name, date_start, date_end, create_uid, create_date, write_uid, write_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
            """,
                (
                    f"Ciclo Lectivo {year}",
                    f"{year}-03-01",
                    f"{year}-12-20",
                    SUPERUSER_ID,
                    datetime.now(),
                    SUPERUSER_ID,
                    datetime.now(),
                ),
            )
            year_id = cr.fetchone()[0]
        year_mapping[year] = year_id

    for year, year_id in year_mapping.items():
        cr.execute(
            """
            UPDATE academic_group
            SET year_id = %s
            WHERE year = %s
        """,
            (year_id, year),
        )
