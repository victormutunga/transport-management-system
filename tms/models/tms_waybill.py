# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
# from openerp.tools.translate import _


class TmsWaybill(models.Model):
    _name = 'tms.waybill'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Waybills'

    @api.multi
    def _amount_all(self):
        cur_obj = self.env['res.currency']
        for waybill in self.search(self):
            cur = waybill.currency_id
            x_freight = 0.0
            x_move = 0.0
            x_highway = 0.0
            x_insurance = 0.0
            x_other = 0.0
            x_subtotal = 0.0
            x_tax = 0.0
            x_total = 0.0
            for line in waybill.waybill_line:
                    if line.product_id.tms_category == 'freight':
                        x_freight += line.price_subtotal
                    else:
                        x_freight += 0.0
                    if line.product_id.tms_category == 'move':
                        x_move += line.price_subtotal
                    else:
                        x_move += 0.0
                    if line.product_id.tms_category == 'highway_tolls':
                        x_highway += line.price_subtotal
                    else:
                        x_highway += 0.0
                    if line.product_id.tms_category == 'insurance':
                        x_insurance += line.price_subtotal
                    else:
                        x_insurance += 0.0
                    if line.product_id.tms_category == 'other':
                        x_other += line.price_subtotal
                    else:
                        x_other += 0.0
                    x_subtotal += line.price_subtotal
                    x_tax += line.tax_amount
                    x_total += line.price_total

            self.amount_freight = cur_obj.round(cur, x_freight)
            self.amount_move = cur_obj.round(cur, x_move)
            self.amount_highway_tolls = cur_obj.round(cur, x_highway)
            self.amount_insurance = cur_obj.round(cur, x_insurance),
            self.amount_other = cur_obj.round(cur, x_other)
            self.amount_untaxed = cur_obj.round(cur, x_subtotal)
            self.amount_tax = cur_obj.round(cur, x_tax)
            self.amount_total = cur_obj.round(cur, x_total)

    # def _invoiced(self, field_name):
    #     res = {}
    #     for rec in self.browse(self):
    #         # print "rec.invoice_id.id: ", rec.invoice_id.id
    #         # print "rec.invoice_id.state: ", rec.invoice_id.state
    #         invoiced = (bool(rec.invoice_id and rec.invoice_id.id and
    #                     rec.invoice_id.state != 'cancel' or False))
    #         paid = bool(
    #             rec.invoice_id and rec.invoice_id.state == 'paid' or False)
    #         res[rec.id] = {
    #             'invoiced': invoiced,
    #             'invoice_paid': paid,
    #             'invoice_name': (
    #                 rec.invoice_id and rec.invoice_id.state != 'cancel' and
    #                 rec.invoice_id.reference or ''),
    #         }

    # def _supplier_invoiced(self, field_name):
    #     res = {}
    #     for record in self.browse(self):
    #         xinvoiced = (
    #             bool(record.supplier_invoice_id and
    #                  record.supplier_invoice_id.id and
    #                  record.supplier_invoice_id.state != 'cancel' or False))
    #         xpaid = bool(record.invoice_id and
    #                      record.invoice_id.state == 'paid')
    #         res[record.id] = {
    #             'supplier_invoiced': xinvoiced,
    #             'supplier_invoice_paid': xpaid,
    #             'supplier_invoice_name': (
    #                 record.supplier_invoice_id and
    #                 record.supplier_invoice_id.state != 'cancel' and
    #                 (record.supplier_invoice_id.supplier_invoice_number or
    #                     record.supplier_invoice_id.reference) or False)
    #         }

    # def _shipped_product(self, field_name):
    #     res = {}

    #     context_wo_lang = self.copy()
    #     context_wo_lang.pop('lang', None)
    #     for waybill in self.browse(context=context_wo_lang):
    #         volume = weight = qty = 0.0
    #         for record in waybill.waybill_shipped_product:
    #             qty += record.product_uom_qty
    #             # print "Waybill - record.product_uom.category_id.name",
    #             # record.product_uom.category_id.name
    #             if record.product_uom.category_id.name == 'Volume':
    #                 volume += record.product_uom_qty
    #             else:
    #                 volume += 0.0
    #             if record.product_uom.category_id.name == 'Weight':
    #                 weight += record.product_uom_qty
    #             else:
    #                 weight += 0.0
    #             res[waybill.id] = {
    #                 'product_qty': qty,
    #                 'product_volume': volume,
    #                 'product_weight': weight,
    #                'product_uom_type': (record.product_uom.category_id.name),
    #             }

    # def _get_route_distance(self, field_name, arg):
    #     res = {}
    #     distance = 1.0
    #     for waybill in self.browse(self):
    #         distance = waybill.route_id.distance
    #         res[waybill.id] = distance

    # def _get_supplier_amount(self, field_name):
    #     res = {}
    #     for waybill in self.browse(self):
    #         result = 0.0
    #         if waybill.waybill_type == 'outsourced':
    #             factor_special_obj = self.pool.get('tms.factor.special')
    #             factor_special_ids = factor_special_obj.search(
    #                 [('type', '=', 'supplier'), ('active', '=', True)])
    #             if len(factor_special_ids):
    #                 exec factor_special_obj.browse(
    #                     factor_special_ids)[0].python_code
    #                 # print result
    #             else:
    #                 factor_obj = self.pool.get('tms.factor')
    #                 result = factor_obj.calculate(
    #                     'waybill', [waybill.id], 'supplier', False)
    #         res[waybill.id] = result

    # def _get_newer_travel_id(self, field_name):
    #     res = {}
    #     travel_id = False
    #     for waybill in self.browse(self):
    #         for travel in waybill.travel_ids:
    #             travel_id = travel.id
    #         res[waybill.id] = travel_id

    # def _get_waybill_type(self, field_name):
    #     print "Entrando aqui..."
    #     res = {}
    #     for waybill in self.browse(self):
    #         waybill_type = 'self'
    #         for travel in waybill.travel_ids:
    #             waybill_type = ('outsourced' if travel.unit_id.supplier_unit
    #                             else 'self')
    #         res[waybill.id] = waybill_type

    # def _get_order(self):
    #     result = {}
    #     for line in self.pool.get('tms.waybill.line').browse(self):
    #         result[line.waybill_id.id] = True

    # def _get_invoice(self):
    #     result = {}
    #     for invoice in self.pool.get('account.invoice').browse(self):
    #         for waybill in invoice.waybill_ids:
    #             result[waybill.id] = True

    # def _get_supplier_invoice(self):
    #     result = {}
    #     for invoice in self.pool.get('account.invoice').browse(self):
    #         for waybill in invoice.waybill_ids:
    #             result[waybill.id] = True
    # __________________________________________________________________
    # waybill_customer_factor = fields.One2many(
    #     'tms.factor', 'waybill_id',
    #     string='Waybill Customer Charge Factors',
    #     domain=[('category', '=', 'customer')],
    #     readonly=False, states={'confirmed': [('readonly', True)],
    #                             'closed': [('readonly', True)]})
    # waybill_supplier_factor = fields.One2many(
    #     'tms.factor', 'waybill_id',
    #     string='Waybill Supplier Payment Factors',
    #     domain=[('category', '=', 'supplier')],
    #     readonly=False, states={'cancel': [('readonly', True)],
    #                             'closed': [('readonly', True)]})
    # expense_driver_factor = fields.One2many(
    #     'tms.factor', 'waybill_id',
    #     string='Travel Driver Payment Factors',
    #     domain=[('category', '=', 'driver')], readonly=False,
    #     states={'cancel': [('readonly', True)],
    #             'closed': [('readonly', True)]})
    tax_line = fields.One2many(
        'tms.waybill.taxes', 'waybill_id',
        string='Tax Lines', readonly=True,
        states={'draft': [('readonly', False)]})
    name = fields.Char('Name', size=64, readonly=False, select=True)
    # waybill_category = fields.Many2one(
    #     'tms.waybill.category', 'Category', ondelete='restrict',
    #      readonly=False,
    #     states={'cancel': [('readonly', True)],
    #             'done': [('readonly', True)],
    #             'closed': [('readonly', True)]})
    # sequence_id = fields.Many2one(
    #     'ir.sequence', 'Sequence', required=True, ondelete='restrict',
    #     readonly=False, states={'confirmed': [('readonly', True)]})
    travel_ids = fields.Many2many(
        'tms.travel',
        string='Travels',
        states={'confirmed': [('readonly', True)]})
    travel_id = fields.Many2one(
        'tms.travel',
        compute='_get_newer_travel_id',
        string='Actual Travel', readonly=True, store=True, ondelete='cascade')
    # supplier_id = fields.Many2one(
    #     'res.partner',
    #     related='unit_id.supplier_id',
    #     string='Freight Supplier', store=True, readonly=True)
    # supplier_amount = fields.Float(
    #     compute=_get_supplier_amount, string='Supplier Freight Amount',
    #     method=True, digits_compute=dp.get_precision('Sale Price'),
    #     help="Freight Amount from Supplier.", multi=False, store=True)
    unit_id = fields.Many2one(
        'fleet.vehicle',
        related='travel_id.unit_id',
        string='Unit', store=True, readonly=True)
    trailer1_id = fields.Many2one(
        'fleet.vehicle',
        related='travel_id.trailer1_id',
        string='Trailer 1', store=True, readonly=True)
    dolly_id = fields.Many2one(
        'fleet.vehicle',
        relate='travel_id.dolly_id',
        string='Dolly',
        store=True, readonly=True)
    trailer2_id = fields.Many2one(
        'fleet.vehicle',
        related='travel_id.trailer2_id',
        string='Trailer 2', store=True, readonly=True)
    employee_id = fields.Many2one(
        'hr.employee',
        related='travel_id.employee_id',
        string='Driver',
        store=True, readonly=True)
    employee2_id = fields.Many2one(
        'hr.employee',
        related='travel_id.employee2_id',
        string='Driver Helper', store=True, readonly=True)
    route_id = fields.Many2one(
        'tms.route',
        related='travel_id.route_id',
        string='Route',
        store=True, readonly=True)
    departure_id = fields.Many2one(
        'tms.place',
        related='route_id.departure_id',
        string='Departure',
        store=True, readonly=True)
    arrival_id = fields.Many2one(
        'tms.place',
        related='route_id.arrival_id',
        string='Arrival',
        store=True, readonly=True)
    origin = fields.Char(
        'Source Document', size=64, help="Reference of the document that \
        generated this Waybill request.", readonly=False,
        states={'confirmed': [('readonly', True)]})
    client_order_ref = fields.Char(
        'Customer Reference', size=64, readonly=False,
        states={'confirmed': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Pending'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled')], 'State', readonly=True,
        help="Gives the state of the Waybill. \n", select=True,
        default=(lambda *a: 'draft'))
    # billing_policy = fields.Selection([
    #     ('manual', 'Manual'),
    #     ('automatic', 'Automatic'), ],
    #     'Billing Policy', readonly=False,
    #     states={'confirmed': [('readonly', True)]},
    #     help="Gives the state of the Waybill. \n -The exception state is \
    #         automatically set when a cancel operation occurs in the invoice \
    #         validation (Invoice Exception) or in the picking list process \
    #        (Shipping Exception). \nThe 'Waiting Schedule' state is set when \
    #        the invoice is confirmed but waiting for the scheduler to run on \
    #         the date 'Ordered Date'.", select=True, default='manual')
    # waybill_type = fields.Selection(
    #     compute=_get_waybill_type, method=True,
    #     selection=[('self', 'Self'), ('outsourced', 'Outsourced')],
    #     string='Waybill Type', store=True,
    #     help=" - Self: Travel with our own units. \n - Outsourced: Travel \
    #     without our own units.", default='self')
    date_order = fields.Date(
        'Date', required=True, select=True, readonly=False,
        states={'confirmed': [('readonly', True)]},
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT)))
    user_id = fields.Many2one(
        'res.users', 'Salesman', select=True, readonly=False,
        states={'confirmed': [('readonly', True)]},
        default=(lambda self: self))
    partner_id = fields.Many2one(
        'res.partner', 'Customer', required=True, change_default=True,
        select=True, readonly=False,
        states={'confirmed': [('readonly', True)]})
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        states={'confirmed': [('readonly', True)]},
        default=lambda self: self.env['res.users'].company_id.currency_id.id)
    partner_invoice_id = fields.Many2one(
        'res.partner', 'Invoice Address', required=True,
        help="Invoice address for current Waybill.", readonly=False,
        states={'confirmed': [('readonly', True)]},
        default=(lambda self: self.env[
            'res.partner'].address_get(
            self['partner_id'])))
    partner_order_id = fields.Many2one(
        'res.partner', 'Ordering Contact', required=True,
        help="The name and address of the contact who requested the order \
        or quotation.", readonly=False,
        states={'confirmed': [('readonly', True)]},
        default=(lambda self: self.env['res.partner'].address_get(
            self['partner_id'])['contact']))
    # account_analytic_id = fields.Many2one(
    #     'account.analytic.account', 'Analytic Account',
    #     help="The analytic account related to a Waybill.", readonly=False,
    #     states={'confirmed': [('readonly', True)]})
    departure_address_id = fields.Many2one(
        'res.partner', 'Departure Address', required=True,
        help="Departure address for current Waybill.", readonly=False,
        states={'confirmed': [('readonly', True)]},
        default=(lambda self: self.env['res.partner'].address_get(
            self['partner_id'])))
    arrival_address_id = fields.Many2one(
        'res.partner', 'Arrival Address', required=True,
        help="Arrival address for current Waybill.", readonly=False,
        states={'confirmed': [('readonly', True)]},
        default=(lambda self: self.env['res.partner'].address_get(
            self['partner_id'])))
    # upload_point = fields.Char(
    #     'Upload Point', size=128, readonly=False,
    #     states={'confirmed': [('readonly', True)]})
    # download_point = fields.Char(
    #     'Download Point', size=128,  readonly=False,
    #     states={'confirmed': [('readonly', True)]})
    # shipped = fields.Boolean(
    #     'Delivered', readonly=True,
    #   help="It indicates that the Waybill has been delivered. This field is \
    #     updated only after the scheduler(s) have been launched.")
    invoice_id = fields.Many2one(
        'account.invoice', 'Invoice Record', readonly=True)
    # invoiced = fields.Boolean(
    #     compute=_invoiced, method=True, string='Invoiced',
    #     multi=True, store={
    #         'tms.waybill': (lambda self, cr, uid, ids, c={}: ids, None, 10),
    #         'account.invoice': (_get_invoice, ['state'], 20)},)
    # invoice_paid = fields.Boolean(
    #     compute=_invoiced, method=True, string='Paid', multi=True,
    #   store={'tms.waybill': (lambda self, cr, uid, ids, c={}: ids, None, 10),
    #            'account.invoice': (_get_invoice, ['state'], 20)})
    # invoice_name = fields.Char(
    #    compute=_invoiced, method=True, string='Invoice', size=64, multi=True,
    #   store={'tms.waybill': (lambda self, cr, uid, ids, c={}: ids, None, 10),
    #            'account.invoice': (_get_invoice, ['state'], 20)})
    # supplier_invoice_id = fields.Many2one(
    #     'account.invoice', 'Supplier Invoice Rec', readonly=True)
    # supplier_invoiced = fields.Boolean(
    #     compute=_supplier_invoiced, method=True, string='Supplier Invoiced',
    #     multi=True,
    #   store={'tms.waybill': (lambda self, cr, uid, ids, c={}: ids, None, 10),
    #            'account.invoice': (_get_supplier_invoice, ['state'], 20)})
    # supplier_invoice_paid = fields.Boolean(
    #     compute=_supplier_invoiced, method=True,
    #     string='Supplier Invoice Paid', multi='invoiced',
    #   store={'tms.waybill': (lambda self, cr, uid, ids, c={}: ids, None, 10),
    #            'account.invoice': (_get_supplier_invoice, ['state'], 20)})
    # supplier_invoice_name = fields.Char(
    #     compute=_supplier_invoiced, method=True, string='Supplier Invoice',
    #     size=64, multi='invoiced',
    #   store={'tms.waybill': (lambda self, cr, uid, ids, c={}: ids, None, 10),
    #            'account.invoice': (_get_supplier_invoice, ['state'], 20)})
    # supplier_invoiced_by = fields.Many2one(
    #     'res.users', 'Suppl. Invoiced by', readonly=True)
    # supplier_invoiced_date = fields.Datetime(
    #     'Suppl. Inv. Date', readonly=True, select=True)
    waybill_line = fields.One2many(
        'tms.waybill.line', 'waybill_id',
        string='Waybill Lines', readonly=False,
        states={'confirmed': [('readonly', True)]})
    # waybill_shipped_product = fields.One2many(
    #     'tms.waybill.shipped_product', 'waybill_id',
    #     string='Shipped Products',
    #     readonly=False, states={'confirmed': [('readonly', True)]})
    # product_qty = fields.Float(
    #     compute=_shipped_product, method=True, string='Sum Qty',
    #     digits=(20, 6), store=True, multi='product_qty')
    # product_volume = fields.Float(
    #     compute=_shipped_product, method=True, string='Sum Volume',
    #     digits=(20, 6), store=True, multi='product_qty')
    # product_weight = fields.Float(
    #     compute=_shipped_product, method=True, string='Sum Weight',
    # digits=(20, 6), store=True, multi='product_qty')
    # product_uom_type = fields.Char(
    #     compute=_shipped_product, method=True, string='Product UoM Type',
    #     size=64, store=True, multi='product_qty')
    # waybill_extradata = fields.One2many(
    #     'tms.waybill.extradata', 'waybill_id',
    #     string='Extra Data Fields',
    #     readonly=False, states={'confirmed': [('readonly', True)]})
    amount_freight = fields.Float(
        compute=_amount_all, method=True,
        digits_compute=dp.get_precision('Sale Price'),
        string='Freight', store=False, multi=True)
    amount_move = fields.Float(
        compute=_amount_all, method=True,
        digits_compute=dp.get_precision('Sale Price'),
        string='Moves', store=False, multi=True)
    amount_highway_tolls = fields.Float(
        compute=_amount_all, method=True,
        digits_compute=dp.get_precision('Sale Price'),
        string='Highway Tolls', store=False, multi=True)
    amount_insurance = fields.Float(
        compute=_amount_all, method=True,
        digits_compute=dp.get_precision('Sale Price'),
        string='Insurance', store=False, multi=True)
    amount_other = fields.Float(
        compute=_amount_all, method=True,
        digits_compute=dp.get_precision('Sale Price'),
        string='Other', store=False, multi=True)
    amount_untaxed = fields.Float(
        compute=_amount_all, method=True,
        digits_compute=dp.get_precision('Sale Price'),
        string='SubTotal', store=False, multi=True)
    amount_tax = fields.Float(
        compute=_amount_all, method=True,
        digits_compute=dp.get_precision('Sale Price'),
        string='Taxes', store=False, multi=True)
    amount_total = fields.Float(
        compute=_amount_all, method=True,
        digits_compute=dp.get_precision('Sale Price'),
        string='Total', store=False, multi=True)
    # distance_route = fields.Float(
    #     compute=_get_route_distance, string='Distance from route',
    #     method=True, digits=(18, 6), help="Route Distance.", multi=False)
    # distance_real = fields.Float(
    #     'Distance Real', digits=(18, 6),
    #     help="Route obtained by electronic reading")
    notes = fields.Text('Notes', readonly=False)
    # payment_term = fields.Many2one(
    #     'account.payment.term', 'Payment Term', readonly=False,
    #     states={'confirmed': [('readonly', True)]})
    # fiscal_position = fields.Many2one(
    #     'account.fiscal.position', 'Fiscal Position', readonly=False,
    #     states={'confirmed': [('readonly', True)]})
    date_start = fields.Datetime(
        'Load Date Sched', help="Date Start time for Load",
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_up_start_sched = fields.Datetime(
        'UpLd Start Sched',
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_up_end_sched = fields.Datetime(
        'UpLd End Sched',
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_up_docs_sched = fields.Datetime(
        'UpLd Docs Sched',
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_appoint_down_sched = fields.Datetime(
        'Download Date Sched',
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_down_start_sched = fields.Datetime(
        'Download Start Sched',
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_down_end_sched = fields.Datetime(
        'Download End Sched',
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_down_docs_sched = fields.Datetime(
        'Download Docs Sched',
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_end = fields.Datetime(
        'Travel End Sched', help="Date End time for Load",
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_start_real = fields.Datetime('Load Date Real', required=False)
    date_up_start_real = fields.Datetime('UpLoad Start Real', required=False)
    date_up_end_real = fields.Datetime('UpLoad End Real', required=False)
    date_up_docs_real = fields.Datetime('Load Docs Real', required=False)
    date_appoint_down_real = fields.Datetime(
        'Download Date Real', required=False)
    date_down_start_real = fields.Datetime(
        'Download Start Real', required=False)
    date_down_end_real = fields.Datetime('Download End Real', required=False)
    date_down_docs_real = fields.Datetime('Download Docs Real', required=False)
    date_end_real = fields.Datetime('Travel End Real', required=False)
#   time_from_appointment_to_uploading_std = fields.float('Std Time from
#         Appointment to Loading (Hrs)', digits=(10, 2), required=True,
#         readonly=False),
#   time_for_uploading_std = fields.float('Std Time for loading (Hrs)',
#         digits=(10, 2), required=True, readonly=False),
#   time_from_uploading_to_docs_sched = fields.float('Std Time from
#         Load to Document Release (Hrs)', digits=(10, 2), required=True,
#         readonly=False),
#   time_travel_sched = fields.float('Std Time for Travel (Hrs)',
#             digits=(10, 2), required=True, readonly=False),
#   time_from_appointment_to_downloading_std = fields.float('Std
#         Time from Download Appointment to Downloading (Hrs)',
#         digits=(10, 2), required=True, readonly=False),
#   time_for_downloading_sched = fields.float('Std Time for downloading
#         (Hrs)', digits=(10, 2), required=True, readonly=False),
#   time_from_downloading_to_docs_sched = fields.float('Std Time for
#         Download Document Release (Hrs)', digits=(10, 2),
#         required=True, readonly=False)
#   payment_type = fields.selection([
#           ('quantity','Charge by Quantity'),
#           ('tons','Charge by Tons'),
#           ('distance','Charge by Distance (mi./kms)'),
#           ('travel','Charge by Travel'),
#           ('volume', 'Charge by Volume'),
#           ], 'Charge Type',required=True,),
    amount_declared = fields.Float(
        'Amount Declared', digits_compute=dp.get_precision('Sale Price'),
        help=" Load value amount declared for insurance purposes...")
    replaced_waybill_id = fields.Many2one(
        'tms.waybill', 'Replaced Waybill', readonly=True)
    move_id = fields.Many2one(
        'account.move', 'Account Move', readonly=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Waybill must be unique !'),
    ]

    _order = 'name desc'

    # def get_freight_from_factors(self):
    #     prod_obj = self.pool.get('product.product')
    #     factor = self.pool.get('tms.factor')
    #     line_obj = self.pool.get('tms.waybill.line')
    #     fpos_obj = self.pool.get('account.fiscal.position')
    #     for waybill in self.browse(self):
    #         prod_id = prod_obj.search(
    #             [('tms_category', '=', 'freight'),
    #              ('tms_default_freight' if waybill.waybill_type == 'self'
    #                 else 'tms_default_supplier_freight', ' =', 1),
    #              ('active', '=', 1)], limit=1)
    #         if not prod_id:
    #             raise Warning(
    #                 _('Missing configuration !'),
    #                 _('There is no product defined as Default Freight !!!'))
    #         product = prod_obj.browse(prod_id, context=None)

    #         for line in waybill.waybill_line:
    #             if line.control:
    #                 line_obj.unlink([line.id])
    #         result = factor.calculate('waybill', 'client', False)
    #         # print result
    #         fpos = waybill.partner_id.property_account_position.id or False
    #         # print "fpos: ", fpos
    #         fpos = fpos and fpos_obj.browse(fpos) or False
    #         # print "fpos: ", fpos
    #         # print "product[0].taxes_id: ", product[0].taxes_id
    #         # print "fpos_obj.map_tax: ", (6, 0, [_x for _x in
    #         # fpos_obj.map_tax(cr, uid, fpos, product[0].taxes_id)]),

    #         xline = {
    #             'waybill_id': waybill.id,
    #             'line_type': 'product',
    #             'name': product[0].name,
    #             'sequence': 1,
    #             'product_id': product[0].id,
    #             'product_uom': product[0].uom_id.id,
    #             'product_uom_qty': 1,
    #             'price_unit': result,
    #             'discount': 0.0,
    #             'control': True,
    #             'tax_id': [(6, 0, [_w for _w in fpos_obj.map_tax(
    #                 fpos, product[0].taxes_id)])],
    #         }
    #         # print xline
    #         line_obj.create(xline)

    # def write(self, vals):
    #     super(TmsWaybill, self).write(self)
    #     if 'state' in vals and vals['state'] not in (
    #             'confirmed', 'cancel') or self.browse(self)[0].state in (
    #                 'draft', 'approved'):
    #         self.get_freight_from_factors(self)
    #     self.pool.get('tms.waybill.taxes').compute(self)

    # def create(self, cr, uid, vals, context=None):
    #     res = super(TmsWaybill, self).create(cr, uid, vals, context=context)
    #     self.get_freight_from_factors(cr, uid, [res], context=context)
    #    self.pool.get('tms.waybill.taxes').compute(cr, uid, waybill_ids=[res])

    # def onchange_sequence_id(self, sequence_id):
    #     if not sequence_id:
    #         return {'value': {'billing_policy': 'manual', }}
    #     result = self.pool.get('ir.sequence').browse(
    #         [sequence_id])[0].tms_waybill_automatic
    #     return {'value': {
    #         'billing_policy': 'automatic' if result else 'manual', }}

    # def onchange_travel_ids(self, travel_ids):
    #     if not travel_ids or not len(travel_ids[0][2]):
    #         return {'value': {
    #             'waybill_type': 'own',
    #             'unit_id': False,
    #             'trailer1_id': False,
    #             'dolly_id': False,
    #             'trailer2_id': False,
    #             'employee_id': False,
    #             'route_id': False,
    #             'departure_id': False,
    #             'arrival_id': False,
    #             'travel_id': False,
    #         }}
    #     travel_id = False
    #     for rec in travel_ids:
    #         travel_id = rec[2][len(rec[2]) - 1] or False

    #     for travel in self.pool.get('tms.travel').browse([travel_id]):
    #         return {'value': {
    #             'waybill_type':
    #             'outsourced' if (travel.unit_id.supplier_unit) else 'own',
    #             'unit_id': travel.unit_id.id,
    #             'trailer1_id': travel.trailer1_id.id,
    #             'dolly_id': travel.dolly_id.id,
    #             'trailer2_id': travel.trailer2_id.id,
    #             'employee_id': travel.employee_id.id,
    #             'route_id': travel.route_id.id,
    #             'departure_id': travel.route_id.departure_id.id,
    #             'arrival_id': travel.route_id.arrival_id.id,
    #             'travel_id': travel_id,
    #             'operation_id': travel.operation_id.id,
    #         }}
    #     return {'value': {'travel_id': travel_id}}

    # def onchange_partner_id(self, partner_id):
    #     if not partner_id:
    #         return {'value': {'partner_invoice_id': False,
    #                           'partner_order_id': False,
    #                           'payment_term': False,
    #                           'user_id': False}
    #                 }
    #     addr = self.pool.get('res.partner').address_get(
    #         [partner_id], ['invoice', 'contact', 'default', 'delivery'])
    #     part = self.pool.get('res.partner').browse(partner_id)
    #     payment_term = (part.property_payment_term and
    #                     part.property_payment_term.id or False)
    #     dedicated_salesman = part.user_id and part.user_id.id or self
    #     val = {
    #         'partner_invoice_id':
    #             addr['invoice'] if addr['invoice'] else addr['default'],
    #         'partner_order_id':
    #             addr['contact'] if addr['contact'] else addr['default'],
    #         'payment_term': payment_term,
    #         'user_id': dedicated_salesman,
    #     }
    #     return {'value': val}

    # def copy(self, cr, uid, id, default=None, context=None):
    #     default = default or {}
    #     default.update({
    #         'name': False,
    #         'state': 'draft',
    #         'invoice_id': False,
    #         'cancelled_by': False,
    #         'date_cancelled': False,
    #         'approved_by': False,
    #         'date_approved': False,
    #         'confirmed_by': False,
    #         'date_confirmed': False,
    #         'drafted_by': False,
    #         'date_drafted': False,
    #         'replaced_waybill_id': False,
    #         'move_id': False,
    #         'user_id': uid,
    #     })

    #     return super(TmsWaybill, self).copy(cr, uid, id, default, context)

    # def action_cancel_draft(self, *args):
    #     if not len(self):
    #         return False

    #     for waybill in self.browse(self):
    #         if (waybill.travel_id.id) and waybill.travel_id.state in (
    #                 'cancel'):
    #             raise Warning(
    #                 _('Could not set to draft this Waybill !'),
    #                 _('Travel is Cancelled !!!'))
    #         else:
    #             self.write({
    #                 'state': 'draft',
    #                 'drafted_by': self,
    #                 'date_drafted':
    #                 time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
    #     return True

    # def action_approve(self):
    #     print "action_approve"
    #     for waybill in self.browse(self):
    #         if waybill.state in ('draft'):
    #             if not waybill.sequence_id.id:
    #                 raise Warning(
    #                     'Could not Approve Waybill !',
    #                     'You have not selected a valid Waybill Sequence')
    #             elif not waybill.name:
    #                 seq_id = waybill.sequence_id.id
    #                 seq_number = self.pool.get('ir.sequence').get_id(seq_id)
    #             else:
    #                 seq_number = waybill.name

    #             self.write({
    #                 'name': seq_number,
    #                 'state': 'approved',
    #                 'approved_by': self,
    #                 'date_approved':
    #                 time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
    #     return True

    # def action_confirm(self):
    #     print "action_confirm"
    #     *******************
    #     move_obj = self.pool.get('account.move')
    #     period_obj = self.pool.get('account.period')
    #     account_jrnl_obj = self.pool.get('account.journal')
    #     cur_obj = self.pool.get('res.currency')
    #     for waybill in self.browse(self):
    #         company_currency = self.pool['res.company'].browse(
    #             waybill.company_id.id).currency_id.id
    #         if waybill.amount_untaxed <= 0.0:
    #             raise Warning(
    #                 _('Could not confirm Waybill !'),
    #                 _('Total Amount must be greater than zero.'))
    #         elif not waybill.travel_id.id:
    #             raise Warning(
    #                 _('Could not confirm Waybill !'),
    #                 _('Waybill must be assigned to a Travel before \
    #                     confirming.'))
    #         elif waybill.billing_policy == 'automatic':
    #             # print "Entrando para generar la factura en automatico..."
    #             wb_invoice = self.pool.get('tms.waybill.invoice')
    #             wb_invoice.makeWaybillInvoices(self)

    #         period_id = period_obj.search(
    #             [('date_start', '<=', waybill.date_order),
    #              ('date_stop', '>=', waybill.date_order),
    #              ('state', '=', 'draft')], context=None)

    #         if not period_id:
    #             raise Warning(
    #                 _('Warning !'),
    #                 _('There is no valid account period for this date %s. \
    #                     Period does not exists or is already closed\
    #                     ') % (waybill.date_order,))
    #         journal_id = account_jrnl_obj.search(
    #             [('type', '=', 'general'),
    #              ('tms_waybill_journal', '=', 1)], context=None)
    #         if not journal_id:
    #             raise Warning(
    #                 'Error !',
    #                 'You have not defined Waybill Journal...')
    #         journal_id = journal_id and journal_id[0]
    #         move_lines = []

    #         precision = self.pool.get('decimal.precision').precision_get(
    #             'Account')
    #         notes = _(
    #             "Waybill: %s\nTravel: %s\nDriver: (ID %s) %s\nVehicle: %s\
    #             ") % (
    #             waybill.name, waybill.travel_id.name,
    #             waybill.travel_id.employee_id.id,
    #             waybill.travel_id.employee_id.name,
    #             waybill.travel_id.unit_id.name)
    #         # #print "notes: ", notes

    #         for waybill_line in waybill.waybill_line:
    #             if not waybill_line.line_type == "product":
    #                 continue
    #             tms_prod_income_account = (
    #                 waybill_line.product_id.tms_property_account_income.id if
    #              waybill_line.product_id.tms_property_account_income.id else
    #                 (waybill_line.product_id.categ_id.
    #                  tms_property_account_income_categ.id)
    #                 if (waybill_line.product_id.categ_id.
    #                     tms_property_account_income_categ.id)
    #                 else False)
    #             prod_income_account = ((waybill_line.product_id.
    #                                     property_account_income.id)
    #                                    if (waybill_line.product_id.
    #                                        property_account_income.id) else
    #                                    (waybill_line.product_id.categ_id.
    #                                     property_account_income_categ.id) if
    #                                    (waybill_line.product_id.categ_id.
    #                                     property_account_income_categ.id)
    #                                    else False)

    #             if not (tms_prod_income_account & prod_income_account):
    #                 raise Warning(
    #                     'Error !',
    #                 _('You have not defined Income Account for product %s\
    #                         ') % (waybill_line.product_id.name))
    #             xsubtotal = cur_obj.compute(
    #                 waybill.currency_id.id, company_currency,
    #                 waybill_line.price_subtotal,
    #                 context={'date': waybill.date_order})
    #             move_line = (0, 0, {
    #                 'name': _('Waybill: %s - Product: %s') % (
    #                     waybill.name, waybill_line.name),
    #                 'account_id': tms_prod_income_account,
    #                 'debit': 0.0,
    #                 'credit': round(xsubtotal, precision),
    #                 'journal_id': journal_id,
    #                 'period_id': period_id[0],
    #                 'product_id': waybill_line.product_id.id,
    #                 'sale_shop_id': waybill.travel_id.shop_id.id,
    #                 'vehicle_id': waybill.travel_id.unit_id.id,
    #                 'employee_id': waybill.travel_id.employee_id.id,
    #                 'currency_id': (
    #                     waybill.currency_id.id != company_currency and
    #                     waybill.currency_id.id or False),
    #                 'amount_currency': (
    #                     waybill.currency_id.id != company_currency and
    #                     (waybill_line.price_subtotal * -1.0) or False),
    #             })
    #             move_lines.append(move_line)
    #             move_line = (0, 0, {
    #                 'name': _('Waybill: %s - Product: %s') % (
    #                     waybill.name, waybill_line.name),
    #                 'account_id': prod_income_account,
    #                 'debit': round(xsubtotal, precision),
    #                 'credit': 0.0,
    #                 'journal_id': journal_id,
    #                 'period_id': period_id[0],
    #                 'sale_shop_id': waybill.travel_id.shop_id.id,
    #                 'vehicle_id': waybill.travel_id.unit_id.id,
    #                 'employee_id': waybill.travel_id.employee_id.id,
    #                 'currency_id': (
    #                     waybill.currency_id.id != company_currency and
    #                     waybill.currency_id.id or False),
    #                 'amount_currency': (
    #                     waybill.currency_id.id != company_currency and
    #                     waybill_line.price_subtotal or False),
    #             })
    #             move_lines.append(move_line)

    #         move = {
    #             'ref': _('Waybill: %s') % (waybill.name),
    #             'journal_id': journal_id,
    #             'narration': notes,
    #             'line_id': [x for x in move_lines],
    #             'date': waybill.date_order,
    #             'period_id': period_id[0],
    #         }
    #         move_id = move_obj.create(move)
    #         if move_id:
    #             move_obj.button_validate([move_id])
    #         self.write({
    #             'move_id': move_id,
    #             'state': 'confirmed',
    #             'confirmed_by': self,
    #             'date_confirmed':
    #             time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
    #     return True

#    def copy(self, cr, uid, id, default=None, context=None):
#        if not default:
#            default = {}
#        default.update({
#                        'name'         : False,
#                        'state'            : 'draft',
#                        'invoice_id'   : False,
#                        'cancelled_by'  : False,
#                        'date_cancelled': False,
#                        'approved_by'   : False,
#                        'date_approved' : False,
#                        'confirmed_by'  : False,
#                        'date_confirmed': False,
#                        'drafted_by'    : False,
#                        'date_drafted'  : False,
#                       })
#        return super(tms_waybill, self).copy(cr, uid, id, default,
#        context=context)
