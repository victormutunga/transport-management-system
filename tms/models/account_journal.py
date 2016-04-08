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


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    tms_advance_journal = fields.Boolean(
        string='TMS Advance Journal',
        help='If set to True then it will be used for TMS \
            Advance Invoices. It must be a General Type Journal',
        default=(lambda *a: False))
    tms_fuelvoucher_journal = fields.Boolean(
        string='TMS Fuel Voucher Journal',
        help='If set to True then it will be used to create \
            Moves when confirming TMS Fuel Voucher. It must be a \
            General Type Journal',
        default=(lambda *a: False))
    tms_expense_journal = fields.Boolean(
        string='TMS Expense Journal',
        help='If set to True then it will be used for TMS \
            Expense Invoices. It must be a General Type Journal',
        default=(lambda *a: False))
    tms_supplier_journal = fields.Boolean(
        string='TMS Freight Supplier Journal',
        help='If set to True then it will be used for TMS \
            Waybill Supplier Invoices. It must be a Purchase Type \
            Journal',
        default=(lambda *a: False))
    tms_waybill_journal = fields.Boolean(
        string='TMS Waybill Journal',
        help='If set to True then it will be used to create \
            Moves when confirming TMS Waybill . It must be a \
            General Type Journal')
    tms_expense_suppliers_journal = fields.Boolean(
        string='TMS Default Suppliers Expense Journal',
        help='If set to True then it will be used to create \
            Supplier Invoices when confirming TMS Travel Expense \
            Record and when Creating Invoices from Fuel Vouchers. \
            It must be a Purchase Type Journal',
        default=(lambda *a: False))
