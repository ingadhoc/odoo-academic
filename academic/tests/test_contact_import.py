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
]
ROWS = [
    [
        "SUAREZ CORREA",
        "SIMON OSCAR",
        "48879185",
        "Beca 50%",
        "CORREA ROXANA",
        "Padre/Madre",
        "Responsable de Facturación, Puede Retirar",
        "20024910",
        "",
        "r@x.com",
        "1122334455",
    ],
    [
        "AMAYA",
        "LUCIA",
        "53761825",
        "Hermanos",
        "AVELLANEDA G",
        "Padre/Madre",
        "Responsable de Facturación",
        "30277377",
        "",
        "g@x.com",
        "",
    ],
    [
        "AMAYA",
        "RODRIGO",
        "50963724",
        "Hermanos",
        "AVELLANEDA G",
        "Padre/Madre",
        "Responsable de Facturación",
        "30277377",
        "",
        "g@x.com",
        "",
    ],
    ["AMERATTE", "MARTINA", "", "", "GESTO CARMEN", "Abuelo/a", "Responsable de Facturación", "", "", "c@x.com", ""],
]


def _build_csv(rows):
    buf = io.StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_ALL)
    writer.writerow(HEADER)
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

    def _run(self, rows):
        wizard = self.env["academic.contact.import"].create(
            {
                "file": _build_csv(rows),
                "filename": "test.csv",
            }
        )
        wizard.action_import()
        return wizard

    def test_import_creates_structure_and_dedups(self):
        self._run(ROWS)

        families = self.Partner.search([("partner_type", "=", "family")])
        self.assertEqual(len(families), 3)
        self.assertEqual(len(self.Partner.search([("partner_type", "=", "student")])), 4)

        amaya = families.filtered(lambda f: f.name == "Familia AMAYA")
        self.assertEqual(len(amaya.student_ids), 2)
        self.assertEqual(len(amaya.student_link_ids), 1)

        dnis = amaya.student_ids.mapped("identification_number")
        self.assertEqual(sorted(dnis), ["50963724", "53761825"])

        simon = self.Partner.search([("partner_type", "=", "student"), ("identification_number", "=", "48879185")])
        self.assertEqual(simon.name, "SUAREZ CORREA SIMON OSCAR")
        self.assertIn(self.tag_beca, simon.category_id)

        amaya_students = amaya.student_ids
        for student in amaya_students:
            self.assertIn(self.tag_hermanos, student.category_id)

        paying = self.env.ref("academic.paying_role")
        withdraw = self.env.ref("academic.withdraw_role")
        suarez = self.Partner.search([("partner_type", "=", "family"), ("name", "=", "Familia SUAREZ CORREA")])
        suarez_link = suarez.student_link_ids
        self.assertEqual(suarez_link.partner_id.name, "CORREA ROXANA")
        self.assertEqual(suarez_link.partner_id.vat, "20024910")
        self.assertEqual(suarez_link.partner_id.phone, "1122334455")
        self.assertIn(paying, suarez_link.role_ids)
        self.assertIn(withdraw, suarez_link.role_ids)

        ameratte = families.filtered(lambda f: f.name == "Familia AMERATTE")
        link = ameratte.student_link_ids
        self.assertEqual(link.relationship_id.name, "Abuelo/a")
        self.assertNotIn(paying, link.role_ids)

    def test_invalid_relationship_raises(self):
        rows = [["PEREZ", "JUAN", "60000001", "", "PEREZ MARIA", "MAMA", "", "20000001", "", "p@x.com", ""]]
        with self.assertRaises(UserError):
            self._run(rows)
        self.assertFalse(self.Partner.search([("partner_type", "=", "family"), ("name", "=", "PEREZ")]))

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
        self.assertFalse(self.Partner.search([("partner_type", "=", "family"), ("name", "=", "GOMEZ")]))

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
        self.assertFalse(self.Partner.search([("partner_type", "=", "family"), ("name", "=", "LOPEZ")]))

    def test_afip_responsibility_assigned(self):
        if "l10n_ar_afip_responsibility_type_id" not in self.Partner._fields:
            self.skipTest("l10n_ar localization not installed")
        afip_type = self.env["l10n_ar.afip.responsibility.type"].search([], limit=1)
        if not afip_type:
            self.skipTest("No AFIP responsibility types available")
        rows = [
            ["RUIZ", "SOL", "60000004", "", "RUIZ CARLOS", "Padre/Madre", "", "20000004", afip_type.name, "s@x.com", ""]
        ]
        self._run(rows)
        parent = self.Partner.search([("partner_type", "=", "parent"), ("vat", "=", "20000004")])
        self.assertEqual(parent.l10n_ar_afip_responsibility_type_id, afip_type)

    def test_reimport_is_idempotent(self):
        self._run(ROWS)
        c1 = self.Partner.search_count([("partner_type", "in", ("family", "student", "parent"))])
        self._run(ROWS)
        c2 = self.Partner.search_count([("partner_type", "in", ("family", "student", "parent"))])
        self.assertEqual(c1, c2)
