# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from __future__ import division
from datetime import datetime

import base64
import calendar
import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)
try:
    from openpyxl import Workbook
    from openpyxl.writer.excel import save_virtual_workbook
    from openpyxl.styles import Font
except ImportError:
    _logger.debug('Cannot `import openpyxl`.')


class AccountGeneralLedgerWizard(models.TransientModel):
    _name = 'account.general.ledger.wizard'

    date_start = fields.Date(
        default=lambda self: self.get_month_start(),
        required=True,)
    date_end = fields.Date(
        default=lambda self: self.get_month_end(),
        required=True,)
    xlsx_file = fields.Binary()
    xlsx_filename = fields.Char()
    state = fields.Selection(
        [('get', 'Get'),
         ('print', 'Error')],
        default='get',)

    @api.model
    def get_month_start(self):
        today = datetime.now()
        month = today.month
        date_string = "%s-%s-01"
        if month < 10:
            date_string = "%s-0%s-01"
        month_start = date_string % (today.year, month)
        return month_start

    @api.model
    def get_month_end(self):
        today = datetime.now()
        month = today.month
        date_string = "%s-%s-%s"
        if month < 10:
            date_string = "%s-0%s-%s"
        month_end = date_string % (
            today.year, today.month, calendar.monthrange(
                today.year-1, month)[1])
        return month_end

    @api.model
    def get_initial_balances(self):
        self._cr.execute(
            """SELECT aa.code, SUM(aml.balance) AS balance
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE date < %s AND aa.user_type_id = 3
            GROUP BY aa.code""", (self.date_start, ))
        return self._cr.fetchall()

    @api.model
    def get_amls_info(self, report_type):
        self.ensure_one()
        # We get all the amls in the month range given by the user except
        # the income statement accounts
        if report_type == 'normal':
            self._cr.execute(
                """SELECT aml.id
                FROM account_move_line aml
                JOIN account_account aa ON aa.id = aml.account_id
                JOIN account_journal aj ON aj.id = aml.journal_id
                WHERE aml.date BETWEEN %s AND %s
                    AND aa.user_type_id NOT IN (13, 14, 15, 16, 17)
                    AND aj.type != %s
                ORDER BY aml.account_id""",
                (self.date_start, self.date_end, 'general'))
            amls = self._cr.fetchall()
        # We get all the amls in the month range given by the user of the
        # miscellanous journal entries
        else:
            expense_journals = self.env['operating.unit'].search([]).mapped(
                'expense_journal_id.id')
            self._cr.execute(
                """SELECT aml.id
                FROM account_move_line aml
                JOIN account_account aa ON aa.id = aml.account_id
                JOIN account_journal aj ON aj.id = aml.journal_id
                WHERE aml.date BETWEEN %s AND %s
                    AND aj.type = %s
                    AND aj.id NOT IN %s
                ORDER BY aml.account_id""",
                (self.date_start, self.date_end,
                 'general', tuple(expense_journals,),))
            amls = self._cr.fetchall()
        return amls

    @api.model
    def get_tms_expense_info(self, expense, aml):
        """Method to get the tms expense info"""
        items = []
        if (expense.amount_balance < 0.0 and expense.payment_move_id and not
                self._context.get('expense', False)):
            return items
        if aml and aml.account_id and not aml.account_id.reconcile:
            return items
        am_obj = self.env['account.move']
        lines = expense.move_id.line_ids
        paid_rate = 1
        if aml:
            # Get the payment rate
            paid_rate = round(
                (abs(aml.balance) * 100) / expense.amount_balance, 4) / 100
        # If the expense is not reconciled we reconcile it
        if aml and not aml.reconciled:
            line_to_reconcile = expense.move_id.line_ids.filtered(
                lambda x: x.account_id.reconcile and x.name == expense.name and
                not x.reconciled)
            if not line_to_reconcile:
                pass
            aml |= line_to_reconcile
            try:
                aml.reconcile()
            except Exception as e:
                raise ValidationError(
                    _(e.name + '\n' + 'TMS Expense: ' + expense.name))
        for line in lines:
            amount = 0.0
            # if the aml is not reconcile or is the root aml itpass directly
            if not line.account_id.reconcile or line.name == expense.name:
                amount = round(abs(line.balance) * paid_rate, 4)
                items.append(
                    [line.account_id.code, line.move_id.name,
                     line.name, line.ref, amount,
                     'debit' if line.debit > 0.0 else 'credit'])
                continue
            self._cr.execute(
                """
                SELECT CASE WHEN pr.debit_move_id = %s THEN
                    pr.credit_move_id ELSE pr.debit_move_id END AS inv_aml,
                    pr.amount, pr.amount_currency, currency_id
                FROM account_partial_reconcile pr
                WHERE pr.credit_move_id = %s OR pr.debit_move_id = %s""",
                (line.id, line.id, line.id,))
            partial = self._cr.dictfetchone()
            if not partial:
                amount = round(abs(line.balance) * paid_rate, 4)
                items.append(
                    [line.account_id.code, line.move_id.name,
                     line.name, line.ref, amount,
                     'debit' if line.debit > 0.0 else 'credit'])
                continue
            inv_lines = am_obj.search(
                [('line_ids', 'in', partial['inv_aml'])]).mapped('line_ids')
            for inv_line in inv_lines:
                amount = round(abs(inv_line.balance) * paid_rate, 4)
                items.append(
                    [inv_line.account_id.code, inv_line.move_id.name,
                     line.name, inv_line.ref, amount,
                     'debit' if line.debit > 0.0 else 'credit'])
        return items

    @api.model
    def get_cash_info(self, aml):
        """This method get the cash basis amounts based on the payments"""
        am_obj = self.env['account.move']
        aml_obj = self.env['account.move.line']
        items = []
        company_currency = aml.company_id.currency_id.id
        # This method search the aml linked to the invoice
        self._cr.execute(
            """
            SELECT CASE WHEN pr.debit_move_id = %s THEN
                pr.credit_move_id ELSE pr.debit_move_id END AS inv_aml,
                pr.amount, pr.amount_currency, currency_id
            FROM account_partial_reconcile pr
            WHERE pr.credit_move_id = %s OR pr.debit_move_id = %s""",
            (aml.id, aml.id, aml.id,))
        partials = self._cr.dictfetchall()
        expense = self.env['tms.expense'].search([
            ('name', '=', aml.name)])
        if not partials and not expense:
            return []
        # if the aml is of an expense is called a method to get the invoice
        # information
        if expense:
            return self.get_tms_expense_info(expense, aml)
        for partial in partials:
            # If the partial is in currency id but don't has amount currency is
            # not necessary the loop to avoid wrong moves in the report
            if ((partial['currency_id'] and partial['currency_id'] !=
                company_currency) and not
                    partial['amount_currency'] and partial['amount']):
                continue
            move = am_obj.search([('line_ids', 'in', partial['inv_aml'])])
            # Exchange currency
            if move.journal_id.id == 4:
                line = aml_obj.browse(partial['inv_aml'])
                items.append(
                    [line.account_id.code, line.move_id.name,
                     line.name, line.ref, round(abs(line.balance), 4),
                     'debit' if line.debit > 0.0 else 'credit'])
                continue
            # Normal case
            inv_aml = aml_obj.browse(partial['inv_aml'])
            inv_balance = abs(inv_aml.balance)
            partial_amount = partial['amount']
            # Case USD
            if partial['amount_currency'] and inv_aml.amount_currency:
                inv_balance = abs(inv_aml.amount_currency)
                partial_amount = partial['amount_currency']
            # Get the payment rate
            paid_rate = round(
                (partial_amount * 100) / inv_balance, 4) / 100
            # Get the income statement amls of the invoice
            lines = move.line_ids.filtered(
                lambda r: r.account_id.user_type_id.id in
                [13, 14, 15, 16, 17] and not r.tax_line_id)
            for line in lines:
                balance = abs(line.balance)
                if partial['amount_currency'] and inv_aml.amount_currency:
                    usd_currency = self.env.ref('base.USD').with_context(
                        date=aml.date)
                    mxn_currency = self.env.ref('base.MXN')
                    balance = usd_currency.compute(
                        abs(line.amount_currency), mxn_currency)
                    if aml.move_id.usd_currency_rate:
                        balance = (
                            abs(line.amount_currency) *
                            aml.move_id.usd_currency_rate)
                amount_untaxed = round(balance * paid_rate, 4)
                items.append(
                    [line.account_id.code, line.move_id.name,
                     line.name, line.ref, amount_untaxed,
                     'debit' if line.debit > 0.0 else 'credit'])
        return items

    @api.multi
    def prepare_data(self):
        """ This method prepare the report data into a dictionary ordered by
        the account code"""
        res = {}
        aml_obj = self.env['account.move.line']
        expense_obj = self.env['tms.expense']
        company_tax_journal = (
            self.env.user.company_id.tax_cash_basis_journal_id)
        initial_balances = self.get_initial_balances()
        for item in initial_balances:
            if item[0] not in res.keys():
                res[item[0]] = []
            res[item[0]].append({
                'C': _('Initial Balance'),
                'G': 0.0,
                'H': 0.0,
                'I': item[1],
            })
        # First get the amls without income statement accounts
        data = self.get_amls_info('normal')
        for aml in aml_obj.browse([x[0] for x in data]):
            # If the aml is of bank or cash is called the method to get the
            # cash basis info
            if (aml.journal_id.type in ['bank', 'cash'] or
                    aml.account_id.user_type_id.id == 3):
                aml_info = self.get_cash_info(aml)
                for item in aml_info:
                    # Set the results to the main dictionary
                    if item[0] not in res.keys():
                        res[item[0]] = []
                    res[item[0]].append({
                        'B': item[1],
                        'C': item[2],
                        'D': item[3],
                        'E': aml.date,
                        'F': aml.partner_id.name if aml.partner_id else '',
                        'G': item[4] if item[5] == 'debit' else 0.0,
                        'H': item[4] if item[5] == 'credit' else 0.0,
                    })
            # Set the aml to the main dictionary
            if aml.account_id.code not in res.keys():
                res[aml.account_id.code] = []
            res[aml.account_id.code].append({
                'B': aml.move_id.name,
                'C': aml.name,
                'D': aml.ref,
                'E': aml.date,
                'F': aml.partner_id.name if aml.partner_id else '',
                'G': aml.debit if aml.debit > 0.0 else 0.0,
                'H': aml.credit if aml.credit > 0.0 else 0.0,
            })
        # Finally get the amls of miscellanous journal entries
        data = self.get_amls_info('miscellanous')
        for aml in aml_obj.browse([x[0] for x in data]):
            # If the account is an income statement account and his journal is
            # the company tax cash basis journal the aml is not necessary
            if (aml.account_id.user_type_id.id in [13, 14, 15, 16, 17] and
                    aml.journal_id == company_tax_journal):
                continue
            if aml.account_id.code not in res.keys():
                res[aml.account_id.code] = []
            res[aml.account_id.code].append({
                'B': aml.move_id.name,
                'C': aml.name,
                'D': aml.ref,
                'E': aml.date,
                'F': aml.partner_id.name if aml.partner_id else '',
                'G': aml.debit if aml.debit > 0.0 else 0.0,
                'H': aml.credit if aml.credit > 0.0 else 0.0,
            })
        # We get the expense info of the negative expenses
        data = expense_obj.search([
            ('amount_balance', '<', 0.0), ('state', '=', 'confirmed'),
            ('move_id.date', '>=', self.date_start),
            ('move_id.date', '<=', self.date_end)])
        for expense in data:
            aml_info = self.with_context(expense=True).get_tms_expense_info(
                expense, False)
            for item in aml_info:
                # Set the results to the main dictionary
                if item[0] not in res.keys():
                    res[item[0]] = []
                res[item[0]].append({
                    'B': item[1],
                    'C': item[2],
                    'D': item[3],
                    'E': aml.date,
                    'F': aml.partner_id.name if aml.partner_id else '',
                    'G': item[4] if item[5] == 'debit' else 0.0,
                    'H': item[4] if item[5] == 'credit' else 0.0,
                })
        dictio_keys = sorted(res.keys())
        return res, dictio_keys

    @api.multi
    def print_report(self):
        self.ensure_one()
        account_obj = self.env['account.account']
        wb = Workbook()
        ws1 = wb.active
        ws1.append({
            'A': _('Account'),
            'B': _('Journal Entry'),
            'C': _('Name'),
            'D': _('Reference'),
            'E': _('Date'),
            'F': _('Partner'),
            'G': _('Debit'),
            'H': _('Credit'),
            'I': _('Balance'),
        })
        res, dictio_keys = self.prepare_data()
        # Loop the sorted dictionary keys and fill the xlsx file
        for key in dictio_keys:
            account_id = account_obj.search([('code', '=', key)])
            balance = 0.0
            ws1.append({
                'A': account_id.code + ' ' + account_id.name
            })
            for item in res[key]:
                if item['C'] == _('Initial Balance'):
                    ws1.append(item)
                    balance = item['I']
                    continue
                balance += (item['G'] - item['H'])
                item['I'] = balance
                ws1.append(item)
            ws1.append({
                'G': sum([x['G'] for x in res[key]]),
                'H': sum([x['H'] for x in res[key]]),
                'I': balance,
            })
        # Apply styles to the xlsx file
        for row in ws1.iter_rows():
            if row[0].value and not row[1].value:
                ws1[row[0].coordinate].font = Font(
                    bold=True, color='7CB7EA')
            if not row[1].value and row[8].value and not row[2].value:
                ws_range = row[6].coordinate + ':' + row[8].coordinate
                for row_cell in enumerate(ws1[ws_range]):
                    for cell in enumerate(row_cell[1]):
                        cell[1].font = Font(bold=True)
            if not row[1].value and row[8].value and row[2].value:
                row[8].font = Font(bold=True)
        xlsx_file = save_virtual_workbook(wb)
        self.xlsx_file = base64.encodestring(xlsx_file)
        self.xlsx_filename = _('TMS General Ledger.xlsx')
        self.state = 'print'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.general.ledger.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
