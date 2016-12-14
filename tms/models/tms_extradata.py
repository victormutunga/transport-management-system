# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class TmsExtradata(models.Model):
    _name = "tms.extradata"
    _description = "TMS Extra Data"

    type_id = fields.Many2one(
        'tms.extradata.type', string="Type", required="True")
    name = fields.Char(required=True)
    type = fields.Selection(related="type_id.type")
    value_char = fields.Char('Value')
    value_integer = fields.Integer('Value')
    value_float = fields.Float('Value')
    value_date = fields.Date('Value')
    value_datetime = fields.Datetime('Value')
    value_extra = fields.Text('Value')
    waybill_id = fields.Many2one(
        'tms.waybill', 'Waybill',
        ondelete='cascade')
    vehicle_id = fields.Many2one(
        'fleet.vehicle', 'Waybill',
        ondelete='cascade')

    @api.onchange('value_char', 'value_integer', 'value_float',
                  'value_date', 'value_datetime', 'value_extra')
    def onchange_value(self):
        values = [
            ['char', self.value_char],
            ['integer', str(self.value_integer)],
            ['float', str(self.value_float)],
            ['date', self.value_date],
            ['datetime', self.value_datetime]
        ]
        for value in values:
            if self.type == value[0]:
                self.value_extra = value[1]
                return self.value_extra
