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

from openerp.osv import osv, fields


class ProductCategory(osv.osv):
    _name = "product.category"
    _inherit = "product.category"

    _columns = {
        'tms_property_account_income_categ': fields.many2one(
            'account.account',
            string="Breakdown Income Account",
            help="Use this to define breakdown income account per \
            vehicle for Freights, Moves, Insurance, etc."),
        'tms_property_account_expense_categ': fields.many2one(
            'account.account',
            string="Breakdown Expense Account",
            help="Use this to define breakdown expense account per \
            vehicle for Fuel, Travel Expenses, etc."),
    }

