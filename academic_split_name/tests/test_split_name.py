##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.addons.academic_split_name import post_init_hook
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

    def test_the_install_hook_fills_a_contact_that_already_has_one_part(self):
        """Installing fills the parts of the contacts that are already there.

        The parts are emptied over SQL because that is the state the install
        finds: columns that have just been created. A contact carrying one of
        them and no last name has to be filled too -- the form requires the
        last name -- and its name has to come out untouched.
        """
        student = self.Partner.create({"name": "Juan Pérez", "partner_type": "student", "parent_id": self.family.id})
        student.flush_recordset()
        self.env.cr.execute(
            "UPDATE res_partner SET firstname=NULL, lastname=NULL, second_lastname=NULL, middlename='Carlos'"
            " WHERE id=%s",
            (student.id,),
        )
        self.env.invalidate_all()

        post_init_hook(self.env)

        self.assertEqual(student.name, "Juan Pérez")
        self.assertEqual(student.firstname, "Juan")
        self.assertEqual(student.lastname, "Pérez")
        self.assertFalse(student.middlename)

    def test_a_student_created_only_with_the_parts_gets_its_name(self):
        """An import of a roll brings a column per part and no name column.

        The name is built from the parts, so it has to be there before the
        INSERT: the database requires a contact to have one.
        """
        student = self.Partner.with_context(default_partner_type="student").create(
            {"parent_id": self.family.id, "firstname": "Juan", "lastname": "Pérez"}
        )
        self.assertEqual(student.name, "Juan Pérez")

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

    def test_on_a_family_the_whole_name_is_the_last_name(self):
        self.assertEqual(self.family.lastname, "García")

    def test_a_contact_that_is_not_academic_keeps_its_name(self):
        partner = self.Partner.create({"name": "Abigail Peterson"})
        self.assertEqual(partner.name, "Abigail Peterson")
        self.assertFalse(partner.firstname)
        self.assertFalse(partner.lastname)
