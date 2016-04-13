# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models
from openerp.tools.translate import _


# Products => We need flags for some process with TMS Module
class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    tms_category = fields.Selection(
        [
            ('no_tms_product', 'No TMS Product'),
            ('transportable', 'Transportable'),
            ('freight', 'Freight'),
            ('move', 'Move'),
            ('insurance', 'Insurance'),
            ('highway_tolls', 'Highway Tolls'),
            ('other', 'Other'),
            ('real_expense', 'Real Expense'),
            ('madeup_expense', 'Made-up Expense'),
            ('salary', 'Salary'),
            ('salary_retention', 'Salary Retention'),
            ('salary_discount', 'Salary Discount'),
            ('negative_balance', 'Negative Balance'),
            ('fuel', 'Fuel'),
            ('indirect_expense', 'Indirect Expense (Agreements)'),
        ], 'TMS Type',
        # required=True,
        help="""Product Type for using with TMS Module
  - No TMS Product: Not related to TMS
  - Transportable: Transportable Product used in Waybills
  - Freight: Represents Freight Price used in Waybills
  - Move: Represents Moves Price used in Waybills
  - Insurance: Represents Insurance for Load used in Waybills
  - Highway Tolls: Represents Highway Tolls used in Waybills
  - Other: Represents any other charge for Freight Service used in Waybills
  - Real Expense: Represent real expenses related to Travel, those that will \
        be used in Travel Expense Checkup.
  - Made-Up Expense: Represent made-up expenses related to Travel, those that \
        will be used in Travel Expense Checkup.
  - Fuel: Used for filtering products used in Fuel Vouchers.
  - Indirect Expense (Agreements): Used to define Accounts for Agreements \
        Indirect Expenses.
  All of these products MUST be used as a service because they will never \
        interact with Inventory.
""", translate=True, default=(lambda *a: 'no_tms_product'))
    tms_account_ids = fields.Many2many(
        'account.account', 'tms_product_account_rel',
        'product_id', 'account_id', 'Accounts for this product')
    tms_activity_duration = fields.Float(
        'Duration', digits=(14, 2), help="Activity duration in hours")
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
    tms_default_freight = fields.Boolean(
        'Default Freight',
        help='Use this as default product for Freight in Waybills')
    tms_default_supplier_freight = fields.Boolean(
        'Default Supplier Freight',
        help='Use this as default product for Supplier Freight in \
        Waybills')
    tms_default_salary = fields.Boolean(
        'Default Salary',
        help='Use this as default product for Salary in Travel Expense \
        Records')
    tms_default_fuel_discount = fields.Boolean(
        'Default Fuel Discount',
        help='Use this as default product for Fuel Difference Discount in \
        Travel Expense Records')

    def _check_tms_product(self):
        for record in self.browse():
            if record.tms_category in ['transportable']:
                return (record.type == 'service' and
                        record.procure_method == 'make_to_stock' and
                        record.supply_method == 'buy' and not
                        record.sale_ok and not record.purchase_ok)
            elif record.tms_category in ['freight', 'move', 'insurance',
                                         'highway_tolls', 'other']:
                return (record.type == 'service' and
                        record.procure_method == 'make_to_stock' and
                        record.supply_method == 'buy' and record.sale_ok)
            elif record.tms_category in [
                    'real_expense', 'madeup_expense', 'salary',
                    'salary_retention', 'salary_discount',
                    'negative_balance', 'indirect_expense']:
                return (record.type == 'service' and
                        record.procure_method == 'make_to_stock' and
                        record.supply_method == 'buy' and record.purchase_ok)
            elif record.tms_category in ['fuel']:
                return (record.type == 'product' and
                        record.procure_method == 'make_to_stock' and
                        record.supply_method == 'buy' and record.purchase_ok)

        return True

    def _check_default_fuel_discount(self):
        prod_obj = self.pool.get('product.product')
        for record in self.browse(self):
            if (record.tms_category == 'salary_discount' and
                    record.tms_default_fuel_discount):
                res = prod_obj.search(
                    [('tms_default_fuel_discount', '=', 1)], context=None)
                if res and res[0] and res[0] != record.id:
                    return False
        return True

    def _check_default_freight(self):
        prod_obj = self.pool.get('product.product')
        for record in self.browse(self):
            if record.tms_category == 'freight' and record.tms_default_freight:
                res = prod_obj.search(
                    [('tms_default_freight', '=', 1)], context=None)
                if res and res[0] and res[0] != record.id:
                    return False
        return True

    def _check_default_supplier_freight(self):
        prod_obj = self.pool.get('product.product')
        for record in self.browse(self):
            if (record.tms_category == 'freight' and
                    record.tms_default_supplier_freight):
                res = prod_obj.search(
                    [('tms_default_supplier_freight', '=', 1)], context=None)
                if res and res[0] and res[0] != record.id:
                    return False
        return True

    def _check_default_salary(self):
        prod_obj = self.pool.get('product.product')
        for record in self.browse(self):
            if record.tms_category == 'salary' and record.tms_default_salary:
                res = prod_obj.search(
                    [('tms_default_salary', '=', 1)], context=None)
                if res and res[0] and res[0] != record.id:
                    return False
        return True

    _constraints = [
        (_check_tms_product,
         'Error ! Product is not defined correctly...Please see tooltip for \
         TMS Category',
         ['tms_category']),
        (_check_default_freight,
         'Error ! You can not have two or more products defined as Default \
         Freight',
         ['tms_default_freight']),
        (_check_default_supplier_freight,
         'Error ! You can not have two or more products defined as Default \
         Supplier Freight',
         ['tms_default_supplier_freight']),
        (_check_default_salary,
         'Error ! You can not have two or more products defined as Default \
         Salary',
         ['tms_default_salary']),
        (_check_default_fuel_discount,
         'Error ! You can not have two or more products defined as Default \
         Fuel Discount',
         ['tms_default_fuel_discount']),
    ]

    def write(self, values):
        if 'tms_category' in values:
            raise Warning(
                _('Warning !'),
                _('You can not change TMS Category for any product...'))
        return super(ProductProduct, self).write(values)

    def onchange_tms_category(self, tms_category):
        val = {}
        if not tms_category or tms_category == 'standard':
            return val
        if tms_category in [
                'transportable', 'freight', 'move', 'insurance',
                'highway_tolls', 'other', 'real_expense', 'madeup_expense',
                'salary', 'salary_retention', 'salary_discount',
                'negative_balance']:
            val = {
                'type': 'service',
                'procure_method': 'make_to_stock',
                'supply_method': 'buy',
                'purchase': False,
                'sale': False,
            }
        return {'value': val}
