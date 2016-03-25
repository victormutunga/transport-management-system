# -*- coding: utf-8 -*-
# © 2016 Jarsa Sistemas, S.A. de C.V.
# - Jesús Alan Ramos Rodríguez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class OperatingUnit(models.Model):
    _name = 'operating.unit'
    _inherit = 'operating.unit'

    tms_travel_seq = fields.Many2one('ir.sequence', string='Travel Sequence')
    tms_advance_seq = fields.Many2one('ir.sequence', string='Advance Sequence')
    tms_travel_expenses_seq = fields.Many2one(
        'ir.sequence', string='Travel Expenses Sequence')
    tms_fuel_sequence_ids = fields.Many2one(
        'ir.sequence',
        string='Fuel Sequence')
#    This field will be in tms_driver_loan module.
#    tms_loan_seq = fields.Many2one('ir.sequence', string='Loan Sequence')
