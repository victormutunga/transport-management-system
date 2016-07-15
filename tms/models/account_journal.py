# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    tms_advance_journal = fields.Boolean(
        string='TMS Advance Journal',
        help='If set to True then it will be used for TMS '
        'Advance Invoices. It must be a General Type Journal',
        default=(lambda *a: False))
    tms_fuelvoucher_journal = fields.Boolean(
        string='TMS Fuel Voucher Journal',
        help='If set to True then it will be used to create '
        'Moves when confirming TMS Fuel Voucher. It must be '
        'a General Type Journal',
        default=(lambda *a: False))
    tms_expense_journal = fields.Boolean(
        string='TMS Expense Journal',
        help='If set to True then it will be used for TMS '
        'Expense Invoices. It must be a General Type Journal',
        default=(lambda *a: False))
    tms_supplier_journal = fields.Boolean(
        string='TMS Freight Supplier Journal',
        help='If set to True then it will be used for TMS '
        'Waybill Supplier Invoices. It must be a Purchase Type Journal',
        default=(lambda *a: False))
    tms_waybill_journal = fields.Boolean(
        string='TMS Waybill Journal',
        help='If set to True then it will be used to create '
        'Moves when confirming TMS Waybill . It must be a General '
        'Type Journal')
    tms_expense_suppliers_journal = fields.Boolean(
        string='TMS Default Suppliers Expense Journal',
        help='If set to True then it will be used to create '
        'Supplier Invoices when confirming TMS Travel Expense '
        'Record and when Creating Invoices from Fuel Vouchers. '
        'It must be a Purchase Type Journal',
        default=(lambda *a: False))
