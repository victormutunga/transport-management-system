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
    fuelvoucher_journal_id = fields.Many2one(
        'account.journal',
        string='Fuel log Journal')
    expense_journal_id = fields.Many2one(
        'account.journal',
        string='Expense Journal')
    supplier_journal_id = fields.Many2one(
        'account.journal',
        string='Supplier Journal')
    waybill_journal_id = fields.Many2one(
        'account.journal',
        string='Waybill Journal')
    account_fuel_id = fields.Many2one(
        'account.account',
        string='Fuel Log Account')
    account_freight_id = fields.Many2one(
        'account.account', string='Waybill Freight Account')
    account_moves_id = fields.Many2one(
        'account.account',
        string='Waybill Moves Account')
    account_highway_tolls_id = fields.Many2one(
        'account.account',
        string='Waybill Highway Tolls Account')
    account_insurance_id = fields.Many2one(
        'account.account',
        string='Waybill Insurance Account')
    account_other_id = fields.Many2one(
        'account.account',
        string='Waybill Other Account')
    fuelvoucher_product_id = fields.Many2one(
        'product.product',
        string="Fuel log product")
    waybill_freight_id = fields.Many2one(
        'product.product',
        string='Waybill Freight Product')
    waybill_moves_id = fields.Many2one(
        'product.product',
        string='Waybill Moves Product')
    waybill_highway_tolls_id = fields.Many2one(
        'product.product',
        string='Waybill Highway Tolls Product')
    waybill_insurance_id = fields.Many2one(
        'product.product',
        string='Waybill Insurance Product')
    waybill_other_product_id = fields.Many2one(
        'product.product',
        string='Waybill Other Product')
    ieps_product_id = fields.Many2one('product.product', string='IEPS Product')
