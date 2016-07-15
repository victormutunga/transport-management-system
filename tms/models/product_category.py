# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = "product.category"

    tms_property_account_income_categ = fields.Many2one(
        'account.account',
        string="Breakdown Income Account",
        help="Use this to define breakdown income account per "
        "vehicle for Freights, Moves, Insurance, etc.")
    tms_property_account_expense_categ = fields.Many2one(
        'account.account',
        string="Breakdown Expense Account",
        help="Use this to define breakdown expense account per "
        "vehicle for Fuel, Travel Expenses, etc.")
