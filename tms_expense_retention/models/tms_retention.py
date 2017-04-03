# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, exceptions, fields, models


class tms_retention(models.Model):
    _name = "tms.retention"
    _description = "Tms Retention"

    name = fields.Char(
        string='Name',
    )
    retention_type = fields.Selection(
        [('days', 'Days'),
         ('salary', 'Salary'), ],
        string='Retention Type',
        default='days')
    factor = fields.Float(
        'Factor',
    )
    mixed = fields.Boolean(
        string='Mixed',
    )
    fixed_amount = fields.Float(
        'Fired Amount',
    )
    employee_ids = fields.One2many(
        'hr.employee',
        'retention_id',
        string='Employees',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )

    @api.constrains('product_id')
    def unique_product(self):
        for rec in self:
            product = rec.search([
                ('product_id', '=', rec.product_id.id),
                ('id', '!=', rec.id)])
            if product:
                raise exceptions.ValidationError(
                    _('Only there must be a product "' +
                        product.product_id.name + '"'))
