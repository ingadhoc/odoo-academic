##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import base64
import re
import unicodedata

from odoo import fields, models
from odoo.exceptions import UserError

COL_SURNAME, COL_STUDENT, COL_STUDENT_DNI, COL_STUDENT_TAGS = 0, 1, 2, 3
COL_PARENT, COL_RELATION, COL_ROLES, COL_PARENT_DNI, COL_PARENT_AFIP, COL_EMAIL, COL_PHONE = 4, 5, 6, 7, 8, 9, 10

ALLOWED_RELATIONS = ["Padre/Madre", "Pariente", "Abuelo/a", "Otro"]

AFIP_FIELD = "l10n_ar_afip_responsibility_type_id"


def _norm(text):
    text = "".join(c for c in unicodedata.normalize("NFKD", str(text or "")) if not unicodedata.combining(c))
    return text.strip().lower()


class AcademicContactImport(models.TransientModel):
    _name = "academic.contact.import"
    _description = "Import Academic Contacts"

    file = fields.Binary(string="Spreadsheet", required=True)
    filename = fields.Char()
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        domain=lambda self: [("id", "in", self.env.companies.ids)],
        required=True,
    )
    state = fields.Selection([("draft", "Draft"), ("done", "Done")], default="draft")
    result_html = fields.Html(readonly=True)

    def _clean_dni(self, value):
        if value is None or str(value).strip() == "":
            return ""
        return re.sub(r"\D", "", str(value).split(".")[0])

    def _cell(self, row, idx):
        value = row[idx] if idx < len(row) else None
        return "" if value is None else str(value).strip()

    def _get_relationship(self, raw):
        canonical = {r.casefold(): r for r in ALLOWED_RELATIONS}.get((raw or "").strip().casefold())
        if not canonical:
            return self.env["res.partner.relationship"]
        Rel = self.env["res.partner.relationship"]
        return Rel.search([("name", "=", canonical)], limit=1) or Rel.create({"name": canonical})

    def _resolve_by_name(self, model, raw, extra_domain=None):
        records = self.env[model].browse()
        invalid = []
        for name in [n.strip() for n in re.split(r"[;,]", raw or "") if n.strip()]:
            record = self.env[model].search([("name", "=ilike", name)] + (extra_domain or []), limit=1)
            if record:
                records |= record
            else:
                invalid.append(name)
        return records, invalid

    def _get_roles(self, raw):
        return self._resolve_by_name("res.partner.role", raw)

    def _get_tags(self, raw):
        return self._resolve_by_name("res.partner.category", raw, [("company_id", "in", [False, self.company_id.id])])

    def _afip_field_available(self):
        return AFIP_FIELD in self.env["res.partner"]._fields

    def _get_afip_responsibility(self, raw):
        """Return (record, invalid_name). Empty cell → empty recordset, no error."""
        Afip = self.env["l10n_ar.afip.responsibility.type"]
        raw = (raw or "").strip()
        if not raw:
            return Afip.browse(), None
        record = Afip.search([("name", "=ilike", raw)], limit=1)
        return (record, None) if record else (Afip.browse(), raw)

    def _layout_error(self, extra=""):
        columns = self.env._(
            "Surname · Student name · Student DNI · Tags · Relative · Relationship · Roles · "
            "Relative DNI · AFIP responsibility type · Email · Phone"
        )
        return UserError(
            self.env._(
                "The spreadsheet does not match the expected layout.%(extra)s\n"
                "Expected columns, in order:\n%(columns)s\n\n"
                "Download the example file from the wizard and fill it in.",
                extra=("\n" + extra) if extra else "",
                columns=columns,
            )
        )

    def _read_rows(self):
        if not self.file:
            raise UserError(self.env._("Please upload a spreadsheet."))
        importer = self.env["base_import.import"].create(
            {
                "res_model": "res.partner",
                "file": base64.b64decode(self.file),
                "file_name": self.filename or "import.xlsx",
                "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
        )
        try:
            _length, rows = importer._read_file({"quoting": '"'})
        except UserError:
            raise
        except Exception as exc:
            raise UserError(self.env._("Could not read the file. Upload a valid .xlsx/.ods/.csv spreadsheet.\n%s", exc))
        finally:
            importer.sudo().unlink()

        if not rows:
            raise UserError(self.env._("The file is empty."))

        header_idx = None
        for idx, row in enumerate(rows[:10]):
            if row and "apellido" in _norm(row[0]):
                header_idx = idx
                break
        if header_idx is None:
            raise self._layout_error()

        self._check_columns(rows[header_idx])
        return rows[header_idx + 1 :]

    def _check_columns(self, header):
        def cell(idx):
            return _norm(header[idx]) if idx < len(header) else ""

        missing = []
        if "apellido" not in cell(COL_SURNAME):
            missing.append(self.env._("Surname"))
        if "nombre" not in cell(COL_STUDENT) and "alumno" not in cell(COL_STUDENT):
            missing.append(self.env._("Student name"))
        if not cell(COL_PARENT):
            missing.append(self.env._("Relative"))
        if "relacion" not in cell(COL_RELATION):
            missing.append(self.env._("Relationship"))
        if missing:
            raise self._layout_error(self.env._("Missing/misplaced columns: %s.") % ", ".join(missing))

    def _validate_vocabulary(self, data_rows):
        allowed = {r.casefold() for r in ALLOWED_RELATIONS}
        afip_available = self._afip_field_available()
        bad_relations, bad_roles, bad_tags, bad_afip = [], [], [], []
        for row in data_rows:
            student_name = self._cell(row, COL_STUDENT)
            if not student_name:
                continue
            _tags, invalid_tags = self._get_tags(self._cell(row, COL_STUDENT_TAGS))
            bad_tags += ["%s → %s" % (student_name, name) for name in invalid_tags]

            parent_name = self._cell(row, COL_PARENT)
            if not parent_name:
                continue
            value = self._cell(row, COL_RELATION)
            if value.casefold() not in allowed:
                bad_relations.append("%s → %s" % (student_name, value or self.env._("(empty)")))
            _roles, invalid = self._get_roles(self._cell(row, COL_ROLES))
            bad_roles += ["%s → %s" % (student_name, name) for name in invalid]
            if afip_available:
                _afip, invalid_afip = self._get_afip_responsibility(self._cell(row, COL_PARENT_AFIP))
                if invalid_afip:
                    bad_afip.append("%s → %s" % (student_name, invalid_afip))

        messages = []
        if bad_relations:
            messages.append(
                self.env._(
                    "The Relationship column must be exactly one of: %(allowed)s.\n"
                    "The following do not exist:\n%(detail)s",
                    allowed=", ".join(ALLOWED_RELATIONS),
                    detail="\n".join(bad_relations[:50]) + ("\n…" if len(bad_relations) > 50 else ""),
                )
            )
        if bad_roles:
            messages.append(
                self.env._(
                    "The following roles do not exist:\n%(detail)s",
                    detail="\n".join(bad_roles[:50]) + ("\n…" if len(bad_roles) > 50 else ""),
                )
            )
        if bad_tags:
            messages.append(
                self.env._(
                    "The following tags do not exist:\n%(detail)s",
                    detail="\n".join(bad_tags[:50]) + ("\n…" if len(bad_tags) > 50 else ""),
                )
            )
        if bad_afip:
            messages.append(
                self.env._(
                    "The following AFIP responsibility types do not exist:\n%(detail)s",
                    detail="\n".join(bad_afip[:50]) + ("\n…" if len(bad_afip) > 50 else ""),
                )
            )
        if messages:
            raise UserError("\n\n".join(messages))

    def action_import(self):
        self.ensure_one()
        data_rows = self._read_rows()
        self._validate_vocabulary(data_rows)
        Partner = self.env["res.partner"]
        paying_role = self.env.ref("academic.paying_role")
        company_id = self.company_id.id
        afip_available = self._afip_field_available()

        stats = {"rows": 0, "families_new": 0, "families_reused": 0, "students": 0, "parents": 0}
        no_dni, errors = [], []

        for line_no, row in enumerate(data_rows, start=1):
            student_name = self._cell(row, COL_STUDENT)
            if not student_name:
                continue
            stats["rows"] += 1
            try:
                surname = self._cell(row, COL_SURNAME)
                parent_name = self._cell(row, COL_PARENT)
                parent_dni = self._clean_dni(self._cell(row, COL_PARENT_DNI))
                family_name = "Familia %s" % surname if surname else student_name
                student_full_name = ("%s %s" % (surname, student_name)).strip()

                family = Partner._find_academic_family_by_parent_vats([parent_dni])
                reused = bool(family)
                if not family and surname:
                    family = Partner.search([("partner_type", "=", "family"), ("name", "=", family_name)], limit=1)
                    reused = bool(family)

                student_dni = self._clean_dni(self._cell(row, COL_STUDENT_DNI))
                if student_dni:
                    student = Partner.search(
                        [("partner_type", "=", "student"), ("identification_number", "=", student_dni)], limit=1
                    )
                else:
                    student = Partner.search(
                        [
                            ("partner_type", "=", "student"),
                            ("name", "=", student_full_name),
                            ("parent_id", "=", family.id if family else False),
                        ],
                        limit=1,
                    )

                tags, _invalid_tags = self._get_tags(self._cell(row, COL_STUDENT_TAGS))

                parent_vals_list = []
                if parent_name:
                    roles, _invalid = self._get_roles(self._cell(row, COL_ROLES))
                    if paying_role in roles and not parent_dni:
                        roles -= paying_role
                        no_dni.append("%s (%s)" % (parent_name, student_name))
                    if parent_dni:
                        existing_parent = Partner.search(
                            [("partner_type", "=", "parent"), ("vat", "=", parent_dni)], limit=1
                        )
                    else:
                        existing_parent = Partner.search(
                            [("partner_type", "=", "parent"), ("name", "=", parent_name)], limit=1
                        )
                    parent_vals = {
                        "name": parent_name,
                        "vat": parent_dni,
                        "email": self._cell(row, COL_EMAIL),
                        "phone": self._cell(row, COL_PHONE),
                        "relationship_id": self._get_relationship(self._cell(row, COL_RELATION)).id,
                        "role_ids": roles.ids,
                        "partner_id": existing_parent or None,
                    }
                    if afip_available:
                        afip, _invalid_afip = self._get_afip_responsibility(self._cell(row, COL_PARENT_AFIP))
                        if afip:
                            parent_vals[AFIP_FIELD] = afip.id
                    parent_vals_list.append(parent_vals)

                result = Partner._create_academic_structure(
                    family_vals={"name": family_name},
                    student_vals={
                        "name": student_full_name,
                        "identification_number": student_dni,
                        "category_id": tags.ids,
                    },
                    parent_vals_list=parent_vals_list,
                    company_id=company_id,
                    family=family or None,
                    student=student or None,
                )
                stats["families_new"] += result["created"]["family"]
                stats["families_reused"] += 1 if (reused and not result["created"]["family"]) else 0
                stats["students"] += result["created"]["student"]
                stats["parents"] += result["created"]["parents"]
            except Exception as exc:
                errors.append(self.env._("Row %(n)s (%(name)s): %(err)s", n=line_no, name=student_name, err=exc))

        self.state = "done"
        self.result_html = self._build_summary(stats, no_dni, errors)
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def _build_summary(self, stats, no_dni, errors):
        rows = [
            (self.env._("Rows processed"), stats["rows"]),
            (self.env._("Families created"), stats["families_new"]),
            (self.env._("Families reused"), stats["families_reused"]),
            (self.env._("Students created"), stats["students"]),
            (self.env._("Relatives created"), stats["parents"]),
        ]
        html = "<h4>%s</h4><ul>" % self.env._("Import finished")
        html += "".join("<li>%s: <b>%s</b></li>" % (label, value) for label, value in rows)
        html += "</ul>"
        if no_dni:
            html += "<div class='alert alert-warning'>%s (%s):<br/>%s</div>" % (
                self.env._("Paying role not assigned (relative has no DNI)"),
                len(no_dni),
                "<br/>".join(no_dni[:50]) + ("…" if len(no_dni) > 50 else ""),
            )
        if errors:
            html += "<div class='alert alert-danger'><b>%s (%s)</b><br/>%s</div>" % (
                self.env._("Rows with errors"),
                len(errors),
                "<br/>".join(str(e) for e in errors[:50]),
            )
        return html
