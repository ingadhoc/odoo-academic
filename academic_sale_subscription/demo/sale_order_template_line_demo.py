from odoo import api, models


class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"

    @api.model
    def _init_academic_template_lines(self):
        template_primaria = self.env.ref("academic_sale_subscription.subscription_template_primaria")
        template_secundaria = self.env.ref("academic_sale_subscription.subscription_template_secundaria")
        template_universidad = self.env.ref("academic_sale_subscription.subscription_template_universidad")
        template_ingles = self.env.ref("academic_sale_subscription.subscription_template_ingles")

        product_cuota_primaria = self.env.ref("academic_sale_subscription.product_cuota_primaria").product_variant_id
        product_inscripcion_primaria = self.env.ref(
            "academic_sale_subscription.product_inscripcion_primaria"
        ).product_variant_id
        product_cuota_secundaria = self.env.ref(
            "academic_sale_subscription.product_cuota_secundaria"
        ).product_variant_id
        product_inscripcion_secundaria = self.env.ref(
            "academic_sale_subscription.product_inscripcion_secundaria"
        ).product_variant_id
        product_cuota_universidad = self.env.ref(
            "academic_sale_subscription.product_cuota_universidad"
        ).product_variant_id
        product_inscripcion_universidad = self.env.ref(
            "academic_sale_subscription.product_inscripcion_universidad"
        ).product_variant_id
        product_cuota_ingles = self.env.ref("academic_sale_subscription.product_cuota_ingles").product_variant_id
        product_inscripcion_ingles = self.env.ref(
            "academic_sale_subscription.product_inscripcion_ingles"
        ).product_variant_id

        uom_unit = self.env.ref("uom.product_uom_unit")

        self.env["sale.order.template.line"].create(
            {
                "sale_order_template_id": template_primaria.id,
                "display_type": "line_section",
                "name": "📚 EDUCACIÓN PRIMARIA",
                "sequence": 1,
            }
        )
        self.env["sale.order.template.line"].create(
            {
                "sale_order_template_id": template_primaria.id,
                "product_id": product_cuota_primaria.id,
                "product_uom_qty": 1,
                "product_uom_id": uom_unit.id,
                "sequence": 2,
            }
        )
        self.env["sale.order.template.line"].create(
            {
                "sale_order_template_id": template_primaria.id,
                "product_id": product_inscripcion_primaria.id,
                "product_uom_qty": 1,
                "product_uom_id": uom_unit.id,
                "sequence": 3,
            }
        )

        self.env["sale.order.template.line"].create(
            {
                "sale_order_template_id": template_secundaria.id,
                "display_type": "line_section",
                "name": "🎓 EDUCACIÓN SECUNDARIA",
                "sequence": 1,
            }
        )
        self.env["sale.order.template.line"].create(
            {
                "sale_order_template_id": template_secundaria.id,
                "product_id": product_cuota_secundaria.id,
                "product_uom_qty": 1,
                "product_uom_id": uom_unit.id,
                "sequence": 2,
            }
        )
        self.env["sale.order.template.line"].create(
            {
                "sale_order_template_id": template_secundaria.id,
                "product_id": product_inscripcion_secundaria.id,
                "product_uom_qty": 1,
                "product_uom_id": uom_unit.id,
                "sequence": 3,
            }
        )

        self.env["sale.order.template.line"].create(
            {
                "sale_order_template_id": template_universidad.id,
                "display_type": "line_section",
                "name": "🏛️ EDUCACIÓN UNIVERSITARIA",
                "sequence": 1,
            }
        )
        self.env["sale.order.template.line"].create(
            {
                "sale_order_template_id": template_universidad.id,
                "product_id": product_cuota_universidad.id,
                "product_uom_qty": 1,
                "product_uom_id": uom_unit.id,
                "sequence": 2,
            }
        )
        self.env["sale.order.template.line"].create(
            {
                "sale_order_template_id": template_universidad.id,
                "product_id": product_inscripcion_universidad.id,
                "product_uom_qty": 1,
                "product_uom_id": uom_unit.id,
                "sequence": 3,
            }
        )

        self.env["sale.order.template.line"].create(
            {
                "sale_order_template_id": template_ingles.id,
                "display_type": "line_section",
                "name": "🇺🇸 CURSOS DE INGLÉS",
                "sequence": 1,
            }
        )
        self.env["sale.order.template.line"].create(
            {
                "sale_order_template_id": template_ingles.id,
                "product_id": product_cuota_ingles.id,
                "product_uom_qty": 1,
                "product_uom_id": uom_unit.id,
                "sequence": 2,
            }
        )
        self.env["sale.order.template.line"].create(
            {
                "sale_order_template_id": template_ingles.id,
                "product_id": product_inscripcion_ingles.id,
                "product_uom_qty": 1,
                "product_uom_id": uom_unit.id,
                "sequence": 3,
            }
        )
