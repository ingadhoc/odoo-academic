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
    section_id = fields.Many2one(
        "academic.section",
        string="Section",
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
    dni = fields.Char(
        "DNI",
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
    # company_type = fields.Selection(selection_add=[('family', 'Family')])
    # is_family = fields.Boolean()
    same_dni_partner_id = fields.Many2one(
        "res.partner",
        string="Partner with same DNI",
        compute="_compute_same_dni_partner_id",
        store=False,
        search="_search_same_dni_partner_id",
    )
    same_dni_partner_company = fields.Many2one(
        "res.company", string="Company same partner", related="same_dni_partner_id.company_id"
    )
    current_main_group_id = fields.Many2one("academic.group", compute="_compute_current_main_group", store=True)
    category_id = fields.Many2many(check_company=True)
    student_count = fields.Integer(compute="_compute_student_count", store=True)

    # @api.depends('is_family')
    # def _compute_company_type(self):
    #     families = self.filtered(lambda x: x.is_company and x.is_family)
    #     families.company_type = 'family'
    #     return super(ResPartner, self - families)._compute_company_type()

    # def _write_company_type(self):
    #     families = self.filtered(lambda x: x.company_type == 'family')
    #     families.is_company = True
    #     families.is_family = True
    #     return super(ResPartner, self - families)._write_company_type()

    @api.constrains("company_id", "partner_type", "parent_id")
    def _check_family_configured(self):
        if self.filtered(
            lambda x: x.partner_type == "student"
            and x.company_id.family_required
            and x.parent_id.partner_type != "family"
        ):
            raise UserError("En la institucion, los estudiantes deben estar vinculados a una familia")

    @api.constrains("parent_id", "partner_type")
    def _check_family_student_relation(self):
        if self.filtered(lambda x: x.partner_type != "student" and x.parent_id.partner_type == "family"):
            raise UserError("Los contactos de una familia solo pueden ser estudiantes")

    def _compute_related_user_id(self):
        for rec in self:
            rec.related_user_id = rec.user_ids and rec.user_ids[0]

    @api.depends("is_company")
    def _compute_partner_type(self):
        self.filtered(lambda x: x.is_company and x.partner_type).partner_type = False

    def quickly_create_portal_user(self):
        """Metodo que crea o activa usuario inactivo en el grupo portal que
        se defina
        """
        # TODO: el metodo onchange_portal_id no existe.
        # Esto dejo de usarse pero queda el codigo por posible implementacion a futuro
        raise UserError(_("Esta función se encuentra en desarrollo!"))

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

    @api.depends("dni")
    def _compute_same_dni_partner_id(self):
        filtered_partners = self.filtered("dni")
        for partner in filtered_partners:
            partner_id = partner._origin.id
            Partner = self.with_context(active_test=False).sudo()
            domain = [
                ("dni", "=", partner.dni),
            ]
            if partner_id:
                domain += [("id", "!=", partner_id)]
            partner.same_dni_partner_id = Partner.search(domain, limit=1)
        (self - filtered_partners).same_dni_partner_id = False

    def _search_same_dni_partner_id(self, operator, value):
        return [("dni", operator, value)]

    @api.constrains("current_main_group_id")
    def _check_unique_main_group_per_year(self):
        """La validación se realiza sobre el campo `current_main_group_id` en lugar de `student_group_ids`
        porque, al usar un campo many2many, la validación no se activaba al agregar un estudiante
        directamente desde un grupo.
        """
        for partner in self:
            domain = [("student_ids", "=", partner.id), ("subject_id", "=", False)]
            grouped_data = self.env["academic.group"].read_group(domain, ["year"], ["year"])
            duplicate_years = [group["year"] for group in grouped_data if group["year_count"] > 1]
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

    @api.depends("student_link_ids", "student_link_ids.role_ids")
    def _compute_payment_responsible(self):
        for rec in self.filtered(lambda x: x.partner_type == "student"):
            partners = rec.student_link_ids.filtered(
                lambda x: self.env.ref("academic.paying_role") in x.role_ids
            ).mapped("partner_id")
            rec.payment_responsible_ids = [(6, 0, partners.ids)]

    @api.constrains("student_link_ids")
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

    @api.constrains("partner_type")
    def _check_groups_student(self):
        if self.env.context.get("install_mode"):
            return True
        if self.filtered(lambda x: x.partner_type == "student" and not x.student_group_ids):
            raise UserError(_("The student must belong to at least one academic group."))
