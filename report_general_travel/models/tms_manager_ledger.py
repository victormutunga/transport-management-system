# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
from openerp.tools.misc import formatLang
from datetime import date, datetime, timedelta
import time
import pytz
from dateutil.rrule import rrule, MONTHLY

method_list = [
    'get_no_travels',
    'get_distance_real',
    'get_income',
    'get_expense_travel',
    'get_expense_mtto',
    'get_utility',
    'get_percentage_utility',
    'get_expense_fuel',
    'get_tires',
    'get_fuel',
    'get_efficienty_fuel',
    'get_expense_km',
    'get_income_km',
    'get_utility_km']


class tms_manager_ledger(models.AbstractModel):
    _name = "tms.manager.ledger"
    _description = "General Manager Report"

    def _format(self, value, currency=False):
        if self.env.context.get('no_format'):
            return value
        currency_id = currency or self.env.user.company_id.currency_id
        if currency_id.is_zero(value):
            value = abs(value)
        res = formatLang(self.env, value, currency_obj=currency_id)
        return res

    @api.model
    def get_lines(self, context_id, line_id=None):
        if type(context_id) == int:
            context_id = self.env['tms.manager.ledger'].search(
                [['id', '=', context_id]])
        new_context = dict(self.env.context)
        new_context.update({
            'date_from': context_id.date_from,
            'date_to': context_id.date_to,
        })
        return self.with_context(new_context)._lines(line_id)

    @api.model
    def _get_name_leve(self, index):
        return [
            _("Done Travels"), _("Kilometers Traveled"),
            _("Income"), _("Travel Expenses"),
            _("Maintenance Expenses"), _("Gross Profit"),
            _("Profit Percent"), _("Fuel Expenses"),
            _("Tire Installation"), _("Fuel Liters"),
            _("Fuel Performance"), _("Cost per Kilometer"),
            _("Income per Kilometer"), _("Utility per Kilometer"),
        ][index]

    @api.model
    def _prepare_level_lines(self, level):
        context = self.env.context
        unfold_all = context.get('print_mode') and not context[
            'context_id']['unfolded_accounts']
        date_from = datetime.strptime(context['date_from'], "%Y-%m-%d")
        date_to = datetime.strptime(context['date_to'], "%Y-%m-%d")
        dates = rrule(MONTHLY, dtstart=date_from).between(
            date_from, date_to, inc=True)
        comluns = []
        for date in dates:
            comluns.append(self.get_method_lines(level, date))
        return {
                'id': self.id,
                'name':  self._get_name_leve(level),
                'type': 'line',
                'footnotes':  {},
                'columns': comluns,
                'level': level + 3,
                'unfoldable': False,
                'unfolded': unfold_all,
                'colspan': 0,
            }

    @api.model
    def _lines(self, line_id=None):
        lines = []
        context = self.env.context
        unfold_all = context.get('print_mode') and not context[
            'context_id']['unfolded_accounts']
        for x in range(0, 14):
            lines.append(self._prepare_level_lines(x))
        return lines

    @api.model
    def get_title(self):
        return _("Management Report")

    @api.model
    def get_name(self):
        return 'manager_ledger'

    @api.model
    def get_report_type(self):
        return 'date_range'

    def get_template(self):
        return 'report_general_travel.main_tms_general_report'

    @api.multi
    def get_method_lines(self, level, date):
        return getattr(self, method_list[level])(date)


# _______METHODS FOR GET DATES OF TABLE_______
    @api.model
    def get_no_travels(self, date):
        obj_travel = self.env['tms.travel'].search([
                    ('state', '=', 'done')])
        tz = pytz.timezone(
            self.env.user.tz) if self.env.user.tz else pytz.utc
        travels = [
            travel for travel in obj_travel if
            pytz.utc.localize(travel.date).astimezone(tz).strptime(
                "%Y-%m-%d %H:%M:%S").month ==
            date.month and
            pytz.utc.localize(travel.date).astimezone(tz).strptime(
                "%Y-%m-%d %H:%M:%S").year == date.year]
        return len(travels)

    @api.model
    def get_distance_real(self, date):
        return "#distance"

    @api.model
    def get_income(self, date):
        return "ingresos"

    @api.model
    def get_expense_travel(self, date):
        return "gastos"

    @api.model
    def get_expense_mtto(self, date):
        return "gastos mtto"

    @api.model
    def get_utility(self, date):
        return "utilidad"

    @api.model
    def get_percentage_utility(self, date):
        return "porcentaje"

    @api.model
    def get_expense_fuel(self, date):
        return "gastos fuel"

    @api.model
    def get_tires(self, date):
        return "tires"

    @api.model
    def get_fuel(self, date):
        return "fuel"

    @api.model
    def get_efficienty_fuel(self, date):
        return "fuel dates"

    @api.model
    def get_expense_km(self, date):
        return "fuel dates"

    @api.model
    def get_income_km(self, date):
        return "fuel dates"

    @api.model
    def get_utility_km(self, date):
        return "fuel dates"
