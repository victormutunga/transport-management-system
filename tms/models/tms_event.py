# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models


class TmsEvent(models.Model):
    _name = "tms.event"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Events"
    _order = "date"

    name = fields.Char(
        string='Description', required=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirm'),
         ('cancel', 'Cancel')], readonly=True, default='draft')
    date = fields.Date(
        default=fields.Date.today,
        required=True,
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    notes = fields.Text(
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    travel_id = fields.Many2one(
        'tms.travel', 'Travel', index=True, required=True, readonly=False,
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]}, ondelete='restrict')
    latitude = fields.Float(
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    longitude = fields.Float(
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    position_real = fields.Text(
        help="Position as GPS",
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    position_pi = fields.Text(
        string='Position P.I.', help="Position near a Point of Interest",
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})

    @api.multi
    def action_confirm(self):
        for rec in self:
            message = _('<b>Event Confirmed.</b></br><ul>'
                        '<li><b>Approved by: </b>%s</li>'
                        '<li><b>Approved at: </b>%s</li>'
                        '</ul>') % (self.env.user.name, fields.Date.today())
            rec.message_post(body=message)
            rec.state = 'confirm'

    @api.multi
    def action_cancel(self):
        for rec in self:
            message = _('<b>Event Cancelled.</b></br><ul>'
                        '<li><b>Cancelled by: </b>%s</li>'
                        '<li><b>Cancelled at: </b>%s</li>'
                        '</ul>') % (
                            self.env.user.name,
                            fields.Date.today())
            rec.message_post(body=message)
            rec.state = 'cancel'

    @api.multi
    def set_2_draft(self):
        for rec in self:
            message = _(
                '<b>Event Draft.</b></br><ul>'
                '<li><b>Drafted by: </b>%s</li>'
                '<li><b>Drafted at: </b>%s</li>'
                '</ul>') % (self.env.user.name, fields.Date.today())
            rec.message_post(body=message)
            rec.state = 'draft'
