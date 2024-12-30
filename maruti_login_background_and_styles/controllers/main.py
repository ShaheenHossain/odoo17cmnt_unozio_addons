# -*- encoding: utf-8 -*-

import logging
import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from werkzeug.urls import url_encode, iri_to_uri
import odoo
import odoo.modules.registry
from odoo.tools.translate import _
from odoo import http, tools
from odoo.http import content_disposition, dispatch_rpc, request, Response

_logger = logging.getLogger(__name__)


db_monodb = http.db_list(force=True)


def _get_login_redirect_url(uid, redirect=None):
    if request.session.uid:  # fully logged
        return redirect or '/web'

    url = request.env(user=uid)['res.users'].browse(uid)._mfa_url()
    if not redirect:
        return url

    parsed = werkzeug.urls.url_parse(url)
    qs = parsed.decode_query()
    qs['redirect'] = redirect
    return parsed.replace(query=werkzeug.urls.url_encode(qs)).to_url()


def abort_and_redirect(url):
    r = request.httprequest
    response = werkzeug.utils.redirect(url, 302)
    response = r.app.get_response(r, response, explicit_session=False)
    werkzeug.exceptions.abort(response)


# override
def ensure_db(redirect='/web/database/selector'):
    db = request.params.get('db') and request.params.get('db').strip()

    if db and db not in http.db_filter([db]):
        db = None

    if db and not request.session.db:
        r = request.httprequest
        url_redirect = werkzeug.urls.url_parse(r.base_url)
        if r.query_string:
            query_string = iri_to_uri(r.query_string)
            url_redirect = url_redirect.replace(query=query_string)
        request.session.db = db
        abort_and_redirect(url_redirect)

    # if db not provided, use the session one
    if not db and request.session.db and http.db_filter([request.session.db]):
        db = request.session.db

    if not db:
        db = db_monodb(request.httprequest)

    if not db:
        werkzeug.exceptions.abort(werkzeug.utils.redirect(redirect, 303))

    if db != request.session.db:
        request.session.logout()
        abort_and_redirect(request.httprequest.url)

    request.session.db = db

class Home(http.Controller):

    def _login_redirect(self, uid, redirect=None):
        return _get_login_redirect_url(uid, redirect)

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                uid = request.session.authenticate(request.session.db, request.params['login'],
                                                   request.params['password'])
                request.params['login_success'] = True
                return request.redirect(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        param_obj = request.env['ir.config_parameter'].sudo()
        values['reset_password_enabled'] = param_obj.get_param('auth_signup.reset_password')
        values['signup_enabled'] = param_obj.get_param('auth_signup.invitation_scope') == 'b2c'
        values['disable_footer'] = param_obj.get_param('disable_footer')
        style = param_obj.get_param('login_background.style')
        background = param_obj.get_param('login_background.background')
        values['background_color'] = param_obj.get_param('login_background.color')
        background_image = param_obj.get_param('login_background.background_image')

        if background == 'image':
            image_url = ''
            if background_image:
                base_url = param_obj.get_param('web.base.url')
                image_url = base_url + '/web/image?' + 'model=login.image&id=' + background_image + '&field=image'
                values['background_src'] = image_url or ''
                values['background_color'] = ''

        if background == 'color':
            values['background_src'] = ''

        if style == 'default' or style is False:
            response = request.render('web.login', values)
        elif style == 'left':
            response = request.render('maruti_login_background_and_styles.left_login_template', values)
        elif style == 'right':
            response = request.render('maruti_login_background_and_styles.right_login_template', values)
        else:
            response = request.render('maruti_login_background_and_styles.middle_login_template', values)

        response.headers['X-Frame-Options'] = 'DENY'
        return response


class Website(Home):

    @http.route(website=True, auth="public", sitemap=False)
    def web_login(self, *args, **kw):
        return super().web_login(*args, **kw)