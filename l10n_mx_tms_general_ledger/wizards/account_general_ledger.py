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
    def get_amls_info(self):
        self.ensure_one()
        self._cr.execute("""
            SELECT aml.id
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE aml.date BETWEEN %s AND %s
                AND aa.user_type_id NOT IN (14, 15, 16, 17)
            ORDER BY aml.account_id""", (self.date_start, self.date_end))
        amls = self._cr.fetchall()
        return amls

    @api.model
    def get_cash_info(self, aml):
        # Query to get the payments in aml
        items = []
        inv_obj = self.env['account.invoice']
        self._cr.execute("""
            SELECT account_invoice_id
            FROM account_invoice_account_move_line_rel
            WHERE account_move_line_id = %s""", (aml.id,))
        invoice_ids = self._cr.fetchall()
        if not invoice_ids:
            return []
        lines = inv_obj.browse([x[0] for x in invoice_ids]).mapped(
                'move_id.line_ids').filtered(
                lambda r: r.account_id.user_type_id.id in [14, 15, 16, 17])
        for line in lines:
            line_rate = 1 / len(lines)
            taxes = line.mapped('tax_ids.amount')
            amount_untaxed = abs(aml.balance) * line_rate
            for tax in taxes:
                tax_rate = tax / 100
                amount_untaxed -= (
                    abs(amount_untaxed) / (tax_rate + 1.0) * tax_rate)
            items.append(
                [line.account_id.code, line.move_id.name,
                 line.ref, round(amount_untaxed, 4)])
        return items

    @api.multi
    def print_report(self):
        self.ensure_one()
        res = {}
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
        data = self.get_amls_info()
        account_obj = self.env['account.account']
        for aml in self.env['account.move.line'].browse([x[0] for x in data]):
            if aml.journal_id.type in ['bank', 'cash']:
                aml_info = self.get_cash_info(aml)
                for item in aml_info:
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
            else:
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
