##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AcademicGroup(models.Model):
    _inherit = "academic.group"

    fee_so_line_ids = fields.One2many(
        "sale.order.line",
        "group_id",
        string="Main SO Line",
        domain=[("product_id.academic_product_type", "=", "fee")],
    )
    registration_so_line_ids = fields.One2many(
        "sale.order.line",
        "group_id",
        string="Registration SO Line",
        domain=[("product_id.academic_product_type", "=", "registration")],
    )
    opportunities_ids = fields.One2many(
        "crm.lead",
        "group_id",
        string="Opportunities",
    )
    fee_student_count = fields.Integer(compute="_compute_fee_student_count")
    no_fee_student_count = fields.Integer(compute="_compute_no_fee_student_count")
    registration_student_count = fields.Integer(compute="_compute_registration_student_count")
    opportunities_student_count = fields.Integer(compute="_compute_opportunities_student_count")
    vacancies = fields.Integer(compute="_compute_vacancies", store=True)
    manage_sale_workflow = fields.Boolean(compute="_compute_manage_sale_workflow", store=True, readonly=False)
    student_ids = fields.Many2many(
        compute="_compute_student_ids",
        store=True,
        readonly=False,
    )

    # TODO mejorar todos estos compute, read group? podemos simplificar calculos? query?
    def _compute_no_fee_student_count(self):
        for group in self:
            group.no_fee_student_count = len(
                group.student_ids
                - group.fee_so_line_ids.filtered(
                    lambda x: x.order_id.state == "sale" and x.order_id.subscription_state != "6_churn"
                ).mapped("order_id.partner_id")
            )

    def _compute_registration_student_count(self):
        # TODO tal vez deberiamos hacer una constraint que no pueda permitir dos lineas de venta "activas" para mismo academic_product_type, student y grupo
        # luego el mapped no seria necesario
        for group in self:
            group.registration_student_count = len(
                group.registration_so_line_ids.filtered(lambda x: x.state in ["draft", "sent"]).mapped(
                    "order_id.partner_id"
                )
            )

    def _compute_opportunities_student_count(self):
        for group in self:
            group.opportunities_student_count = len(
                group.opportunities_ids.filtered(
                    lambda x: x.active
                    and x.partner_id
                    not in group.registration_so_line_ids.mapped("order_id.partner_id")
                    | group.fee_so_line_ids.mapped("order_id.partner_id")
                )
            )

    def _compute_fee_student_count(self):
        for group in self:
            group.fee_student_count = len(
                group.fee_so_line_ids.filtered(
                    lambda x: x.order_id.state == "sale" and x.order_id.subscription_state != "6_churn"
                ).mapped("order_id.partner_id")
            )

    @api.depends("student_ids")
    def _compute_vacancies(self):
        for group in self:
            group.vacancies = group.capacity - len(group.student_ids)

    @api.constrains("vacancies")
    def _check_vacancies(self):
        if self.filtered(lambda x: x.vacancies < 0):
            raise ValidationError(_("There can be no negative vacancies. Increase group capacity."))

    def open_opportunities(self):
        action = self.env["ir.actions.actions"]._for_xml_id("crm.crm_lead_action_pipeline")
        action.update(
            {
                "domain": [("group_id", "=", self.id)],
                "context": {},
            }
        )
        return action

    def open_registration_sales(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action.update({"domain": [("id", "in", self.registration_so_line_ids.mapped("order_id").ids)], "context": {}})
        return action

    def open_no_fee_students(self):
        action = self.env.ref("academic.action_academic_partner_students").read()[0]
        action.update(
            {
                "domain": [
                    (
                        "id",
                        "in",
                        (
                            self.student_ids
                            - self.fee_so_line_ids.filtered(
                                lambda x: x.order_id.state == "sale" and x.order_id.subscription_state != "6_churn"
                            ).mapped("order_id.partner_id")
                        ).ids,
                    )
                ],
                "views": [(False, "list"), (False, "form")],
                "context": {"from_open_student_view": True},
            }
        )
        return action

    @api.depends(
        "manage_sale_workflow",
        "registration_so_line_ids",
        "registration_so_line_ids.state",
        "registration_so_line_ids.order_id.close_reason_id",
    )
    def _compute_student_ids(self):
        for group in self.filtered("manage_sale_workflow"):
            # Suscripciones (estudiantes) de matrícula confirmadas Y que estén en progreso o finalizada que no libere vacantes
            group.student_ids = group.registration_so_line_ids.filtered(
                lambda x: x.order_id.state == "sale"
                and (
                    x.order_id.subscription_state != "6_churn"
                    or (
                        x.order_id.subscription_state == "6_churn"
                        and x.order_id.close_reason_id
                        and not x.order_id.close_reason_id.release_vacancy
                    )
                )
            ).mapped("order_id.partner_id")

    @api.constrains("capacity")
    def _check_capacity(self):
        if self.filtered(lambda x: x.capacity <= 0):
            raise ValidationError(self.env._("The capacity must be greater than 0."))

    @api.depends("subject_id")
    def _compute_manage_sale_workflow(self):
        groups_with_subject = self.filtered("subject_id")
        groups_with_subject.manage_sale_workflow = False
        (self - groups_with_subject).manage_sale_workflow = True

    def open_order_wizard(self):
        action = self.env.ref("academic_sale_subscription.action_view_academic_order_wizard").read()[0]
        action.update({"context": {"default_student_ids": self.student_ids.ids}})
        return action

    def open_fee_sales(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action.update(
            {
                "domain": [("id", "in", self.fee_so_line_ids.mapped("order_id").ids)],
                "context": {},
            }
        )
        return action
