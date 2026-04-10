##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"
    _check_company_auto = True
    _check_company_domain = models.check_company_domain_parent_of

    parent_id = fields.Many2one(check_company=True)
    partner_type = fields.Selection(
        [
            ("student", "Student"),
            ("teacher", "Teacher"),
            ("administrator", "Administrator"),
            ("gral_administrator", "General Administrator"),
            ("parent", "Relative"),
            ("other", "Other"),
            ("family", "Family"),
        ],
        change_default=True,
        string="Tipo de Contacto Académico",
        compute="_compute_partner_type",
        readonly=False,
        store=True,
    )
    promotion_id = fields.Many2one(
        "academic.promotion",
        string="Promotion",
    )
    teacher_group_ids = fields.One2many(
        "academic.group",
        "teacher_id",
        string="Teacher Groups",
    )
    student_group_ids = fields.Many2many(
        "academic.group",
        "academic_student_group_ids_student_ids_rel",
        "partner_id",
        "group_id",
        string="Student Groups",
        context={"active_test": False},
    )
    disabled_person = fields.Boolean("Disabled Person?", help="¿Alumno/a con Dificultades de aprendizaje?")
    sex = fields.Selection(
        [("M", "Male"), ("F", "Female")],
    )
    file_number = fields.Char(
        copy=False,
    )
    birthdate = fields.Date(
        copy=False,
    )
    admission_date = fields.Date()
    exit_date = fields.Date()
    medical_insurance = fields.Char(
        copy=False,
    )
    identification_number = fields.Char(
        string="Academic Identification Number",
        compute="_compute_identification_number",
        store=True,
        readonly=False,
    )
    same_identification_number_partner_id = fields.Many2one(
        "res.partner",
        string="Partner with same identification number",
        compute="_compute_same_identification_number_partner_id",
        store=False,
        search="_search_same_identification_number_partner_id",
    )
    same_identification_number_partner_company = fields.Many2one(
        "res.company",
        string="Company same partner",
        compute="_compute_same_identification_number_partner_id",
        store=False,
    )
    same_identification_number_company_email = fields.Char(
        string="Company email same identification number partner",
        compute="_compute_same_identification_number_partner_id",
        store=False,
    )
    same_vat_company_email = fields.Char(
        string="Company email same VAT partner",
        compute="_compute_same_vat_partner_id",
        store=False,
    )
    same_vat_partner_company_id = fields.Many2one(
        "res.company",
        string="Company same VAT partner",
        compute="_compute_same_vat_partner_id",
        store=False,
    )
    related_user_id = fields.Many2one(
        "res.users",
        compute="_compute_related_user_id",
    )
    student_link_ids = fields.One2many(
        "res.partner.link",
        "student_id",
        string="Contactos y Roles",
        copy=True,
        compute="_compute_student_links",
        readonly=False,
        store=True,
        recursive=True,
    )
    payment_responsible_ids = fields.Many2many(
        "res.partner",
        "payment_responsible_ids_student_id_rel",
        "partner_id",
        "student_id",
        compute="_compute_payment_responsible",
        store=True,
    )
    self_payment_responsible = fields.Boolean(
        help="Check if the student is an adult and responsible for their own payment",
        default=False,
    )
    parent_id = fields.Many2one(context={"default_partner_type": "family"})

    @api.depends("parent_links_by_student", "parent_id.student_link_ids")
    def _compute_student_links(self):
        """Si se confirugan los contactos en la flia, los propagamos a los hijos. Lo hacemos así para que:
        a) en todo el codigo solo miremos siempre hijos, lo de la familia es un asistente
        b) si se marca llevar en estudiantes ya van a tener toda la data que tenía la familia"""
        for rec in self.filtered(
            lambda x: x.partner_type == "student" and x.parent_id and not x.parent_links_by_student
        ):
            commands = []
            for link in rec.parent_id.student_link_ids:
                existing_link = rec.student_link_ids.filtered(lambda l: l.partner_id == link.partner_id)
                if existing_link:
                    existing_link.write(
                        {
                            "relationship_id": link.relationship_id.id,
                            "note": link.note,
                            "role_ids": [(6, 0, link.role_ids.ids)],
                            "sequence": link.sequence,
                        }
                    )
                else:
                    commands.append(
                        (
                            0,
                            0,
                            {
                                "partner_id": link.partner_id.id,
                                "relationship_id": link.relationship_id.id,
                                "note": link.note,
                                "role_ids": [(6, 0, link.role_ids.ids)],
                                "sequence": link.sequence,
                            },
                        )
                    )
            parent_partner_ids = rec.parent_id.student_link_ids.mapped("partner_id")
            obsolete_links = rec.student_link_ids.filtered(lambda l: l.partner_id not in parent_partner_ids)
            commands += [(2, link.id) for link in obsolete_links]
            if commands:
                rec.student_link_ids = commands

    partner_link_ids = fields.One2many("res.partner.link", "partner_id", string="Roles", copy=True)
    links_by_student = fields.Boolean(string="Contactos y Roles por Estudiante")
    company_family_required = fields.Boolean(related="company_id.family_required")
    parent_links_by_student = fields.Boolean(
        related="parent_id.links_by_student", string="La familia define Contactos y Roles por Estudiante"
    )
    # creamos nuevo campo porque el child_ids como ya esta en la vista nos propaga el mode kanban
    # al hacerlo con mode tree nos simplfica bastante la herencia de vista porque no tenemos que agregar en el quick
    # create tantas cosas
    student_ids = fields.One2many("res.partner", "parent_id")
    company_id = fields.Many2one(compute="_compute_company_id", store=True, readonly=False)
    current_main_group_id = fields.Many2one("academic.group", compute="_compute_current_main_group", store=True)
    category_id = fields.Many2many(check_company=True)
    student_count = fields.Integer(compute="_compute_student_count", store=True)

    @api.constrains("company_id", "partner_type", "parent_id", "self_payment_responsible")
    def _check_family_configured(self):
        if self.filtered(
            lambda x: (
                x.partner_type == "student"
                and x.company_id.family_required
                and x.parent_id.partner_type != "family"
                and not x.self_payment_responsible
                and not self.env.context.get("skip_family_check")
            )
        ):
            raise UserError(self.env._("Students must be linked to a family at this institution"))

        if self.filtered(
            lambda x: (
                x.partner_type == "student"
                and x.self_payment_responsible
                and x.parent_id
                and x.parent_id.partner_type == "family"
            )
        ):
            raise UserError(
                self.env._("A student cannot be self payment responsible and belong to a family at the same time")
            )

    @api.constrains("parent_id", "partner_type")
    def _check_family_student_relation(self):
        if self.filtered(lambda x: x.partner_type != "student" and x.parent_id.partner_type == "family"):
            raise UserError(self.env._("Family contacts can only be students"))

    def _compute_related_user_id(self):
        for rec in self:
            rec.related_user_id = rec.user_ids and rec.user_ids[0]

    @api.depends("self_payment_responsible", "vat")
    def _compute_identification_number(self):
        for rec in self:
            if rec.self_payment_responsible and not rec.parent_id and rec.vat:
                rec.identification_number = rec.vat

    @api.depends("is_company")
    def _compute_partner_type(self):
        self.filtered(lambda x: x.is_company and x.partner_type).partner_type = False

    @api.depends("parent_id")
    def _compute_company_id(self):
        """
        Si soy parte de una compañía (o familia, es campo "parent_id"), queremos que todos los childs tengan misma company
        Ahora bien, si la compañía está compartida (parent_id = False) matenemos fleixibilidad con los hijos.
        Por defecto ponemos la company donde está parado el usuario pero permitimos sacarla o cambiarla.
        Un padre, madre o estudiante podrían en algunos casos de uso estar compartidos entre varias instituciones
        """
        if self.env.context.get("install_mode"):
            # salimos del método porque no queremos que se modifique el comportamiento nativo de odoo al momento de
            # instalar ya que puede afectar registros demo de otros módulos (ejemplo: que se cree un registro
            # de account.move para una compañía y dicho registro tiene un parter que pertenece a otra entonces
            # tendríamos error de instalación de registros demo.
            return
        for rec in self:
            rec.company_id = rec.parent_id.company_id or rec.env.company

    def _onchange_company_id(self):
        # anulamos el onchange nativo de odoo porque ahora lo hicimos compute
        return

    def _compute_same_vat_partner_id(self):
        super()._compute_same_vat_partner_id()
        # The base method only searches within the same company. For any partner
        # that still has no match, widen the search to all companies.
        Partner = self.env["res.partner"].with_context(active_test=False).sudo()
        for partner in self.filtered(
            lambda p: not p.same_vat_partner_id and p.vat and len(p.vat) != 1 and not p.parent_id
        ):
            partner_id = partner._origin.id
            domain = [("vat", "=", partner.vat)]
            if partner_id:
                domain += [("id", "!=", partner_id), "!", ("id", "child_of", partner_id)]
            partner.same_vat_partner_id = Partner.search(domain, limit=1)
        for partner in self:
            same_vat_partner = partner.same_vat_partner_id.sudo()
            partner.same_vat_partner_company_id = same_vat_partner.company_id
            partner.same_vat_company_email = same_vat_partner.company_id.email or "-"

    @api.depends("identification_number")
    def _compute_same_identification_number_partner_id(self):
        Partner = self.env["res.partner"].with_context(active_test=False).sudo()
        for partner in self:
            same_identification_partner = Partner.browse()
            if partner.identification_number:
                partner_id = partner._origin.id
                domain = [
                    ("identification_number", "=", partner.identification_number),
                ]
                if partner_id:
                    domain += [("id", "!=", partner_id)]
                same_identification_partner = Partner.search(domain, limit=1)
            partner.same_identification_number_partner_id = same_identification_partner
            same_identification_partner = same_identification_partner.sudo()
            partner.same_identification_number_partner_company = same_identification_partner.company_id
            partner.same_identification_number_company_email = same_identification_partner.company_id.email or "-"

    def _search_same_identification_number_partner_id(self, operator, value):
        return [("identification_number", operator, value)]

    @api.constrains("current_main_group_id")
    def _check_unique_main_group_per_year(self):
        """La validación se realiza sobre el campo `current_main_group_id` en lugar de `student_group_ids`
        porque, al usar un campo many2many, la validación no se activaba al agregar un estudiante
        directamente desde un grupo.
        """
        current_year = date.today().year
        for partner in self:
            domain = [("student_ids", "=", partner.id), ("subject_id", "=", False), ("year", ">=", current_year)]
            grouped_data = self.env["academic.group"]._read_group(domain, ["year"], ["__count"])
            duplicate_years = [year for year, count in grouped_data if count > 1]
            if duplicate_years:
                raise ValidationError(
                    _(
                        "The partner '%s' cannot belong to multiple groups "
                        "without a subject in the same year. Conflicting year(s): %s."
                    )
                    % (partner.name, ", ".join(map(str, duplicate_years)))
                )

    @api.depends("student_group_ids")
    def _compute_current_main_group(self):
        for rec in self:
            student_group = rec.student_group_ids.filtered(lambda g: g.year == date.today().year and not g.subject_id)
            rec.current_main_group_id = student_group[:1]

    @api.depends("student_link_ids", "student_link_ids.role_ids", "self_payment_responsible")
    def _compute_payment_responsible(self):
        students = self.filtered(lambda x: x.partner_type == "student")
        for rec in students:
            partners = rec.student_link_ids.filtered(
                lambda x: self.env.ref("academic.paying_role") in x.role_ids
            ).mapped("partner_id")
            if rec.self_payment_responsible:
                partners |= rec
            rec.payment_responsible_ids = [(6, 0, partners.ids)]
        (self - students).payment_responsible_ids = False

    @api.constrains("student_link_ids", "self_payment_responsible", "vat")
    def _check_vat_partner_paying_role(self):
        paying_role = self.env.ref("academic.paying_role")
        partners = self.student_link_ids.filtered(
            lambda x: x.partner_id and paying_role in x.role_ids and not x.partner_id.vat
        )
        if partners:
            partner_names = "\n".join(partners.mapped("partner_id.name"))
            raise UserError(
                _("The payer must have an identification number set up. The following do not meet this condition: \n%s")
                % partner_names
            )

        if self.filtered(lambda x: x.self_payment_responsible and not x.vat):
            raise UserError(
                _("The student must have a tax identification number configured to be their own payment responsible.")
            )

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        if self.env.context.get("from_open_student_view"):
            limit = self.env["res.partner"].search_count(domain)
        return super().web_search_read(
            domain, specification, offset=offset, limit=limit, order=order, count_limit=count_limit
        )

    @api.depends("student_ids")
    def _compute_student_count(self):
        for rec in self.filtered(lambda x: x.partner_type == "family"):
            rec.student_count = len(rec.student_ids)
