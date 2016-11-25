# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class TmsWaybill(models.Model):
    _name = 'tms.waybill'
    _inherit = 'tms.waybill'

    customs_ids = fields.One2many(
        'tms.pediments',
        'waybill_id',
        string="Customs")
