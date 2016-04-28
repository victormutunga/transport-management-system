# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.exceptions import ValidationError
from openerp.tools.translate import _


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    tms_category = fields.Selection(
        [
            ('no_tms_product', 'No TMS Product'),
            ('freight', 'Freight'),
            ('move', 'Move'),
            ('insurance', 'Insurance'),
            ('highway_tolls', 'Highway Tolls'),
            ('other', 'Other'),
            ('real_expense', 'Real Expense'),
            ('fuel', 'Fuel'),
        ], string='TMS Product',
        help="""Product Type for using with TMS Module
  - No TMS Product: Not related to TMS
  - Freight: Represents Freight Price used in Waybills
  - Move: Represents Moves Price used in Waybills
  - Insurance: Represents Insurance for Load used in Waybills
  - Highway Tolls: Represents Highway Tolls used in Waybills
  - Other: Represents any other charge for Freight Service used in Waybills
  - Real Expense: Represent real expenses related to Travel, those that will \
        be used in Travel Expense Checkup.
  - Fuel: Used for filtering products used in Fuel Vouchers.
  All of these products MUST be used as a service because they will never \
        interact with Inventory.
""", default='no_tms_product')
    tms_property_account_income = fields.Many2one(
        'account.account', 'Breakdown Income Account',
        help='Use this to define breakdown income account per vehicle for \
        Freights, Moves, Insurance, etc.',
        required=False)
    tms_property_account_expense = fields.Many2one(
        'account.account', 'Breakdown Expense Account',
        help='Use this to define breakdown expense account per vehicle for \
        Fuel, Travel Expenses, etc.',
        required=False)

    @api.onchange('tms_category')
    def _onchange_tms_category(self):
        if self.tms_category in ['freight', 'move', 'insurance',
                                 'highway_tolls', 'other']:
            self.type = 'service'
            self.purchase_ok = False
            self.sale_ok = True
        elif self.tms_category in ['real_expense']:
            self.type = 'service'
            self.purchase_ok = True
            self.sale_ok = False
        elif self.tms_category in ['fuel']:
            self.type = 'product'
            self.purchase_ok = True
            self.sale_ok = False

    @api.multi
    @api.constrains('tms_category', 'type', 'purchase_ok', 'sale_ok')
    def _check_tms_product(self):
        for rec in self:
            if rec.tms_category in [
                    'freight', 'move', 'insurance', 'highway_tolls', 'other']:
                    if (rec.type != 'service' or rec.purchase_ok is True or
                            rec.sale_ok is False):
                        raise ValidationError(
                            _('Error! Product is not defined correctly...'))
            elif (rec.tms_category == 'real_expense' and
                    rec.type != 'service' or
                    rec.purchase_ok is False or rec.sale_ok is True):
                        raise ValidationError(
                            _('Error! Real Expense is not defined \
                                correctly...'))
            elif (rec.tms_category == 'fuel' and
                  rec.type != 'product' or
                  rec.purchase_ok is False or
                  rec.sale_ok is True):
                        raise ValidationError(
                            _('Error! Fuel is not defined correctly...'))
