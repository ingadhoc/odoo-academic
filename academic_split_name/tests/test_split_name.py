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

    def test_editing_a_part_through_the_form_keeps_the_last_name(self):
        """The defect this fix is about: the last name used to swallow
        everything after the first word, leaving "Ana García Pérez".
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
        self.assertEqual(student.lastname, "García")

    def test_editing_a_part_over_the_orm_rebuilds_the_name(self):
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

    def test_a_name_that_arrives_whole_on_a_write_is_split_too(self):
        student = self.Partner.create({"name": "Sofía García", "partner_type": "student", "parent_id": self.family.id})
        student.write({"name": "Mateo Sosa"})
        self.assertEqual(student.firstname, "Mateo")
        self.assertEqual(student.lastname, "Sosa")

    def test_on_a_family_the_whole_name_is_the_last_name(self):
        self.assertEqual(self.family.lastname, "García")

    def test_a_contact_that_is_not_academic_keeps_its_name(self):
        partner = self.Partner.create({"name": "Abigail Peterson"})
        self.assertEqual(partner.name, "Abigail Peterson")
        self.assertFalse(partner.firstname)
        self.assertFalse(partner.lastname)
