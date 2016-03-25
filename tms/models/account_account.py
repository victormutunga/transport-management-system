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

from openerp import fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    tms_vehicle_mandatory = fields.Boolean(
        string='TMS Vehicle Mandatory', help='If set to True then it will require to add \
            Vehicle to Move Line', default=lambda *a: False)
    tms_employee_mandatory = fields.Boolean(
        string='TMS Vehicle Mandatory', help='If set to True then it will require to add \
            Vehicle to Move Line', default=lambda *a: False)
    tms_sale_shop_mandatory = fields.Boolean(
        string='TMS Sale Shop Mandatory', help='If set to True then it will require to add \
                       Sale Shop to Move Line', default=lambda *a: False)
