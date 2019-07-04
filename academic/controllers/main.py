from odoo import http
from odoo.http import request
from odoo.modules import get_resource_path
from odoo.addons.web.controllers.main import Binary
import base64
import functools
import imghdr
import io


class BinaryBackground(Binary):

    @http.route(
        ['/web_enterprise/custom-background'], type='http', auth="none",
        cors="*")
    def set_switch_image(self, dbname=None, **kw):
        imgname = 'application-switcher-bg'
        imgext = '.jpg'
        placeholder = functools.partial(
            get_resource_path, 'web_enterprise', 'static', 'src', 'img')
        company = request.env["res.company"].sudo().browse(1)
        background = company.background_image
        if background:
            image_base64 = base64.b64decode(background)
            image_data = io.BytesIO(image_base64)
            imgext = '.' + (imghdr.what(None, h=image_base64) or 'png')
            response = http.send_file(
                image_data, filename=imgname + imgext,
                mtime=company.write_date)
        else:
            response = http.send_file(placeholder(imgname + imgext))
        return response
