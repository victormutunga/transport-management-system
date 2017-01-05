# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class TmsTollData(models.Model):
    _name = 'tms.toll.data'

    date = fields.Datetime()
    num_tag = fields.Char(string='Tag number')
    economic_number = fields.Char()
    station = fields.Char()
    import_rate = fields.Float()
    product_id = fields.Many2one(
        'product.product', string='Product', required=True,
        domain=[('tms_product_category', '=', 'tolls')])
