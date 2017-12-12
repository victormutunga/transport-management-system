# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from __future__ import division
from datetime import datetime

import base64
import calendar
import logging

from odoo import api, fields, models
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
        month_start = "%s-%s-01" % (today.year, today.month)
        return month_start

    @api.model
    def get_month_end(self):
        today = datetime.now()
        month_end = "%s-%s-%s" % (
            today.year, today.month, calendar.monthrange(
                today.year-1, today.month)[1])
        return month_end

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
            self._cr.execute(
                """SELECT aml.id
                FROM account_move_line aml
                JOIN account_account aa ON aa.id = aml.account_id
                JOIN account_journal aj ON aj.id = aml.journal_id
                WHERE aml.date BETWEEN %s AND %s
                    AND aj.type = %s
                ORDER BY aml.account_id""",
                (self.date_start, self.date_end, 'general'))
            amls = self._cr.fetchall()
        return amls

    @api.model
    def get_cash_info(self, aml):
        """This method get the cash basis amounts based on the payments"""
        am_obj = self.env['account.move']
        aml_obj = self.env['account.move.line']
        items = []
        # This method search the aml linked to the invoice
        self._cr.execute(
            """
            SELECT CASE WHEN pr.debit_move_id = %s THEN
                pr.credit_move_id ELSE pr.debit_move_id END AS inv_aml,
                pr.amount, pr.amount_currency
            FROM account_partial_reconcile pr
            WHERE pr.credit_move_id = %s OR pr.debit_move_id = %s""",
            (aml.id, aml.id, aml.id,))
        partials = self._cr.dictfetchall()
        if not partials:
            return []
        for partial in partials:
            move = am_obj.search([('line_ids', 'in', partial['inv_aml'])])
            # Exchange currency
            if move.journal_id.id == 4:
                line = aml_obj.browse(partial['inv_aml'])
                items.append(
                    [line.account_id.code, line.move_id.name,
                     line.ref, round(abs(line.balance), 4)])
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
                     line.ref, amount_untaxed])
        return items

    @api.multi
    def prepare_data(self):
        """ This method prepare the report data into a dictionary ordered by
        the account code"""
        res = {}
        # First get the amls without income statement accounts
        data = self.get_amls_info('normal')
        for aml in self.env['account.move.line'].browse([x[0] for x in data]):
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
                        'D': aml.date,
                        'E': aml.partner_id.name if aml.partner_id else '',
                        'F': item[3] if aml.debit > 0.0 else 0.0,
                        'G': item[3] if aml.credit > 0.0 else 0.0,
                    })
            # Set the  aml to the main dictionary
            if aml.account_id.code not in res.keys():
                res[aml.account_id.code] = []
                res[aml.account_id.code].append({
                    'B': aml.move_id.name,
                    'C': aml.ref,
                    'D': aml.date,
                    'E': aml.partner_id.name if aml.partner_id else '',
                    'F': aml.debit if aml.debit > 0.0 else 0.0,
                    'G': aml.credit if aml.credit > 0.0 else 0.0,
                })
        # Finally get the amls of miscellanous journal entries
        data = self.get_amls_info('miscellanous')
        for aml in self.env['account.move.line'].browse([x[0] for x in data]):
            if aml.account_id.code not in res.keys():
                res[aml.account_id.code] = []
            res[aml.account_id.code].append({
                'B': aml.move_id.name,
                'C': aml.ref,
                'D': aml.date,
                'E': aml.partner_id.name if aml.partner_id else '',
                'F': aml.debit if aml.debit > 0.0 else 0.0,
                'G': aml.credit if aml.credit > 0.0 else 0.0,
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
            'C': _('Reference'),
            'D': _('Date'),
            'E': _('Partner'),
            'F': _('Debit'),
            'G': _('Credit'),
            'H': _('Balance'),
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
                balance += (item['F'] - item['G'])
                item['H'] = balance
                ws1.append(item)
            ws1.append({
                'F': sum([x['F'] for x in res[key]]),
                'G': sum([x['G'] for x in res[key]]),
                'H': balance,
            })
        # Apply styles to the xlsx file
        for row in ws1.iter_rows():
            if row[0].value and not row[1].value:
                ws1[row[0].coordinate].font = Font(
                    bold=True, color='7CB7EA')
            if not row[1].value and row[7].value:
                ws_range = row[5].coordinate + ':' + row[7].coordinate
                for row_cell in enumerate(ws1[ws_range]):
                    for cell in enumerate(row_cell[1]):
                        cell[1].font = Font(bold=True)
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
