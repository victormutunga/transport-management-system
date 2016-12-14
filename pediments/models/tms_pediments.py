# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class TmsPediments(models.Model):
    _name = 'tms.pediments'

    customs = fields.Char()
    datetime = fields.Datetime(default=fields.Datetime.now)
    return_datetime = fields.Datetime(string="Date of Return")
    returned_datetime = fields.Datetime(string="Date of Returned")
    waybill_id = fields.Many2one('tms.waybill', string="Waybill")
