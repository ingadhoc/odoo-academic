from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request


class CustomerPortal(CustomerPortal):
    @http.route(["/my/personal_data"], type="http", auth="user", website=True)
    def portal_my_personal_data(self, **kw):
        user = request.env.user
        employee = request.env["hr.employee"].search(
            [("user_id", "=", user.id), ("main_employee_id", "=", False)], limit=1
        )

        if not employee:
            return request.redirect("/my")

        values = {
            "employee": employee,
            "page_name": "personal_data",
            "countries": request.env["res.country"].search([]),
            "states": request.env["res.country.state"].search([]),
        }

        if kw.get("error"):
            values["error_message"] = "There was an error updating your information. Please try again."

        if kw.get("success"):
            values["success_message"] = "Your personal data has been updated successfully."

        return request.render("academic_hr.portal_my_personal_data", values)

    @http.route(["/my/personal_data/update"], type="http", auth="user", website=True, methods=["POST"])
    def portal_update_personal_data(self, **kw):
        user = request.env.user
        employee = request.env["hr.employee"].search(
            [("user_id", "=", user.id), ("main_employee_id", "=", False)], limit=1
        )

        if not employee:
            return request.redirect("/my")

        try:
            state_id = int(kw.get("state_id")) if kw.get("state_id") else False
        except (ValueError, TypeError):
            state_id = False

        try:
            country_id = int(kw.get("country_id")) if kw.get("country_id") else False
        except (ValueError, TypeError):
            country_id = False

        employee_vals = {
            "private_phone": kw.get("phone") or False,
            "private_email": kw.get("email") or False,
            "private_street": kw.get("street") or False,
            "private_city": kw.get("city") or False,
            "private_zip": kw.get("zip") or False,
            "private_state_id": state_id,
            "private_country_id": country_id,
        }

        try:
            employee.write(employee_vals)
        except Exception:
            return request.redirect("/my/personal_data?error=1")

        return request.redirect("/my/personal_data?success=1")
