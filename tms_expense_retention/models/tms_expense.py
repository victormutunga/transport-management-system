# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, models
from openerp.exceptions import ValidationError


class TmsExpense(models.Model):
    _inherit = 'tms.expense'

    @api.multi
    def get_retention(self):
        for rec in self:
            retentions = ['ISR', 'Insurance']
            for obj in retentions:
                value = 0.0
                obj_retention = self.env['tms.retention']
                product = self.env['product.product'].search(
                    [('name', '=', obj), ('apply_for_retention', '=', True)],
                    limit=1)
                if not product:
                    raise ValidationError(
                        _('You must have a product called %s' % obj))
                retention = obj_retention.search([
                    ('product_id', '=', product.id)])
                days = int(rec.travel_days.split('D')[0])
                if retention.employee_ids:
                    if rec.employee_id in retention.employee_ids:
                        value = retention.factor * days
                else:
                    value = retention.factor * days
                if value > 0.0:
                    rec.expense_line_ids.create({
                        'name': obj,
                        'expense_id': rec.id,
                        'line_type': "salary_retention",
                        'product_qty': 1.0,
                        'product_uom_id': product.uom_id.id,
                        'product_id': product.id,
                        'unit_price': value,
                        'control': True
                    })

    @api.multi
    def get_travel_info(self):
        for rec in self:
            super(TmsExpense, self).get_travel_info()
            rec.get_retention()
