def migrate(cr, version):
    # correlative_ids used to point at the plan that comes BEFORE, and now points at the ones
    # that come after: a base with the old data would send the students backwards
    cr.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'academic_section_correlative_ids_rel'")
    if not cr.fetchone():
        return
    cr.execute(
        """
        UPDATE academic_section_correlative_ids_rel
           SET section_id = correlative_id,
               correlative_id = section_id
        """
    )
