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
COL_LINKS_BY_STUDENT = 11

ALLOWED_RELATIONS = ["Padre/Madre", "Pariente", "Abuelo/a", "Otro"]

TRUE_VALUES = {"si", "yes", "true", "verdadero", "1"}
FALSE_VALUES = {"", "no", "false", "falso", "0"}

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
        value = row[idx] if idx is not None and idx < len(row) else None
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

    def _get_links_by_student(self, raw):
        """Empty cell → False. Unknown values are rejected by _validate_vocabulary."""
        return _norm(raw) in TRUE_VALUES

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
            "Relative DNI · AFIP responsibility type · Email · Phone · Contacts and roles per student"
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
        return rows[header_idx + 1 :], self._parent_side_columns(rows[header_idx])

    def _parent_side_columns(self, header):
        norm = [_norm(c) for c in header]
        afip_present = COL_PARENT_AFIP < len(norm) and (
            "afip" in norm[COL_PARENT_AFIP] or "responsabilidad" in norm[COL_PARENT_AFIP]
        )
        email_col = COL_PARENT_AFIP + (1 if afip_present else 0)
        links_idx = email_col + 2
        links_col = (
            links_idx
            if links_idx < len(norm) and ("estudiante" in norm[links_idx] or "student" in norm[links_idx])
            else None
        )
        return {
            "afip": COL_PARENT_AFIP if afip_present else None,
            "email": email_col,
            "phone": email_col + 1,
            "links": links_col,
        }

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

    def _validate_vocabulary(self, data_rows, cols):
        allowed = {r.casefold() for r in ALLOWED_RELATIONS}
        afip_available = self._afip_field_available()
        paying_role = self.env.ref("academic.paying_role")
        bad_relations, bad_roles, bad_tags, bad_afip, bad_flags = [], [], [], [], []
        bad_paying, bad_paying_afip = [], []
        for row in data_rows:
            student_name = self._cell(row, COL_STUDENT)
            if not student_name:
                continue
            _tags, invalid_tags = self._get_tags(self._cell(row, COL_STUDENT_TAGS))
            bad_tags += ["%s → %s" % (student_name, name) for name in invalid_tags]

            flag = self._cell(row, cols["links"])
            if _norm(flag) not in TRUE_VALUES | FALSE_VALUES:
                bad_flags.append("%s → %s" % (student_name, flag))

            parent_name = self._cell(row, COL_PARENT)
            if not parent_name:
                continue
            value = self._cell(row, COL_RELATION)
            if value.casefold() not in allowed:
                bad_relations.append("%s → %s" % (student_name, value or self.env._("(empty)")))
            _roles, invalid = self._get_roles(self._cell(row, COL_ROLES))
            bad_roles += ["%s → %s" % (student_name, name) for name in invalid]
            if paying_role in _roles and not self._clean_dni(self._cell(row, COL_PARENT_DNI)):
                bad_paying.append("%s → %s" % (student_name, parent_name))
            if afip_available:
                afip, invalid_afip = self._get_afip_responsibility(self._cell(row, cols["afip"]))
                if invalid_afip:
                    bad_afip.append("%s → %s" % (student_name, invalid_afip))
                elif paying_role in _roles and not afip:
                    bad_paying_afip.append("%s → %s" % (student_name, parent_name))

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
        if bad_paying:
            messages.append(
                self.env._(
                    "The paying role (Responsable de Facturación) requires the relative's DNI.\n"
                    "The following have it without a DNI:\n%(detail)s",
                    detail="\n".join(bad_paying[:50]) + ("\n…" if len(bad_paying) > 50 else ""),
                )
            )
        if bad_paying_afip:
            messages.append(
                self.env._(
                    "The paying role (Responsable de Facturación) requires the relative's AFIP responsibility type.\n"
                    "Check that the AFIP responsibility type column is present and filled in for:\n%(detail)s",
                    detail="\n".join(bad_paying_afip[:50]) + ("\n…" if len(bad_paying_afip) > 50 else ""),
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
        if bad_flags:
            messages.append(
                self.env._(
                    "The Contacts and roles per student column only accepts Yes or No.\n"
                    "The following are not valid:\n%(detail)s",
                    detail="\n".join(bad_flags[:50]) + ("\n…" if len(bad_flags) > 50 else ""),
                )
            )
        if messages:
            raise UserError("\n\n".join(messages))

    def _find_family(self, student, family_name, parent_dni, parent_name, student_full_name, links_by_student):
        """Resolve the family a row belongs to, and the student when the row identifies one.

        The relative is the discriminator: two students sharing a surname but with different
        relatives belong to different families. Falling back to the family name alone is only
        safe when the row carries no relative, or when contacts are kept per student.
        """
        Partner = self.env["res.partner"]
        if student.parent_id.partner_type == "family":
            return student.parent_id, student

        family = Partner._find_academic_family_by_parent_vats([parent_dni])
        if family:
            return family, student

        # one indexed search feeds every remaining criterion; the rest is decided in memory
        namesakes = Partner.search([("partner_type", "=", "family"), ("name", "=", family_name)])
        for candidate in namesakes:
            if parent_name and any(
                _norm(link.partner_id.name) == _norm(parent_name) for link in candidate.student_link_ids
            ):
                return candidate, student
            # same student spread over several rows (one per relative) and no DNI to match on
            namesake_student = candidate.student_ids.filtered(lambda s: _norm(s.name) == _norm(student_full_name))
            if namesake_student:
                return candidate, namesake_student[:1]
        if links_by_student or not parent_name:
            return namesakes[:1], student
        return Partner.browse(), student

    def action_import(self):
        self.ensure_one()
        data_rows, cols = self._read_rows()
        self._validate_vocabulary(data_rows, cols)
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
                links_by_student = self._get_links_by_student(self._cell(row, cols["links"]))

                student_dni = self._clean_dni(self._cell(row, COL_STUDENT_DNI))
                student = Partner.browse()
                if student_dni:
                    student = Partner.search(
                        [("partner_type", "=", "student"), ("identification_number", "=", student_dni)], limit=1
                    )

                family, student = self._find_family(
                    student, family_name, parent_dni, parent_name, student_full_name, links_by_student
                )
                reused = bool(family)

                if not student:
                    if family:
                        student = family.student_ids.filtered(lambda s: _norm(s.name) == _norm(student_full_name))[:1]
                    else:
                        student = Partner.search(
                            [
                                ("partner_type", "=", "student"),
                                ("name", "=", student_full_name),
                                ("parent_id", "=", False),
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
                        "email": self._cell(row, cols["email"]),
                        "phone": self._cell(row, cols["phone"]),
                        "relationship_id": self._get_relationship(self._cell(row, COL_RELATION)).id,
                        "role_ids": roles.ids,
                        "partner_id": existing_parent or None,
                    }
                    if afip_available:
                        afip, _invalid_afip = self._get_afip_responsibility(self._cell(row, cols["afip"]))
                        if afip:
                            parent_vals[AFIP_FIELD] = afip.id
                    parent_vals_list.append(parent_vals)

                result = Partner._create_academic_structure(
                    family_vals={"name": family_name, "links_by_student": links_by_student},
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
