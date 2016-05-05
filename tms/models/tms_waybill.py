# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from openerp import fields, models
# import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TmsWaybill(models.Model):
    _name = 'tms.waybill'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Waybills'

    # def _amount_all(self):
    #     cur_obj = self.env['res.currency']
    #     for waybill in self.browse(self):
    #         cur = waybill.currency_id
    #         x_freight = 0.0
    #         x_move = 0.0
    #         x_highway = 0.0
    #         x_insurance = 0.0
    #         x_other = 0.0
    #         x_subtotal = 0.0
    #         x_tax = 0.0
    #         x_total = 0.0
    #         for line in waybill.waybill_line:
    #             if line.product_id.tms_category == 'freight':
    #                 x_freight += line.price_subtotal
    #             else:
    #                 x_freight += 0.0
    #             if line.product_id.tms_category == 'move':
    #                 x_move += line.price_subtotal
    #             else:
    #                 x_move += 0.0
    #             if line.product_id.tms_category == 'highway_tolls':
    #                 x_highway += line.price_subtotal
    #             else:
    #                 x_highway += 0.0
    #             if line.product_id.tms_category == 'insurance':
    #                 x_insurance += line.price_subtotal
    #             else:
    #                 x_insurance += 0.0
    #             if line.product_id.tms_category == 'other':
    #                 x_other += line.price_subtotal
    #             else:
    #                 x_other += 0.0
    #             x_subtotal += line.price_subtotal
    #             x_tax += line.tax_amount
    #             x_total += line.price_total

    #             self.amount_freight = cur_obj.round(cur, x_freight),
    #             self.amount_move = cur_obj.round(cur, x_move),
    #             self.amount_highway_tolls = cur_obj.round(cur, x_highway),
    #             self.amount_insurance = cur_obj.round(cur, x_insurance),
    #             self.amount_other = cur_obj.round(cur, x_other),
    #             self.amount_untaxed = cur_obj.round(cur, x_subtotal),
    #             self.amount_tax = cur_obj.round(cur, x_tax),
    #             self.amount_total = cur_obj.round(cur, x_total),

    state = fields.Selection(
        [('draft', 'Draft'),
         ('approved', 'Approved'),
         ('confirmed', 'Confirmed'),
         ('closed', 'Closed'),
         ('cancel', 'Cancelled')],
        string='State', readonly=True, default='draft')
    date_order = fields.Date(
        'Date', required=True, select=True, readonly=False,
        states={'confirmed': [('readonly', True)]},
        default=(lambda * a: time.strftime(DEFAULT_SERVER_DATE_FORMAT)))
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        # states={'confirmed': [('readonly', True)]},
        default=lambda self: self.env['res.users'].company_id.currency_id.id)
    sequence_id = fields.Many2one(
        'ir.sequence', 'Sequence', required=True,
        readonly=False,
        # states={'confirmed': [('readonly', True)]}
    )
    partner_id = fields.Many2one(
        'res.partner', 'Customer', required=True, change_default=True,
        select=True, readonly=False,
        # states={'confirmed': [('readonly', True)]}
    )
    partner_order_id = fields.Many2one(
        'res.partner', 'Ordering Contact', required=True,
        help="The name and address of the contact who requested the order \
        or quotation.", readonly=False,
        # states={'confirmed': [('readonly', True)]},
        default=(lambda self: self.env['res.partner'].address_get(
            self['partner_id'])['contact']))
    partner_invoice_id = fields.Many2one(
        'res.partner', 'Invoice Address', required=True,
        help="Invoice address for current Waybill.", readonly=False,
        # states={'confirmed': [('readonly', True)]},
        default=(lambda self: self.env[
            'res.partner'].address_get(
            self['partner_id'])))
    upload_point = fields.Char(
        'Upload Point', size=128, readonly=False,
        # states={'confirmed': [('readonly', True)]}
    )
    download_point = fields.Char(
        'Download Point', size=128, required=False, readonly=False,
        # states={'confirmed': [('readonly', True)]}
    )
    # travel_ids = fields.Many2many(
    #     'tms.travel',
    #     string='Travels',
    #     states={'confirmed': [('readonly', True)]})
    # waybill_customer_factor = fields.One2many(
    #     'tms.factor', 'waybill_id',
    #     string='Waybill Customer Charge Factors',
    #     domain=[('category', '=', 'customer')],
    #     readonly=False, states={'confirmed': [('readonly', True)],
    #                             'closed': [('readonly', True)]})
    # waybill_shipped_product = fields.One2many(
    #     'tms.waybill.shipped_product', 'waybill_id',
    #     string='Shipped Products',
    #     readonly=False, states={'confirmed': [('readonly', True)]})
    # waybill_line = fields.One2many(
    #     'tms.waybill.line', 'waybill_id',
    #     string='Waybill Lines', readonly=False,
    #     states={'confirmed': [('readonly', True)]})
    # tax_line = fields.One2many(
    #     'tms.waybill.taxes', 'waybill_id',
    #     string='Tax Lines', readonly=True,
    #     states={'draft': [('readonly', False)]})
    # amount_freight = fields.Float(
    #     compute=_amount_all, method=True,
    #     digits_compute=dp.get_precision('Sale Price'),
    #     string='Freight', store=False, multi=True)
    # amount_move = fields.Float(
    #     compute=_amount_all, method=True,
    #     digits_compute=dp.get_precision('Sale Price'),
    #     string='Moves', store=False, multi=True)
    # amount_highway_tolls = fields.Float(
    #     compute=_amount_all, method=True,
    #     digits_compute=dp.get_precision('Sale Price'),
    #     string='Highway Tolls', store=False, multi=True)
    # amount_insurance = fields.Float(
    #     compute=_amount_all, method=True,
    #     digits_compute=dp.get_precision('Sale Price'),
    #     string='Insurance', store=False, multi=True)
    # amount_other = fields.Float(
    #     compute=_amount_all, method=True,
    #     digits_compute=dp.get_precision('Sale Price'),
    #     string='Other', store=False, multi=True)
    # amount_untaxed = fields.Float(
    #     compute=_amount_all, method=True,
    #     digits_compute=dp.get_precision('Sale Price'),
    #     string='SubTotal', store=False, multi=True)
    # amount_tax = fields.Float(
    #     compute=_amount_all, method=True,
    #     digits_compute=dp.get_precision('Sale Price'),
    #     string='Taxes', store=False, multi=True)
    # amount_total = fields.Float(
    #     compute=_amount_all, method=True,
    #     digits_compute=dp.get_precision('Sale Price'),
    #     string='Total', store=False, multi=True)
    date_start = fields.Datetime(
        'Load Date Sched', required=False, help="Date Start time for Load",
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_up_start_sched = fields.Datetime(
        'UpLd Start Sched', required=False,
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_up_end_sched = fields.Datetime(
        'UpLd End Sched', required=False,
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_up_docs_sched = fields.Datetime(
        'UpLd Docs Sched', required=False,
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_appoint_down_sched = fields.Datetime(
        'Download Date Sched', required=False,
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_down_start_sched = fields.Datetime(
        'Download Start Sched', required=False,
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_down_end_sched = fields.Datetime(
        'Download End Sched', required=False,
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_down_docs_sched = fields.Datetime(
        'Download Docs Sched', required=False,
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_end = fields.Datetime(
        'Travel End Sched', required=False, help="Date End time for Load",
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

    # @api.multi
    # @api.onchange('partner_id')
    # def _onchange_partner_id(self):
    #     if self.partner_id:
    #         addr = self.env['res.partner'].address_get(
    #             ['invoice', 'contact', 'default', 'delivery'])
    #         self.partner_invoice_id = (
    #             addr['invoice'] if addr['invoice'] else addr['default'])
    #         self.partner_order_id = (
    #             addr['contact'] if addr['contact'] else addr['default'])
