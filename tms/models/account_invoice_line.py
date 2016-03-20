# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp import models, fields


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    vehicle_id = fields.Many2one(
        'fleet.vehicle', 'Vehicle', readonly=True, required=False)
    employee_id = fields.Many2one(
        'hr.employee', 'Driver', readonly=True, required=False)
    sale_shop_id = fields.Many2one(
        'sale.shop', 'Shop', readonly=True, required=False)

    def move_line_get_item(self, line):
        res = super(AccountInvoiceLine, self).move_line_get_item(
            self)
        res.update({
            'vehicle_id':
            line.vehicle_id.id if line.vehicle_id else False,
            'employee_id':
            line.employee_id.id if line.employee_id else False,
            'sale_shop_id':
            line.sale_shop_id.id if line.sale_shop_id else False,
            'line_id':
            line.id,
            'account_id2':
            line.account_id.id,
        })
        return res
