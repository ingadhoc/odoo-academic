##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests import Form
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSplitName(TransactionCase):
    """The module splits the name of the academic contacts in four parts.

    Through the form the only way in is the parts: the module hides the name
    for students, relatives and families. The other way round -- a name that
    arrives whole and has to be split -- happens on an import or over RPC, so
    those cases go through create/write.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]
        cls.family = cls.Partner.create({"name": "García", "partner_type": "family"})

    def _student_form(self):
        form = Form(self.Partner)
        form.partner_type = "student"
        form.parent_id = self.family
        return form

    def test_the_form_builds_the_name_from_the_four_parts(self):
        form = self._student_form()
        form.firstname = "Sofía"
        form.middlename = "Ana"
        form.lastname = "García"
        form.second_lastname = "Pérez"
        student = form.save()
        self.assertEqual(student.name, "Sofía Ana García Pérez")

    def test_the_parts_that_are_empty_leave_no_double_space(self):
        form = self._student_form()
        form.firstname = "Sofía"
        form.lastname = "García"
        student = form.save()
        self.assertEqual(student.name, "Sofía García")

    def test_editing_a_part_over_the_orm_rebuilds_the_name(self):
        """Over the ORM -- an import, a server action -- the parts survive."""
        form = self._student_form()
        form.firstname = "Sofía"
        form.lastname = "García"
        student = form.save()
        student.second_lastname = "Pérez"
        self.assertEqual(student.name, "Sofía García Pérez")
        self.assertEqual(student.lastname, "García")

    def test_a_name_that_arrives_whole_is_split_on_a_student(self):
        student = self.Partner.create(
            {"name": "Sofía García Pérez", "partner_type": "student", "parent_id": self.family.id}
        )
        self.assertEqual(student.firstname, "Sofía")
        self.assertEqual(student.lastname, "García Pérez")

    def test_a_single_word_name_leaves_no_last_name(self):
        relative = self.Partner.create({"name": "Carlos", "partner_type": "parent"})
        self.assertEqual(relative.firstname, "Carlos")
        self.assertFalse(relative.lastname)

    def test_on_a_family_the_whole_name_is_the_last_name(self):
        self.assertEqual(self.family.lastname, "García")
        self.assertFalse(self.family.firstname)

    def test_a_contact_that_is_not_academic_keeps_its_name(self):
        other = self.Partner.create({"name": "Proveedor SA"})
        self.assertEqual(other.name, "Proveedor SA")
        self.assertFalse(other.firstname)
        self.assertFalse(other.lastname)

    def test_duplicating_a_student_does_not_add_the_copy_suffix(self):
        """From 20 on, a Char called `name` is copied with " (copy)" at the end
        unless the field declares `copy`. Here the name comes from the parts, so
        the suffix would leave it out of sync with them."""
        form = self._student_form()
        form.firstname = "Sofía"
        form.lastname = "García"
        student = form.save()
        copy = student.copy()
        self.assertEqual(copy.name, "Sofía García")
        self.assertEqual(copy.firstname, "Sofía")
        self.assertEqual(copy.lastname, "García")

    def test_a_name_that_arrives_whole_is_split_with_the_type_from_the_context(self):
        """Importing from a list, the type arrives as a default in the context."""
        student = self.Partner.with_context(default_partner_type="student").create(
            {"name": "Lucía Sosa", "parent_id": self.family.id}
        )
        self.assertEqual(student.partner_type, "student")
        self.assertEqual(student.firstname, "Lucía")
        self.assertEqual(student.lastname, "Sosa")

    def test_a_family_created_from_the_context_gets_its_last_name(self):
        """The last name is required on a family: empty, the form cannot save."""
        family = self.Partner.with_context(default_partner_type="family").create({"name": "Quiroga"})
        self.assertEqual(family.partner_type, "family")
        self.assertEqual(family.lastname, "Quiroga")

    def test_a_name_that_arrives_whole_replaces_every_part(self):
        """An import that fixes a name has to leave the old parts behind."""
        form = self._student_form()
        form.firstname = "Sofía"
        form.middlename = "Ana"
        form.lastname = "García"
        form.second_lastname = "Pérez"
        student = form.save()

        student.write({"name": "Mateo Sosa"})

        self.assertEqual(student.name, "Mateo Sosa")
        self.assertEqual(student.firstname, "Mateo")
        self.assertEqual(student.lastname, "Sosa")
        self.assertFalse(student.middlename)
        self.assertFalse(student.second_lastname)

    def test_editing_a_part_through_the_form_keeps_the_last_name(self):
        """Used to be a bug, and not from the 19 -> 20 jump: it behaved the same
        on both.

        The cycle between the name and its parts was guarded with
        `skip_name_split_compute` in the context, which holds over the ORM but
        not through the form, where the client recomputes on its own: rebuilding
        the name fired `_compute_lastname` again and the last name swallowed
        everything after the first word. The guard is now a consistency check,
        so it holds whichever way in.
        """
        form = self._student_form()
        form.firstname = "Sofía"
        form.lastname = "García"
        student = form.save()

        with Form(student) as editing:
            editing.middlename = "Ana"
            editing.second_lastname = "Pérez"

        self.assertEqual(student.name, "Sofía Ana García Pérez")
        self.assertEqual(student.firstname, "Sofía")
        self.assertEqual(student.middlename, "Ana")
        self.assertEqual(student.lastname, "García")
        self.assertEqual(student.second_lastname, "Pérez")
