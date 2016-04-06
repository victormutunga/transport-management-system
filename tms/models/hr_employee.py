# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models


class HrEmployee(models.Model):
    _description = 'Employees'
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    def name_get(self):
        reads = self.read(['name'])
        res = []
        for record in reads:
            name = ('(%s) ' % record['id']) + record['name']
            res.append((record['id'], name))
        return res

    def name_search(self, user, name='', args=None,
                    operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(
                user, [('name', '=', name)] + args,
                limit=limit)
            if not ids:
                try:
                    int_name = int(name)
                    ids = self.search(
                        user, [('id', '=', int_name)] + args,
                        limit=limit)
                except:
                    ids = []
            if not ids:
                ids = set()
                ids.update(self.search(
                    user, args + [('name', operator, name)],
                    limit=limit))
                ids = list(ids)
        else:
            ids = self.search(user, args, limit=limit)
        result = self.name_get(user, ids)
        return result

    tms_category = fields.Selection(
        [('none', 'N/A'), ('driver', 'Driver'),
         ('mechanic', 'Mechanic'), ], 'TMS Category',
        help='Used to define if this person will be used as \
            a Driver (Frieghts related) or Mechanic (Maintenance \
            related)', required=False, default=None)
    tms_advance_account_id = fields.Many2one(
        'account.account', 'Advance Account',
        domain=[('type', '=', 'other')])
    tms_expense_negative_balance_account_id = fields.Many2one(
        'account.account', 'Negative Balance Account',
        domain=[('type', '=', 'other')])
    tms_supplier_driver = fields.Boolean('Supplier Driver')
    tms_supplier_id = fields.Many2one(
        'res.partner', 'Supplier',
        domain=[('supplier', '=', 1)])
    # tms_global_salary = fields.Float(
    #     compute='job_id.tms_global_salary',
    #     digits=(18, 6), string='Salary', readonly=True)
    tms_alimony = fields.Float('Alimony', digits=(18, 6))
    tms_alimony_prod_id = fields.Many2one(
        'product.product', 'Alimony Product',
        domain=[('tms_category', '=', 'salary_discount')])
    tms_house_rent_discount_perc = fields.Float(
        'Monthly House Rental Discount (%)', digits=(18, 6))
    tms_house_rent_prod_id = fields.Many2one(
        'product.product', 'House Rental Product',
        domain=[('tms_category', '=', 'salary_discount')])
    tms_house_rent_discount = fields.Float(
        'Monthly House Rental Discount', digits=(18, 6))
    tms_credit_charge_discount = fields.Float(
        'Monthly Credit Amount Discount', digits=(18, 6))
    tms_credit_charge_prod_id = fields.Many2one(
        'product.product', 'Credit Charge Product',
        domain=[('tms_category', '=', 'salary_discount')])
    tms_social_security_discount = fields.Float(
        'Social Security Discount', digits=(18, 6))
    tms_social_security_prod_id = fields.Many2one(
        'product.product', 'Social Security Product',
        domain=[('tms_category', '=', 'salary_discount')])
    tms_salary_tax_discount = fields.Float(
        'Salary Tax Discount', digits=(18, 6))
    tms_salary_tax_prod_id = fields.Many2one(
        'product.product', 'Salary Tax Product',
        domain=[('tms_category', '=', 'salary_retention')])
    tms_global_salary = fields.Float(
        'Global Salary', digits=(18, 6))
    # shop_id = fields.Many2one('sale.shop', 'Shop')
    # , domain=[('company_id', '=', user.company_id.id)]),
