# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    usd_currency_rate = fields.Float(
        digits=(12, 6),
        help='This special field represents the usd currency rate for journal'
        ' entries that the currency rate is different that the date rate',)
