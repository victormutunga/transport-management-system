# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, fields, models


class TmsWaybill(models.Model):
    _name = 'tms.waybill'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Waybills'
    _order = 'name desc'

    base_id = fields.Many2one(
        'tms.base', string='Base', required=True)
    waybill_customer_factor_id = fields.One2many(
        'tms.factor', 'waybill_id',
        string='Waybill Customer Charge Factors')
    waybill_supplier_factor_id = fields.One2many(
        'tms.factor', 'waybill_id',
        string='Waybill Supplier Payment Factors')
    expense_driver_factor_id = fields.One2many(
        'tms.factor', 'waybill_id',
        string='Travel Driver Payment Factors')
    tax_line = fields.One2many(
        'tms.waybill.taxes', 'waybill_id',
        string='Tax Lines', readonly=True)
    name = fields.Char()
    travel_ids = fields.Many2many(
        'tms.travel',
        string='Travels')
    route_id = fields.Many2one(
        'tms.route',
        related='travel_ids.route_id',
        string='Route',
        readonly=True)
    departure_id = fields.Many2one(
        'tms.place',
        related='route_id.departure_id',
        string='Departure',
        readonly=True)
    arrival_id = fields.Many2one(
        'tms.place',
        related='route_id.arrival_id',
        string='Arrival',
        readonly=True)
    origin = fields.Char(
        'Source Document',
        help="Reference of the document that generated this Waybill request.")
    client_order_ref = fields.Char(
        'Customer Reference')
    state = fields.Selection([
        ('draft', 'Pending'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled')], 'State', readonly=True,
        help="Gives the state of the Waybill. \n",
        default='draft')
    date_order = fields.Date(
        'Date', required=True,
        default=fields.Date.today)
    user_id = fields.Many2one(
        'res.users', 'Salesman',
        default=(lambda self: self))
    partner_id = fields.Many2one(
        'res.partner',
        'Customer', required=True, change_default=True)
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    partner_invoice_id = fields.Many2one(
        'res.partner', 'Invoice Address', required=True,
        help="Invoice address for current Waybill.",
        default=(lambda self: self.env[
            'res.partner'].address_get(
            self['partner_id'])))
    partner_order_id = fields.Many2one(
        'res.partner', 'Ordering Contact', required=True,
        help="The name and address of the contact who requested the "
        "order or quotation.",
        default=(lambda self: self.env['res.partner'].address_get(
            self['partner_id'])['contact']))
    account_analytic_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account',
        help="The analytic account related to a Waybill.")
    departure_address_id = fields.Many2one(
        'res.partner', 'Departure Address', required=True,
        help="Departure address for current Waybill.",
        default=(lambda self: self.env['res.partner'].address_get(
            self['partner_id'])))
    arrival_address_id = fields.Many2one(
        'res.partner', 'Arrival Address', required=True,
        help="Arrival address for current Waybill.",
        default=(lambda self: self.env['res.partner'].address_get(
            self['partner_id'])))
    upload_point = fields.Char(
        'Upload Point')
    download_point = fields.Char(
        'Download Point')
    shipped = fields.Boolean(
        'Delivered', readonly=True,
        help="It indicates that the Waybill has been delivered. This field "
        "is updated only after the scheduler(s) have been launched.")
    invoice_id = fields.Many2one(
        'account.invoice', 'Invoice Record', readonly=True)
    invoiced = fields.Boolean(
        # compute=_invoiced,
        )
    invoice_paid = fields.Boolean(
        # compute=_invoiced,
        )
    supplier_invoice_id = fields.Many2one(
        'account.invoice', 'Supplier Invoice Rec', readonly=True)
    supplier_invoiced = fields.Boolean(
        # compute=_supplier_invoiced,
        string='Supplier Invoiced',
        )
    supplier_invoice_paid = fields.Boolean(
        # compute=_supplier_invoiced,
        string='Supplier Invoice Paid',
        )
    waybill_line = fields.One2many(
        'tms.waybill.line', 'waybill_id',
        string='Waybill Lines')
    transportable_ids = fields.One2many(
        'tms.waybill.transportable.line', 'transportable_id',
        string='Shipped Products')
    product_qty = fields.Float(
        # compute=_shipped_product,
        string='Sum Qty')
    product_volume = fields.Float(
        # compute=_shipped_product,
        string='Sum Volume')
    product_weight = fields.Float(
        # compute=_shipped_product,
        string='Sum Weight')
    product_uom_type = fields.Char(
        # compute=_shipped_product,
        string='Product UoM Type')
    amount_freight = fields.Float(
        # compute=_amount_all,
        string='Freight')
    amount_move = fields.Float(
        # compute=_amount_all,
        string='Moves')
    amount_highway_tolls = fields.Float(
        # compute=_amount_all,
        string='Highway Tolls')
    amount_insurance = fields.Float(
        # compute=_amount_all,
        string='Insurance')
    amount_other = fields.Float(
        # compute=_amount_all,
        string='Other')
    amount_untaxed = fields.Float(
        # compute=_amount_all,
        string='SubTotal')
    amount_tax = fields.Float(
        # compute=_amount_all,
        string='Taxes')
    amount_total = fields.Float(
        # compute=_amount_all,
        string='Total')
    distance_route = fields.Float(
        # compute=_get_route_distance,
        string='Distance from route',
        help="Route Distance.")
    distance_real = fields.Float(
        'Distance Real',
        help="Route obtained by electronic reading")
    notes = fields.Text()
    payment_term = fields.Many2one(
        'account.payment.term', 'Payment Term')
    fiscal_position = fields.Many2one(
        'account.fiscal.position', 'Fiscal Position')
    time_for_uploading_std = fields.Float(
        'Std Time for loading (Hrs)')
    time_from_uploading_to_docs_sched = fields.Float(
        'Std Time fromLoad to Document Release (Hrs)')
    time_travel_sched = fields.Float(
        'Std Time for Travel (Hrs)')
    time_from_appointment_to_downloading_std = fields.Float(
        'StdTime from Download Appointment to Downloading (Hrs)')
    time_for_downloading_sched = fields.Float(
        'Std Time for downloading(Hrs)')
    time_from_downloading_to_docs_sched = fields.Float(
        'Std Time for Download Document Release (Hrs)',
        readonly=False)
    date_start = fields.Datetime(
        'Load Date Sched', help="Date Start time for Load",
        default=fields.Datetime.now)
    date_up_start_sched = fields.Datetime(
        'UpLd Start Sched',
        default=fields.Datetime.now)
    date_up_end_sched = fields.Datetime(
        'UpLd End Sched',
        default=fields.Datetime.now)
    date_up_docs_sched = fields.Datetime(
        'UpLd Docs Sched',
        default=fields.Datetime.now)
    date_appoint_down_sched = fields.Datetime(
        'Download Date Sched',
        default=fields.Datetime.now)
    date_down_start_sched = fields.Datetime(
        'Download Start Sched',
        default=fields.Datetime.now)
    date_down_end_sched = fields.Datetime(
        'Download End Sched',
        default=fields.Datetime.now)
    date_down_docs_sched = fields.Datetime(
        'Download Docs Sched',
        default=fields.Datetime.now)
    date_end = fields.Datetime(
        'Travel End Sched', help="Date End time for Load",
        default=fields.Datetime.now)
    date_start_real = fields.Datetime('Load Date Real')
    date_up_start_real = fields.Datetime('UpLoad Start Real')
    date_up_end_real = fields.Datetime('UpLoad End Real')
    date_up_docs_real = fields.Datetime('Load Docs Real')
    date_appoint_down_real = fields.Datetime('Download Date Real')
    date_down_start_real = fields.Datetime('Download Start Real')
    date_down_end_real = fields.Datetime('Download End Real')
    date_down_docs_real = fields.Datetime('Download Docs Real')
    date_end_real = fields.Datetime('Travel End Real')
    amount_declared = fields.Float(
        'Amount Declared',
        help=" Load value amount declared for insurance purposes...")
    replaced_waybill_id = fields.Many2one(
        'tms.waybill', 'Replaced Waybill', readonly=True)
    move_id = fields.Many2one(
        'account.move', 'Account Move', readonly=True)

    @api.model
    def create(self, values):
        waybill = super(TmsWaybill, self).create(values)
        sequence = waybill.base_id.waybill_sequence_id
        waybill.name = sequence.next_by_id()
        return waybill
