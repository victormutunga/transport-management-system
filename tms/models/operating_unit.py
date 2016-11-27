# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    travel_sequence_id = fields.Many2one(
        'ir.sequence',
        string='Travel Sequence')
    fuel_log_sequence_id = fields.Many2one(
        'ir.sequence', string='Fuel Log Sequence')
    advance_sequence_id = fields.Many2one(
        'ir.sequence', string='Advance Sequence')
    waybill_sequence_id = fields.Many2one(
        'ir.sequence', string='Waybill Sequence')
    expense_sequence_id = fields.Many2one(
        'ir.sequence', string='Expense Sequence')
    advance_journal_id = fields.Many2one(
        'account.journal',
        string='Advance Journal')
    expense_journal_id = fields.Many2one(
        'account.journal',
        string='Expense Journal')
    ieps_product_id = fields.Many2one('product.product', string='IEPS Product')
