##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import base64
import csv
import io

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged

HEADER = [
    "APELLIDO",
    "NOMBRE ALUMNO",
    "DNI ALUMNO",
    "ETIQUETAS",
    "RESPONSABLE",
    "RELACION",
    "ROLES",
    "DNI RESPONSABLE",
    "TIPO RESPONSABILIDAD AFIP",
    "EMAIL",
    "TELEFONO",
    "CONTACTOS Y ROLES POR ESTUDIANTE",
]


def _row(surname, student, relative, **kwargs):
    """Spreadsheet row in HEADER order, naming only the columns a test cares about."""
    values = {
        "student_dni": "",
        "tags": "",
        "relation": "Padre/Madre",
        "roles": "",
        "relative_dni": "",
        "afip": "",
        "email": "x@x.com",
        "phone": "",
        "links_by_student": "",
    }
    values.update(kwargs)
    return [
        surname,
        student,
        values["student_dni"],
        values["tags"],
        relative,
        values["relation"],
        values["roles"],
        values["relative_dni"],
        values["afip"],
        values["email"],
        values["phone"],
        values["links_by_student"],
    ]


def _reference_rows(afip=""):
    """Four students over three families, every one of them with a paying relative."""
    return [
        _row(
            "SUAREZ CORREA",
            "SIMON OSCAR",
            "CORREA ROXANA",
            student_dni="48879185",
            tags="Beca 50%",
            roles="Responsable de Facturación, Puede Retirar",
            relative_dni="20024910",
            afip=afip,
            email="r@x.com",
            phone="1122334455",
        ),
        _row(
            "AMAYA",
            "LUCIA",
            "AVELLANEDA G",
            student_dni="53761825",
            tags="Hermanos",
            roles="Responsable de Facturación",
            relative_dni="30277377",
            afip=afip,
            email="g@x.com",
        ),
        _row(
            "AMAYA",
            "RODRIGO",
            "AVELLANEDA G",
            student_dni="50963724",
            tags="Hermanos",
            roles="Responsable de Facturación",
            relative_dni="30277377",
            afip=afip,
            email="g@x.com",
        ),
        _row(
            "AMERATTE",
            "MARTINA",
            "GESTO CARMEN",
            relation="Abuelo/a",
            roles="Responsable de Facturación",
            relative_dni="31222333",
            afip=afip,
            email="c@x.com",
        ),
    ]


def _build_csv(rows, header=None):
    buf = io.StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_ALL)
    writer.writerow(header or HEADER)
    for r in rows:
        writer.writerow(r)
    return base64.b64encode(buf.getvalue().encode("utf-8-sig"))


