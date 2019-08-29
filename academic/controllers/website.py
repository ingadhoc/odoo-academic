from odoo import http
from odoo.addons.website.controllers.main import Website
from odoo.http import request
from werkzeug import url_encode


class Website(Website):

    @http.route()
    def web_login(self, redirect=None, *args, **kw):
        """ Por ahora hacemos que los students hagan redirect a backend, mas adelante deberiamos ver si hacemos
        algo mas lindo teniendo en cuenta que ofrecemos en backend/frontend
        Tal vez directamente le podemos agregar la opcion esta en frontend
        Como usamos website tenemos que modificar este metodo, si no podriamos modificar _login_redirect
        aprovechamos a redirigir tambien a los otros directivos y demas
        """
        response = super(Website, self).web_login(redirect=redirect, *args, **kw)
        if not redirect and request.params['login_success']:
            user = request.env['res.users'].browse(request.uid)
            if user.has_group('academic.group_portal_student'):
                # si es solo estudiante lo mandamos a evaluaciones
                if not user.has_group('academic.group_portal_teacher'):
                    url_params = {
                        'view_type': 'list',
                        'model': 'survey.user_input',
                        'menu_id': request.env.ref('academic.menu_my_evaluations').id,
                        'action': request.env.ref('academic.action_academic_user_input_my_evaluations').id,
                    }
                    redirect = '/web?#%s' % url_encode(url_params)
                else:
                    redirect = b'/web?' + request.httprequest.query_string
                return http.redirect_with_hash(redirect)
        return response
