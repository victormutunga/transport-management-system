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

# Additionat field to set Account Journal for Advances and Travel Expenses


class AccountJournal(osv.osv):
    _inherit = 'account.journal'

    _columns = {
        'tms_advance_journal':
        fields.boolean('TMS Advance Journal',
                       help='If set to True then it will be used for TMS \
                       Advance Invoices. It must be a General Type Journal'),
        'tms_fuelvoucher_journal':
        fields.boolean('TMS Fuel Voucher Journal',
                       help='If set to True then it will be used to create \
                       Moves when confirming TMS Fuel Voucher. It must be a \
                       General Type Journal'),
        'tms_expense_journal':
        fields.boolean('TMS Expense Journal',
                       help='If set to True then it will be used for TMS \
                       Expense Invoices. It must be a General Type Journal'),
        'tms_supplier_journal':
        fields.boolean('TMS Freight Supplier Journal',
                       help='If set to True then it will be used for TMS \
                       Waybill Supplier Invoices. It must be a Purchase Type \
                       Journal'),
        'tms_waybill_journal':
        fields.boolean('TMS Waybill Journal',
                       help='If set to True then it will be used to create \
                       Moves when confirming TMS Waybill . It must be a \
                       General Type Journal'),
        'tms_expense_suppliers_journal':
        fields.boolean('TMS Default Suppliers Expense Journal',
                       help='If set to True then it will be used to create \
                       Supplier Invoices when confirming TMS Travel Expense \
                       Record and when Creating Invoices from Fuel Vouchers. \
                       It must be a Purchase Type Journal'),
    }

    _defaults = {

        'tms_advance_journal': lambda *a: False,
        'tms_fuelvoucher_journal': lambda *a: False,
        'tms_expense_journal': lambda *a: False,
        'tms_supplier_journal': lambda *a: False,
        'tms_expense_suppliers_journal': lambda *a: False,
    }
