# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class TmsBase(models.Model):
    _name = 'tms.base'
    _description = 'Base'

    name = fields.Char(string='', required=True)
    advance_journal_id = fields.Many2one(
        'account.journal',
        string='Advance Journal'
        )
    fuelvoucher_journal_id = fields.Many2one(
        'account.journal',
        string='Fuel log Journal'
        )
    expense_journal_id = fields.Many2one(
        'account.journal',
        string='Expense Journal'
        )
    supplier_journal_id = fields.Many2one(
        'account.journal',
        string='Supplier Journal'
        )
    waybill_journal_id = fields.Many2one(
        'account.journal',
        string='Waybill Journal'
        )
    account_fuel_id = fields.Many2one(
        'account.account',
        string='Fuel log account')
    account_fleight_id = fields.Many2one(
        'account.account',
        string='')
