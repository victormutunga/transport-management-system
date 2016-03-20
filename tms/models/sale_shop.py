# -*- encoding: utf-8 -*-
from openerp import fields, models


class SaleShop(models.Model):
    _name = "sale.shop"
    _description = "Sales Shop"

    name = fields.Char('Shop Name', size=64, required=True)
    tms_travel_seq = fields.Many2one('ir.sequence', 'Travel Sequence')
    tms_advance_seq = fields.Many2one('ir.sequence', 'Advance Sequence')
    tms_travel_expenses_seq = fields.Many2one(
        'ir.sequence', 'Travel Expenses Sequence')
    tms_loan_seq = fields.Many2one('ir.sequence', 'Loan Sequence')
    tms_fuel_sequence_ids = fields.One2many(
        'tms.sale.shop.fuel.supplier.seq', 'shop_id',
        'Fuel Sequence per Supplier')
    company_id = fields.Many2one(
        'res.company', string='Company', required=False,
        default=(lambda s, cr, uid, c: s.pool.get(
            'res.company')._company_default_get('sale.shop')))