@tagged("post_install", "-at_install")
class TestContactImport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]
        Category = cls.env["res.partner.category"]
        cls.tag_beca = Category.create({"name": "Beca 50%"})
        cls.tag_hermanos = Category.create({"name": "Hermanos"})
        # the AFIP responsibility type only exists with the Argentinian localization installed, and
        # there it is mandatory for the paying role, so every fixture with that role must carry it
        cls.afip_type = None
        if "l10n_ar_afip_responsibility_type_id" in cls.Partner._fields:
            cls.afip_type = cls.env["l10n_ar.afip.responsibility.type"].search([], limit=1)
        cls.afip_name = cls.afip_type.name if cls.afip_type else ""
        # the database may already hold academic contacts (demo data), so every assertion counts
        # what the import created instead of what the database holds. Postgres sequences do not
        # roll back with the test savepoint, so anything a test creates keeps an id above this one
        cls.max_id = cls.Partner.search([], order="id desc", limit=1).id

    def _imported(self, partner_type, name=None):
        domain = [("partner_type", "=", partner_type), ("id", ">", self.max_id)]
        if name:
            domain.append(("name", "=", name))
        return self.Partner.search(domain)

    def _run(self, rows, header=None):
        wizard = self.env["academic.contact.import"].create(
            {
                "file": _build_csv(rows, header),
                "filename": "test.csv",
            }
        )
        wizard.action_import()
        return wizard

    def test_import_creates_structure_and_dedups(self):
        self._run(_reference_rows(self.afip_name))

        families = self._imported("family")
        self.assertEqual(len(families), 3)
        self.assertEqual(len(self._imported("student")), 4)

        amaya = families.filtered(lambda f: f.name == "Familia AMAYA")
        self.assertEqual(len(amaya.student_ids), 2)
        self.assertEqual(len(amaya.student_link_ids), 1)

        dnis = amaya.student_ids.mapped("identification_number")
        self.assertEqual(sorted(dnis), ["50963724", "53761825"])

        simon = self._imported("student").filtered(lambda s: s.identification_number == "48879185")
        self.assertEqual(simon.name, "SUAREZ CORREA SIMON OSCAR")
        self.assertIn(self.tag_beca, simon.category_id)

        amaya_students = amaya.student_ids
        for student in amaya_students:
            self.assertIn(self.tag_hermanos, student.category_id)

        paying = self.env.ref("academic.paying_role")
        withdraw = self.env.ref("academic.withdraw_role")
        suarez = self._imported("family", "Familia SUAREZ CORREA")
        suarez_link = suarez.student_link_ids
        self.assertEqual(suarez_link.partner_id.name, "CORREA ROXANA")
        self.assertEqual(suarez_link.partner_id.vat, "20024910")
        self.assertEqual(suarez_link.partner_id.phone, "1122334455")
        self.assertIn(paying, suarez_link.role_ids)
        self.assertIn(withdraw, suarez_link.role_ids)

        ameratte = families.filtered(lambda f: f.name == "Familia AMERATTE")
        link = ameratte.student_link_ids
        self.assertEqual(link.relationship_id.name, "Abuelo/a")
        self.assertIn(paying, link.role_ids)

    def test_invalid_relationship_raises(self):
        rows = [["PEREZ", "JUAN", "60000001", "", "PEREZ MARIA", "MAMA", "", "20000001", "", "p@x.com", ""]]
        with self.assertRaises(UserError):
            self._run(rows)
        self.assertFalse(self._imported("family", "Familia PEREZ"))

    def test_invalid_role_raises(self):
        rows = [
            [
                "GOMEZ",
                "ANA",
                "60000002",
                "",
                "GOMEZ LUIS",
                "Padre/Madre",
                "Rol Inexistente",
                "20000002",
                "",
                "g@x.com",
                "",
            ]
        ]
        with self.assertRaises(UserError):
            self._run(rows)
        self.assertFalse(self._imported("family", "Familia GOMEZ"))

    def test_paying_role_without_dni_raises(self):
        rows = [_row("LOPEZ", "MATEO", "LOPEZ ANA", roles="Responsable de Facturación")]
        with self.assertRaises(UserError):
            self._run(rows)
        self.assertFalse(self._imported("family", "Familia LOPEZ"))

    def test_invalid_tag_raises(self):
        rows = [
            [
                "LOPEZ",
                "PEDRO",
                "60000003",
                "Etiqueta Inexistente",
                "LOPEZ MARIA",
                "Padre/Madre",
                "",
                "20000003",
                "",
                "l@x.com",
                "",
            ]
        ]
        with self.assertRaises(UserError):
            self._run(rows)
        self.assertFalse(self._imported("family", "Familia LOPEZ"))

    def test_afip_responsibility_assigned(self):
        if not self.afip_type:
            self.skipTest("l10n_ar localization not installed")
        rows = [
            _row("RUIZ", "SOL", "RUIZ CARLOS", student_dni="60000004", relative_dni="20000004", afip=self.afip_name)
        ]
        self._run(rows)
        parent = self._imported("parent").filtered(lambda p: p.vat == "20000004")
        self.assertEqual(parent.l10n_ar_afip_responsibility_type_id, self.afip_type)

    def test_paying_role_without_afip_raises(self):
        if not self.afip_type:
            self.skipTest("l10n_ar localization not installed")
        rows = [
            _row("LOPEZ", "MATEO", "LOPEZ ANA", roles="Responsable de Facturación", relative_dni="20000007"),
        ]
        with self.assertRaises(UserError):
            self._run(rows)
        self.assertFalse(self._imported("family", "Familia LOPEZ"))

    def test_same_surname_different_relatives_split_families(self):
        rows = [
            _row("AGUERO", "JOAQUIN", "AMARD JOSE LUIS", student_dni="58120334", relative_dni="27890123"),
            _row("AGUERO", "FRANCISCA", "MIRANDA YESICA", student_dni="59230445", relative_dni="30112233"),
        ]
        self._run(rows)

        families = self._imported("family", "Familia AGUERO")
        self.assertEqual(len(families), 2)
        for family in families:
            self.assertEqual(len(family.student_ids), 1)
            self.assertEqual(len(family.student_link_ids), 1)

        self._run(rows)
        self.assertEqual(len(self._imported("family", "Familia AGUERO")), 2)

    def test_same_surname_different_relatives_without_dni_split_families(self):
        rows = [
            _row("AGUERO", "JOAQUIN", "AMARD JOSE LUIS"),
            _row("AGUERO", "FRANCISCA", "MIRANDA YESICA"),
        ]
        self._run(rows)
        self.assertEqual(len(self._imported("family", "Familia AGUERO")), 2)

    def test_same_student_several_relatives_shares_family(self):
        rows = [
            _row("PAZ", "LEON", "PAZ HECTOR", student_dni="58000111", relative_dni="27000111"),
            _row("PAZ", "LEON", "DIAZ LAURA", student_dni="58000111", relative_dni="28000222"),
        ]
        self._run(rows)

        families = self._imported("family", "Familia PAZ")
        self.assertEqual(len(families), 1)
        self.assertEqual(len(families.student_ids), 1)
        self.assertEqual(len(families.student_link_ids), 2)

    def test_same_student_several_relatives_without_dni_shares_family(self):
        rows = [
            _row("PAZ", "LEON", "PAZ HECTOR"),
            _row("PAZ", "LEON", "DIAZ LAURA"),
        ]
        self._run(rows)

        families = self._imported("family", "Familia PAZ")
        self.assertEqual(len(families), 1)
        self.assertEqual(len(families.student_ids), 1)
        self.assertEqual(len(families.student_link_ids), 2)

    def test_links_by_student_groups_family_and_links_students(self):
        rows = [
            _row(
                "BENITEZ",
                "TOMAS",
                "BENITEZ RAUL",
                student_dni="55440022",
                relative_dni="24556677",
                links_by_student="Sí",
            ),
            _row(
                "BENITEZ",
                "CAMILA",
                "SOSA MARIANA",
                student_dni="56550133",
                relative_dni="26778899",
                links_by_student="Sí",
            ),
        ]
        self._run(rows)

        family = self._imported("family", "Familia BENITEZ")
        self.assertEqual(len(family), 1)
        self.assertTrue(family.links_by_student)
        self.assertEqual(len(family.student_ids), 2)
        self.assertFalse(family.student_link_ids)

        tomas = family.student_ids.filtered(lambda s: s.identification_number == "55440022")
        camila = family.student_ids.filtered(lambda s: s.identification_number == "56550133")
        self.assertEqual(tomas.student_link_ids.partner_id.name, "BENITEZ RAUL")
        self.assertEqual(camila.student_link_ids.partner_id.name, "SOSA MARIANA")

    def test_invalid_links_by_student_raises(self):
        rows = [_row("VEGA", "IVAN", "VEGA JUAN", student_dni="60000005", links_by_student="Tal vez")]
        with self.assertRaises(UserError):
            self._run(rows)
        self.assertFalse(self._imported("family", "Familia VEGA"))

    def test_unknown_trailing_column_is_ignored(self):
        """A spreadsheet carrying its own extra column must not be read as the flag."""
        header = HEADER[:-1] + ["OBSERVACIONES"]
        rows = [_row("SOTO", "NICOLAS", "SOTO ANDRES", student_dni="60000006", links_by_student="Repite curso")]
        self._run(rows, header=header)

        family = self._imported("family", "Familia SOTO")
        self.assertEqual(len(family), 1)
        self.assertFalse(family.links_by_student)

    def test_reimport_is_idempotent(self):
        rows = _reference_rows(self.afip_name)
        self._run(rows)
        c1 = self.Partner.search_count([("partner_type", "in", ("family", "student", "parent"))])
        self._run(rows)
        c2 = self.Partner.search_count([("partner_type", "in", ("family", "student", "parent"))])
        self.assertEqual(c1, c2)
