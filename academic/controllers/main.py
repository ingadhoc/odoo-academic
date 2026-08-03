##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import io

import xlsxwriter
from odoo import http
from odoo.exceptions import AccessError
from odoo.http import content_disposition, request
from xlsxwriter.utility import xl_col_to_name

from ..wizards.academic_contact_import import AFIP_FIELD, ALLOWED_RELATIONS

FILENAME = "contactos_academicos_ejemplo.xlsx"

LAST_VALIDATION_ROW = 500


class AcademicContactImportController(http.Controller):
    @http.route("/academic/contact_import/example", type="http", auth="user")
    def download_example(self, **kwargs):
        if not request.env.user.has_group("academic.group_manager"):
            raise AccessError(request.env._("Only Academic managers can download the import example."))

        Partner = request.env["res.partner"]
        afip_available = AFIP_FIELD in Partner._fields and "l10n_ar.afip.responsibility.type" in request.env
        role_values = request.env["res.partner.role"].search([]).mapped("name")
        afip_values = (
            request.env["l10n_ar.afip.responsibility.type"].search([]).mapped("name") if afip_available else []
        )

        columns = [
            {
                "header": "APELLIDO",
                "width": 14,
                "example": "Suárez",
                "help": "Apellido de la familia. Los alumnos que comparten apellido y responsable se agrupan "
                "en la misma familia.",
            },
            {
                "header": "NOMBRE ALUMNO",
                "width": 16,
                "example": "Simón",
                "help": "Nombre del alumno (sin apellido). Cargá una fila por cada alumno y responsable.",
            },
            {
                "header": "DNI ALUMNO",
                "width": 12,
                "example": "45123456",
                "help": "DNI del alumno (opcional). Se usa para no duplicar alumnos al reimportar.",
            },
            {
                "header": "ETIQUETAS",
                "width": 24,
                "example": "",
                "help": "Una o más etiquetas separadas por coma. Deben existir previamente en el sistema o la "
                "importación falla.",
            },
            {
                "header": "RESPONSABLE",
                "width": 20,
                "example": "Roxana Correa",
                "help": "Nombre del familiar/responsable del alumno.",
            },
            {
                "header": "RELACIÓN",
                "width": 16,
                "example": "Padre/Madre",
                "dropdown": "relation",
                "help": "Vínculo del responsable con el alumno. Elegí un valor de la lista desplegable.",
            },
            {
                "header": "ROLES",
                "width": 30,
                "example": "Responsable de Facturación",
                "dropdown": "roles",
                "help": "Uno o más roles existentes. Elegí de la lista o escribí varios separados por coma "
                "(ej.: Responsable de Facturación, Puede Retirar). El Responsable de Facturación exige DNI del "
                "responsable y, con la localización argentina instalada, también su tipo de responsabilidad "
                "AFIP: si falta alguno, la importación falla.",
            },
            {
                "header": "DNI RESPONSABLE",
                "width": 16,
                "example": "27333444",
                "help": "DNI del responsable. Obligatorio para el Responsable de Facturación; opcional para el resto "
                "de los parientes. Se usa para deduplicar familias y responsables al reimportar.",
            },
        ]
        if afip_available:
            columns.append(
                {
                    "header": "TIPO RESPONSABILIDAD AFIP",
                    "width": 28,
                    "example": "",
                    "dropdown": "afip",
                    "help": "Solo disponible con la localización argentina instalada. Elegí un valor de la lista "
                    "desplegable. Obligatorio para el Responsable de Facturación; opcional para el resto de los "
                    "parientes.",
                }
            )
        columns += [
            {
                "header": "EMAIL",
                "width": 24,
                "example": "roxana@example.com",
                "help": "Email del responsable (opcional).",
            },
            {
                "header": "TELÉFONO",
                "width": 18,
                "example": "+54 9 11 5555-5555",
                "help": "Teléfono del responsable (opcional).",
            },
            {
                "header": "CONTACTOS Y ROLES POR ESTUDIANTE",
                "width": 32,
                "example": "No",
                "dropdown": "yesno",
                "help": "Opcional (Sí/No, vacío = No). Poné Sí cuando alumnos que comparten apellido son una misma "
                "familia pero cada uno tiene sus propios contactos y roles.",
            },
        ]

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})

        sheet = workbook.add_worksheet("Contactos")
        lists = workbook.add_worksheet("Listas")

        header_fmt = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#D9E1F2",
                "border": 1,
                "text_wrap": True,
                "valign": "top",
                "align": "center",
            }
        )
        example_fmt = workbook.add_format({"italic": True, "font_color": "#808080", "bg_color": "#F2F2F2", "border": 1})

        sources = {"relation": list(ALLOWED_RELATIONS), "roles": role_values, "yesno": ["Sí", "No"]}
        if afip_available:
            sources["afip"] = afip_values
        source_ref = {}
        list_col = 0
        for key, values in sources.items():
            if not values:
                continue
            for row, name in enumerate(values):
                lists.write(row, list_col, name)
            letter = xl_col_to_name(list_col)
            source_ref[key] = "=Listas!$%s$1:$%s$%d" % (letter, letter, len(values))
            list_col += 1
        lists.hide()

        for col, spec in enumerate(columns):
            sheet.set_column(col, col, spec["width"])
            sheet.write(0, col, spec["header"], header_fmt)
            sheet.write_comment(0, col, spec["help"], {"x_scale": 2.5, "y_scale": 1.5})
            sheet.write(1, col, spec["example"], example_fmt)
            dropdown = spec.get("dropdown")
            if dropdown and dropdown in source_ref:
                options = {"validate": "list", "source": source_ref[dropdown]}
                if dropdown == "roles":
                    options["show_error"] = False
                sheet.data_validation(1, col, LAST_VALIDATION_ROW, col, options)

        sheet.write_comment(1, 0, "Fila de ejemplo — eliminá esta línea antes de importar.", {"color": "#FFC7CE"})
        sheet.freeze_panes(1, 0)

        workbook.close()
        output.seek(0)
        return request.make_response(
            output.read(),
            headers=[
                ("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                ("Content-Disposition", content_disposition(FILENAME)),
            ],
        )
