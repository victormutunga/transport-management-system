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

# Fields <vechicle_id>, <employee_id> added to acount_move_line for
# reporting and analysis and constraint added


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=False)
    employee_id = fields.Many2one('hr.employee', 'Driver', required=False)
    sale_shop_id = fields.Many2one('sale.shop', 'Shop', required=False)

    def _check_mandatory_vehicle(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            return ((record.account_id.tms_vehicle_mandatory and
                    record.vehicle_id.id)
                    if record.account_id.tms_vehicle_mandatory else True)
        return True

    def _check_mandatory_employee(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            return ((record.account_id.tms_employee_mandatory and
                     record.employee_id.id)
                    if record.account_id.tms_employee_mandatory else True)
        return True

    def _check_mandatory_sale_shop(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            return ((record.account_id.tms_sale_shop_mandatory and
                     record.sale_shop_id.id)
                    if record.account_id.tms_sale_shop_mandatory else True)
        return True

    _constraints = [
        (_check_mandatory_vehicle,
            'Error ! You have not added Vehicle to Move Line',
            ['vehicle_id']),
        (_check_mandatory_employee,
            'Error ! You have not added Employee to Move Line',
            ['employee_id']),
        (_check_mandatory_sale_shop,
            'Error ! You have not added Sale Shop to Move Line',
            ['sale_shop_id']),
    ]
