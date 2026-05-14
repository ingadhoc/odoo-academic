from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import content_disposition, request, route


class DebtCertificatePortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "debt_certificate_count" in counters:
            paying_role_id = request.env.ref("academic.paying_role").id
            student_links = (
                request.env["res.partner.link"]
                .sudo()
                .search(
                    [
                        ("partner_id", "=", request.env.user.partner_id.id),
                        ("role_ids", "in", [paying_role_id]),
                    ]
                )
            )
            values["debt_certificate_count"] = len(student_links)
        return values

    @route(["/my/debt_free_certificates"], type="http", auth="user", website=True)
    def portal_my_debt_free_certificates(self, **kwargs):
        values = self._prepare_portal_layout_values()

        # Get students for which the current user is payment responsible
        paying_role_id = request.env.ref("academic.paying_role").id
        student_links = (
            request.env["res.partner.link"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", request.env.user.partner_id.id),
                    ("role_ids", "in", [paying_role_id]),
                ]
            )
        )
        students = student_links.mapped("student_id").filtered(lambda s: s.partner_type == "student")

        values.update(
            {
                "students": students,
            }
        )

        return request.render("academic_sale_subscription.portal_my_debt_free_certificates", values)

    @route(["/my/debt_free_certificate/<int:student_id>"], type="http", auth="user", website=True)
    def download_debt_free_certificate(self, student_id, **kwargs):
        student = request.env["res.partner"].sudo().browse(student_id)

        # Verify that the user is the payment responsible for this student
        paying_role_id = request.env.ref("academic.paying_role").id
        student_links = (
            request.env["res.partner.link"]
            .sudo()
            .search(
                [
                    ("student_id", "=", student.id),
                    ("partner_id", "=", request.env.user.partner_id.id),
                    ("role_ids", "in", [paying_role_id]),
                ]
            )
        )

        if not student_links:
            return request.redirect("/my")

        # Check if student has pending debt
        if student._has_pending_debt():
            return request.render(
                "academic_sale_subscription.debt_certificate_unavailable",
                {
                    "student": student,
                },
            )

        # Generate and return the certificate using the report action
        report = request.env.ref("academic_sale_subscription.report_debt_free_certificate")
        pdf_content, report_format = report.sudo()._render(report.id, student.ids)

        filename = f"{report.name}.{report_format or 'pdf'}"

        pdfhttpheaders = [
            ("Content-Type", "application/pdf"),
            ("Content-Length", len(pdf_content)),
            ("Content-Disposition", content_disposition(filename)),
        ]
        return request.make_response(pdf_content, headers=pdfhttpheaders)
