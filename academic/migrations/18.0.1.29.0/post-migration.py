def migrate(cr, version):
    # the old m2m had no order: the sequence follows the level ids and the admin
    # reviews it by dragging the lines on the study plan
    cr.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'academic_section_level_ids_rel'")
    if not cr.fetchone():
        return
    cr.execute(
        """
        INSERT INTO academic_section_level (section_id, level_id, sequence, create_uid, create_date, write_uid, write_date)
             SELECT rel.section_id,
                    rel.level_id,
                    10 * row_number() OVER (PARTITION BY rel.section_id ORDER BY rel.level_id),
                    1, now(), 1, now()
               FROM academic_section_level_ids_rel rel
              WHERE NOT EXISTS (
                        SELECT 1
                          FROM academic_section_level line
                         WHERE line.section_id = rel.section_id
                           AND line.level_id = rel.level_id)
        """
    )
