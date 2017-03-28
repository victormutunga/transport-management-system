# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _, osv
from openerp.exceptions import Warning
from datetime import timedelta, datetime
import calendar
import json
from openerp.tools import config
from openerp.tools.misc import xlwt


class TMSReportContextCommon(models.TransientModel):
    _name = "tms.report.context.common"
    _description = "A particular context for a financial report"

    date_from = fields.Date("Start date")
    date_to = fields.Date("End date")
    date_filter = fields.Char('Date filter used', default=None)

    @api.model
    def get_context_by_report_name(self, name):
        return self.env[self._report_name_to_report_context()[name]]

    @api.model
    def get_context_name_by_report_name_json(self):
        return json.dumps(self._report_name_to_report_context())

    @api.model
    def get_context_name_by_report_model_json(self):
        return json.dumps(self._report_model_to_report_context())

    def _report_name_to_report_model(self):
        return {
            'manager_ledger': 'tms.manager.ledger',
        }

    def _report_model_to_report_context(self):
        return {
            'tms.manager.ledger': 'tms.context.manager.ledger',
        }

    def _report_name_to_report_context(self):
        return dict([(k[0], self._report_model_to_report_context()[k[1]]) for k in self._report_name_to_report_model().items()])

    @api.model
    def get_full_report_name_by_report_name(self, name):
        return self._report_name_to_report_model()[name]

    def get_report_obj(self):
        raise Warning(_('get_report_obj not implemented'))

    @api.multi
    def remove_line(self, line_id):
        self.write({self.fold_field: [(3, line_id)]})

    @api.multi
    def add_line(self, line_id):
        self.write({self.fold_field: [(4, line_id)]})

    @api.multi
    def set_next_number(self, num):
        self.write({'next_footnote_number': num})
        return

    def get_columns_names(self):
        raise Warning(_('get_columns_names not implemented'))

    def get_full_date_names(self, dt_to, dt_from=None):
        convert_date = self.env['ir.qweb.field.date'].value_to_html
        date_to = convert_date(dt_to, None)
        dt_to = datetime.strptime(dt_to, "%Y-%m-%d")
        if dt_from:
            date_from = convert_date(dt_from, None)
        if 'month' in self.date_filter:
            return '%s %s' % (self._get_month(dt_to.month - 1), dt_to.year)
        if 'quarter' in self.date_filter:
            month_start = self.env.user.company_id.fiscalyear_last_month + 1
            month = dt_to.month if dt_to.month >= month_start else dt_to.month + 12
            quarter = int((month - month_start) / 3) + 1
            return dt_to.strftime(_('Quarter #') + str(quarter) + ' %Y')
        if 'year' in self.date_filter:
            if self.env.user.company_id.fiscalyear_last_day == 31 and self.env.user.company_id.fiscalyear_last_month == 12:
                return dt_to.strftime('%Y')
            else:
                return str(dt_to.year - 1) + ' - ' + str(dt_to.year)
        if not dt_from:
            return _('(As of %s)') % (date_to,)
        return _('(From %s <br/> to  %s)') % (date_from, date_to)

    def _get_month(self, index):
        return [
            _('January'), _('February'), _('March'), _('April'), _('May'), _('June'),
            _('July'), _('August'), _('September'), _('October'), _('November'), _('December')
        ][index]

    def get_cmp_date(self):
        if self.get_report_obj().get_report_type() == 'no_date_range':
            return self.get_full_date_names(self.date_to_cmp)
        return self.get_full_date_names(self.date_to_cmp, self.date_from_cmp)

    @api.model
    def create(self, vals):
        res = super(TMSReportContextCommon, self).create(vals)
        report_type = res.get_report_obj().get_report_type()
        if report_type in ['date_range', 'date_range_cash', 'no_comparison']:
            dt = datetime.today()
            update = {
                'date_from': datetime.today().replace(day=1),
                'date_to': dt.replace(day=calendar.monthrange(dt.year, dt.month)[1]),
                'date_filter': 'this_month',
            }
        res.write(update)
        return res

    def get_xml(self):
        return self.env['account.financial.html.report.xml.export'].do_xml_export(self)

    def get_pdf(self):
        if not config['test_enable']:
            self = self.with_context(commit_assetsbundle=True)

        report_obj = self.get_report_obj()
        lines = report_obj.with_context(print_mode=True).get_lines(self)
        base_url = self.env['ir.config_parameter'].sudo().get_param('report.url') or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        rcontext = {
            'mode': 'print',
            'base_url': base_url,
            'company': self.env.user.company_id,
        }

        body = self.pool['ir.ui.view'].render(
            self._cr, self._uid, "report_general_travel.main_tms_general_report_letter",
            values=dict(rcontext, lines=lines, report=report_obj, context=self),
            context=self.env.context
        )

        header = self.pool['report'].render(
            self._cr, self._uid, [], "report.internal_layout",
            values=rcontext,
            context=self.env.context
        )
        header = self.pool['report'].render(
            self._cr, self._uid, [], "report.minimal_layout",
            values=dict(rcontext, subst=True, body=header),
            context=self.env.context
        )

        landscape = False
        if len(self.get_columns_names()) > 4:
            landscape = True

        return self.env['report']._run_wkhtmltopdf([header], [''], [(0, body)], landscape, self.env.user.company_id.paperformat_id, spec_paperformat_args={'data-report-margin-top': 10, 'data-report-header-spacing': 10})

    @api.multi
    def get_html_and_data(self, given_context=None):
        if given_context is None:
            given_context = {}
        result = {}
        if given_context:
            update = {}
            for field in given_context:
                if field.startswith('add_'):
                    update[field[4:]] = [(4, int(given_context[field]))]
                if field.startswith('remove_'):
                    update[field[7:]] = [(3, int(given_context[field]))]
                if self._fields.get(field) and given_context[field] != 'undefined':
                    if given_context[field] == 'false':
                        given_context[field] = False
                    if given_context[field] == 'none':
                        given_context[field] = None
                    if field == 'company_ids': #  Needs to be treated differently as it's a many2many
                        update[field] = [(6, 0, given_context[field])]
                    else:
                        update[field] = given_context[field]

            self.write(update)
        lines = self.get_report_obj().get_lines(self)
        rcontext = {
            'res_company': self.env['res.users'].browse(self.env.uid).company_id,
            'context': self,
            'report': self.get_report_obj(),
            'lines': lines,
            'mode': 'display',
        }
        result['html'] = self.env['ir.model.data'].xmlid_to_object(self.get_report_obj().get_template()).render(rcontext)
        result['report_type'] = self.get_report_obj().get_report_type()
        select = ['id', 'date_filter', 'date_from', 'date_to']
        result['report_context'] = self.read(select)[0]
        return result

    def get_xls(self, response):
        book = xlwt.Workbook()
        report_id = self.get_report_obj()
        sheet = book.add_sheet(report_id.get_title())

        title_style = xlwt.easyxf(
            'font: bold true; borders: bottom medium;',
            num_format_str='#,##0.00')
        level_0_style = xlwt.easyxf('font: bold true; borders: bottom medium, top medium; pattern: pattern solid, fore-colour grey25;', num_format_str='#,##0.00')
        level_0_style_left = xlwt.easyxf('font: bold true; borders: bottom medium, top medium, left medium; pattern: pattern solid, fore-colour grey25;', num_format_str='#,##0.00')
        level_0_style_right = xlwt.easyxf('font: bold true; borders: bottom medium, top medium, right medium; pattern: pattern solid, fore-colour grey25;', num_format_str='#,##0.00')
        level_1_style = xlwt.easyxf('font: bold true; borders: bottom medium, top medium;', num_format_str='#,##0.00')
        level_1_style_left = xlwt.easyxf('font: bold true; borders: bottom medium, top medium, left medium;', num_format_str='#,##0.00')
        level_1_style_right = xlwt.easyxf('font: bold true; borders: bottom medium, top medium, right medium;', num_format_str='#,##0.00')
        level_2_style = xlwt.easyxf('font: bold true; borders: top medium;', num_format_str='#,##0.00')
        level_2_style_left = xlwt.easyxf('font: bold true; borders: top medium, left medium;', num_format_str='#,##0.00')
        level_2_style_right = xlwt.easyxf('font: bold true; borders: top medium, right medium;', num_format_str='#,##0.00')
        level_3_style = xlwt.easyxf(num_format_str='#,##0.00')
        level_3_style_left = xlwt.easyxf('borders: left medium;', num_format_str='#,##0.00')
        level_3_style_right = xlwt.easyxf('borders: right medium;', num_format_str='#,##0.00')
        domain_style = xlwt.easyxf('font: italic true;', num_format_str='#,##0.00')
        domain_style_left = xlwt.easyxf('font: italic true; borders: left medium;', num_format_str='#,##0.00')
        domain_style_right = xlwt.easyxf('font: italic true; borders: right medium;', num_format_str='#,##0.00')
        upper_line_style = xlwt.easyxf('borders: top medium;', num_format_str='#,##0.00')
        def_style = xlwt.easyxf(num_format_str='#,##0.00')

        sheet.col(0).width = 10000

        sheet.write(0, 0, '', title_style)

        x = 1
        for column in self.with_context(is_xls=True).get_columns_names():
            sheet.write(0, x, column, title_style)
            x += 1

        y_offset = 1
        lines = report_id.with_context(no_format=True, print_mode=True).get_lines(self)

        for y in range(0, len(lines)):
            if lines[y].get('level') == 0 and lines[y].get('type') == 'line':
                for x in range(0, len(lines[y]['columns']) + 1):
                    sheet.write(y + y_offset, x, None, upper_line_style)
                y_offset += 1
                style_left = level_0_style_left
                style_right = level_0_style_right
                style = level_0_style
            elif lines[y].get('level') == 1 and lines[y].get('type') == 'line':
                for x in range(0, len(lines[y]['columns']) + 1):
                    sheet.write(y + y_offset, x, None, upper_line_style)
                y_offset += 1
                style_left = level_1_style_left
                style_right = level_1_style_right
                style = level_1_style
            elif lines[y].get('level') == 2:
                style_left = level_2_style_left
                style_right = level_2_style_right
                style = level_2_style
            elif lines[y].get('level') == 3:
                style_left = level_3_style_left
                style_right = level_3_style_right
                style = level_3_style
            elif lines[y].get('type') != 'line':
                style_left = domain_style_left
                style_right = domain_style_right
                style = domain_style
            else:
                style = def_style
                style_left = def_style
                style_right = def_style
            sheet.write(y + y_offset, 0, lines[y]['name'], style_left)
            for x in xrange(1, len(lines[y]['columns']) + 1):
                if isinstance(lines[y]['columns'][x - 1], tuple):
                    lines[y]['columns'][x - 1] = lines[y]['columns'][x - 1][0]
                if x < len(lines[y]['columns']):
                    sheet.write(y + y_offset, x, lines[y]['columns'][x - 1], style)
                else:
                    sheet.write(y + y_offset, x, lines[y]['columns'][x - 1], style_right)
            if lines[y]['type'] == 'total' or lines[y].get('level') == 0:
                for x in xrange(0, len(lines[0]['columns']) + 1):
                    sheet.write(y + 1 + y_offset, x, None, upper_line_style)
                y_offset += 1
        if lines:
            for x in xrange(0, len(lines[0]['columns']) + 1):
                sheet.write(len(lines) + y_offset, x, None, upper_line_style)

        book.save(response.stream)

    # Tries to find the corresponding context (model name and id) and creates it if none is found.
    @api.model
    def return_context(self, report_model, given_context, report_id=None):
        context_model = self._report_model_to_report_context()[report_model]
        # Fetch the context_id or create one if none exist.
        # Look for a context with create_uid = current user (and with possibly a report_id)
        domain = [('create_uid', '=', self.env.user.id)]
        if report_id:
            domain.append(('report_id', '=', int(report_id)))
        context = False
        if not context:
            create_vals = {}
            if report_id:
                create_vals['report_id'] = report_id
            context = self.env[context_model].create(create_vals)
        if 'force_account' in given_context:
            context.unfolded_accounts = [(6, 0, [given_context['active_id']])]
        return [context_model, context.id]
