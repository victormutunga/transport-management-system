# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, exceptions, fields, models


class TmsWaybill(models.Model):
    _name = 'tms.waybill'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Waybills'
    _order = 'name desc'

    base_id = fields.Many2one(
        'tms.base', string='Base', required=True)
    customer_factor_ids = fields.One2many(
        'tms.factor', 'waybill_id',
        string='Waybill Customer Charge Factors',
        domain=[('category', '=', 'customer'), ])
    supplier_factor_ids = fields.One2many(
        'tms.factor', 'waybill_id',
        string='Waybill Supplier Payment Factors',
        domain=[('category', '=', 'supplier'), ])
    driver_factor_ids = fields.One2many(
        'tms.factor', 'waybill_id',
        string='Travel Driver Payment Factors',
        domain=[('category', '=', 'driver'), ])
    transportable_line_ids = fields.One2many(
        'tms.waybill.transportable.line', 'waybill_id', string="Transportable"
    )
    tax_line_ids = fields.One2many(
        'tms.waybill.taxes', 'waybill_id',
        string='Tax Lines', store=True)
    name = fields.Char()
    travel_ids = fields.Many2many(
        'tms.travel',
        string='Travels')
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
        help="Gives the state of the Waybill.",
        default='draft')
    date_order = fields.Date(
        'Date', required=True,
        default=fields.Date.today)
    user_id = fields.Many2one(
        'res.users', 'Salesman',
        default=(lambda self: self.env.user))
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
    departure_address_id = fields.Many2one(
        'res.partner', 'Departure Address', required=True,
        help="Departure address for current Waybill.", change_default=True)
    arrival_address_id = fields.Many2one(
        'res.partner', 'Arrival Address', required=True,
        help="Arrival address for current Waybill.", change_default=True)
    upload_point = fields.Char('Upload Point', change_default=True)
    download_point = fields.Char('Download Point', change_default=True)
    invoice_id = fields.Many2one(
        'account.invoice', 'Invoice', readonly=True)
    invoice_paid = fields.Boolean(
        compute="_compute_invoice_paid"
        )
    supplier_invoice_id = fields.Many2one(
        'account.invoice', 'Supplier Invoice', readonly=True)
    supplier_invoice_paid = fields.Boolean(
        compute='_compute_supplier_invoice_paid',
        string='Supplier Invoice Paid',
        )
    waybill_line_ids = fields.One2many(
        'tms.waybill.line', 'waybill_id',
        string='Waybill Lines')
    transportable_ids = fields.One2many(
        'tms.waybill.transportable.line', 'waybill_id',
        string='Shipped Products')
    product_qty = fields.Float(
        compute='_transportable_product',
        string='Sum Qty')
    product_volume = fields.Float(
        compute='_transportable_product',
        string='Sum Volume')
    product_weight = fields.Float(
        compute='_transportable_product',
        string='Sum Weight')
    amount_freight = fields.Float(
        compute='_amount_all',
        string='Freight')
    amount_move = fields.Float(
        compute='_amount_all',
        string='Moves')
    amount_highway_tolls = fields.Float(
        compute='_amount_all',
        string='Highway Tolls')
    amount_insurance = fields.Float(
        compute='_amount_all',
        string='Insurance')
    amount_other = fields.Float(
        compute='_amount_all',
        string='Other')
    amount_untaxed = fields.Float(
        compute='_amount_all',
        string='SubTotal')
    amount_tax = fields.Float(
        compute='_amount_all',
        string='Taxes')
    amount_total = fields.Float(
        compute='_amount_all',
        string='Total')
    distance_route = fields.Float(
        compute='_get_route_distance',
        string='Distance from route',
        help="Route Distance.")
    distance_real = fields.Float(
        'Distance Real',
        help="Route obtained by electronic reading")
    notes = fields.Text()
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
        products = [
            [waybill.base_id.waybill_other_product_id,
             waybill.base_id.account_other_id],
            [waybill.base_id.waybill_insurance_id,
             waybill.base_id.account_insurance_id],
            [waybill.base_id.waybill_highway_tolls_id,
             waybill.base_id.account_highway_tolls_id],
            [waybill.base_id.waybill_moves_id,
             waybill.base_id.account_moves_id],
            [waybill.base_id.waybill_freight_id,
             waybill.base_id.account_freight_id]
        ]
        for product in products:
            self.waybill_line_ids.create({
                'name': product[0][0].name,
                'waybill_id': waybill.id,
                'product_id': product[0][0].id,
                'tax_ids': [(
                    6, 0, [x.id for x in (
                        product[0][0].supplier_taxes_id)]
                )],
                'account_id': product[1][0].id,
            })
        waybill._transportable_product()
        waybill.onchange_waybill_line_ids()

        return waybill

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        default['travel_ids'] = False
        return super(TmsWaybill, self).copy(default)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.partner_order_id = self.partner_id.address_get(
                ['invoice', 'contact']).get('contact', False)
            self.partner_invoice_id = self.partner_id.address_get(
                ['invoice', 'contact']).get('invoice', False)

    @api.multi
    def action_approve(self):
        for waybill in self:
            waybill.state = 'approved'
            self.message_post(body=_(
                "<h5><strong>Aprroved</strong></h5>"
                "<p><strong>Approved by: </strong> %s <br>"
                "<strong>Approved at: </strong> %s</p") % (
                self.user_id.name, fields.Datetime.now()))
        return True

    @api.multi
    @api.depends('invoice_id')
    def _compute_invoice_paid(self):
        for rec in self:
            paid = (rec.invoice_id and rec.invoice_id.state == 'paid')
            rec.invoice_paid = paid

    @api.multi
    @api.onchange(
        'transportable_line_ids', 'customer_factor_ids')
    def _transportable_product(self):
        for waybill in self:
            volume = weight = qty = distance_real = distance_route = 0.0
            for record in waybill.transportable_line_ids:
                total = 0.0
                for factor in waybill.customer_factor_ids:
                    qty = record.quantity
                    if (record.transportable_uom_id.category_id.name ==
                            'Volume'):
                        volume += record.quantity
                    elif (record.transportable_uom_id.category_id.name ==
                            'Weight'):
                        weight += record.quantity
                    elif (record.transportable_uom_id.category_id.name ==
                            'Length / Distance'):
                        if factor.factor_type == 'distance':
                            distance_route += record.quantity
                        else:
                            distance_real += record.quantity

                    waybill.product_qty = qty
                    waybill.product_volume = volume
                    waybill.product_weight = weight
                    waybill.distance_route = distance_route
                    waybill.distance_real = distance_real
                    total_get_amount = waybill.customer_factor_ids.get_amount(
                        waybill.product_weight, waybill.distance_route,
                        waybill.distance_real, waybill.product_qty,
                        waybill.product_volume, waybill.amount_total)
                    total = total + total_get_amount
                    for product in waybill.waybill_line_ids:
                        if (product.product_id.name ==
                                waybill.base_id.waybill_freight_id.name):
                            product.update({'unit_price': total})

    @api.depends('waybill_line_ids')
    @api.multi
    def _amount_all(self):
        for waybill in self:
            for line in waybill.waybill_line_ids:
                if line.product_id.id == waybill.base_id.waybill_freight_id.id:
                    waybill.amount_freight += line.price_subtotal
                elif line.product_id.id == waybill.base_id.waybill_moves_id.id:
                    waybill.amount_move += line.price_subtotal
                elif (line.product_id.id ==
                        waybill.base_id.waybill_highway_tolls_id.id):
                    waybill.amount_highway_tolls += line.price_subtotal
                elif (line.product_id.id ==
                        waybill.base_id.waybill_insurance_id.id):
                    waybill.amount_insurance += line.price_subtotal
                elif (line.product_id.id ==
                        waybill.base_id.waybill_other_product_id.id):
                    waybill.amount_other += line.price_subtotal
                waybill.amount_untaxed += line.price_subtotal
                waybill.amount_tax += line.tax_amount
            waybill.amount_total = waybill.amount_untaxed + waybill.amount_tax

    @api.multi
    def action_confirm(self):
        for waybill in self:
            if waybill.amount_untaxed <= 0.0:
                raise exceptions.ValidationError(
                    _('Could not confirm Waybill !\n'
                      'Total Amount must be greater than zero.'))
            elif not waybill.travel_ids:
                raise exceptions.ValidationError(
                    _('Could not confirm Waybill !\n'
                      'Waybill must be assigned to a Travel before '
                      'confirming.'))
            waybill_journal_id = waybill.base_id.waybill_journal_id.id
            if not waybill_journal_id:
                    raise exceptions.ValidationError(
                        _('You have not defined Waybill Journal...'))
            move_obj = self.env['account.move']
            freight = waybill.base_id.waybill_freight_id
            moves = waybill.base_id.waybill_moves_id
            highway = waybill.base_id.waybill_highway_tolls_id
            insurance = waybill.base_id.waybill_insurance_id
            other = waybill.base_id.waybill_other_product_id
            base = waybill.base_id
            move_lines = []
            for waybill_line in waybill.waybill_line_ids:
                product = waybill_line.product_id
                if product == freight:
                    waybill_debit_account_id = (
                        freight.property_account_income_id.id if
                        freight.property_account_income_id else
                        freight.categ_id.property_account_income_categ_id.id)
                    waybill_credit_account_id = base.account_freight_id.id
                elif product == moves:
                    waybill_debit_account_id = (
                        moves.property_account_income_id.id if
                        moves.property_account_income_id else
                        moves.categ_id.property_account_income_categ_id.id)
                    waybill_credit_account_id = base.account_moves_id.id
                elif product == highway:
                    waybill_debit_account_id = (
                        highway.property_account_income_id.id if
                        highway.property_account_income_id else
                        highway.categ_id.property_account_income_categ_id.id)
                    waybill_credit_account_id = (
                        base.account_highway_tolls_id.id)
                elif product == insurance:
                    waybill_debit_account_id = (
                        insurance.property_account_income_id.id if
                        insurance.property_account_income_id else
                        insurance.categ_id.property_account_income_categ_id.id)
                    waybill_credit_account_id = base.account_insurance_id.id
                elif product == other:
                    waybill_debit_account_id = (
                        other.property_account_income_id.id if
                        other.property_account_income_id else
                        other.categ_id.property_account_income_categ_id.id)
                    waybill_credit_account_id = base.account_other_id.id
                if not (
                    waybill_credit_account_id and
                        waybill_debit_account_id):
                    raise exceptions.ValidationError(
                        _('Check if you already set the journal / product '
                          'in the base and the account of the driver.'))

                notes = _(
                    '* Waybill: %s \n'
                    '* Travel: %s \n'
                    '* Driver: %s \n'
                    '* Vehicle: %s') % (
                    waybill.name,
                    waybill.travel_ids.name,
                    waybill.travel_ids.employee_id.name,
                    waybill.travel_ids.unit_id.name)
                xsubtotal = waybill.currency_id.compute(
                    waybill_line.price_subtotal,
                    waybill.currency_id,
                    )
                if xsubtotal > 0.0:
                    move_line = (
                        0, 0,
                        {
                            'name': waybill.name,
                            'account_id': waybill_credit_account_id,
                            'narration': notes,
                            'debit': 0.0,
                            'credit': xsubtotal,
                            'journal_id': waybill_journal_id,
                            'partner_id': self.env.user.company_id.id,
                        })
                    move_lines.append(move_line)
                    move_line = (
                        0, 0,
                        {
                            'name': waybill.name,
                            'account_id': waybill_debit_account_id,
                            'narration': notes,
                            'debit': xsubtotal,
                            'credit': 0.0,
                            'journal_id': waybill_journal_id,
                            'partner_id': self.env.user.company_id.id,
                        })
                    move_lines.append(move_line)

            move = {
                'date': fields.Date.today(),
                'journal_id': waybill_journal_id,
                'name': _('Waybill: %s') % (waybill.name),
                'line_ids': [line for line in move_lines],
            }
            move_id = move_obj.create(move)
            if not move_id:
                raise exceptions.ValidationError(
                    _('An error has occurred in the creation'
                        ' of the accounting move. '))
            else:
                self.write(
                    {
                        'move_id': move_id.id,
                        'state': 'confirmed'
                    })
                self.message_post(body=_(
                    "<h5><strong>Confirmed</strong></h5>"
                    "<p><strong>Confirmed by: </strong> %s <br>"
                    "<strong>Confirmed at: </strong> %s</p") % (
                    self.user_id.name, fields.Datetime.now()))

    @api.onchange('waybill_line_ids')
    def onchange_waybill_line_ids(self):
        for waybill in self:
            tax_grouped = {}
            for line in waybill.waybill_line_ids:
                unit_price = (
                    line.unit_price * (1-(line.discount or 0.0) / 100.0))
                taxes = line.tax_ids.compute_all(
                    unit_price, waybill.currency_id, line.product_qty,
                    line.product_id, waybill.partner_id)
                for tax in taxes['taxes']:
                    val = {
                        'tax_id': tax['id'], 'base': taxes['base'],
                        'tax_amount': tax['amount']}
                    key = waybill.env['account.tax'].browse(tax['id']).id
                    if key not in tax_grouped:
                        tax_grouped[key] = val
                    else:
                        tax_grouped[key]['tax_amount'] += val['tax_amount']
                        tax_grouped[key]['base'] += val['base']
            tax_lines = waybill.tax_line_ids.browse([])
            for tax in tax_grouped.values():
                tax_lines += tax_lines.new(tax)
            waybill.tax_line_ids = tax_lines

    @api.multi
    def action_cancel_draft(self):
        for waybill in self:
            for travel in waybill.travel_ids:
                if travel.state == 'cancel':
                    raise exceptions.ValidationError(
                        _('Could not set to draft this Waybill !\n'
                          'Travel is Cancelled !!!'))
            waybill.message_post(body=_(
                "<h5><strong>Cancel to Draft</strong></h5>"
                "<p><strong>by: </strong> %s <br>"
                "<strong>at: </strong> %s</p") % (
                waybill.user_id.name, fields.Datetime.now()))
            waybill.state = 'draft'

    @api.multi
    def action_cancel(self):
        for waybill in self:
            for travel in waybill.travel_ids:
                if travel.state == 'done':
                    raise exceptions.ValidationError(
                        _('Could not cancel this waybill because'
                          'the waybill is already linked to a travel.'))
            if waybill.paid:
                raise exceptions.ValidationError(
                    _('Could not cancel this waybill because'
                      'the waybill is already paid.'))
            else:
                move_obj = self.env['account.move']
                move_id = (move_obj.search(
                    [('id', '=', waybill.move_id.id)]))
                move_count = len(move_id)

                if move_count > 0:
                    move_id.unlink()

                waybill.state = 'cancel'
                waybill.message_post(body=_(
                    "<h5><strong>Cancelled</strong></h5>"
                    "<p><strong>Cancelled by: </strong> %s <br>"
                    "<strong>Cancelled at: </strong> %s</p") % (
                    waybill.user_id.name, fields.Datetime.now()))

    @api.depends('supplier_invoice_id')
    def _compute_supplier_invoice_paid(self):
        for rec in self:
            paid = (rec.invoice_id and rec.invoice_id.state == 'paid')
            self.supplier_invoice_paid = paid
