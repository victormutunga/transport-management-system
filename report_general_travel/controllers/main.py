# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import _serialize_exception
from openerp.tools import html_escape

import json


class ledgerReportController(http.Controller):
    @http.route(
        '/report_general_travel/<string:output_format>/'
        '<string:report_name>/<string:report_id>', type='http', auth='user')
    def report(self, output_format, report_name, token, report_id=None, **kw):
        uid = request.session.uid
        domain = [('create_uid', '=', uid)]
        report_model = request.env[
            'tms.report.context.common'].get_full_report_name_by_report_name(
                report_name)
        report_obj = request.env[report_model].sudo(uid)
        # if report_name == 'manager_ledger':
        #     report_id = int(report_id)
        #     domain.append(('report_id', '=', report_id))
        #     report_obj = report_obj.browse(report_id)
        context_obj = request.env[
            'tms.report.context.common'].get_context_by_report_name(
                report_name)
        context_id = context_obj.sudo(uid).search(domain, limit=1)
        try:
            if output_format == 'xls':
                response = request.make_response(
                    None,
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition', 'attachment; filename=' +
                            report_obj.get_name() + '.xls;')
                    ]
                )
                context_id.get_xls(response)
                response.set_cookie('fileToken', token)
                return response
            if output_format == 'pdf':
                response = request.make_response(
                    context_id.get_pdf(),
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', 'attachment; filename=' +
                            report_obj.get_name() + '.pdf;')
                    ]
                )
                response.set_cookie('fileToken', token)
                return response
            if output_format == 'xml':
                content = context_id.get_xml()
                response = request.make_response(
                    content,
                    headers=[
                        ('Content-Type', 'application/vnd.sun.xml.writer'),
                        ('Content-Disposition', 'attachment; filename=' +
                            report_obj.get_name() + '.xml;'),
                        ('Content-Length', len(content))
                    ]
                )
                response.set_cookie('fileToken', token)
                return response
        except IOError as i_o_error:
            ser_excep = _serialize_exception(i_o_error)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': ser_excep
            }
        except AttributeError as attr_error:
            ser_excep = _serialize_exception(attr_error)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': ser_excep
            }
        except OSError as op_sis_error:
            ser_excep = _serialize_exception(op_sis_error)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': ser_excep
            }
            return request.make_response(html_escape(json.dumps(error)))
        else:
            return request.not_found()
