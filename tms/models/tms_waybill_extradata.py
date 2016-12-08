# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class TmsWaybillExtradata(models.Model):
    _name = "tms.waybill.extradata"
    _description = "Tms Waybill Extra Data"
    _order = "sequence"

    name = fields.Char('Name', size=30, required=True)
    notes = fields.Text('Notes')
    sequence = fields.Integer(
        'Sequence', help="Gives the sequence order when "
        "displaying this list of categories.", default=10)
    mandatory = fields.Boolean('Mandatory')
    type_extra = fields.Selection([
        ('char', 'String (250)'),
        ('text', 'Text'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('date', 'Date'),
        ('datetime', 'Datetime')],
        'Data Type',
        help="Useful to set wich field is used for extra data field",
        select=True)
    value_char = fields.Char('Value', size=250)
    value_text = fields.Text('Value')
    value_integer = fields.Integer('Value')
    value_float = fields.Float('Value', digits=(16, 4))
    value_date = fields.Date('Value')
    value_datetime = fields.Datetime('Value')
    value_extra = fields.Text('Value')
    waybill_id = fields.Many2one(
        'tms.waybill', 'Waybill',
        ondelete='cascade')

    @api.onchange('value_char', 'value_text', 'value_integer', 'value_float',
                  'value_date', 'value_datetime', 'value_extra')
    def onchange_value(self):
        values = [
            ['char', self.value_char],
            ['text', self.value_text],
            ['integer', str(self.value_integer)],
            ['float', str(self.value_float)],
            ['date', self.value_date],
            ['datetime', self.value_datetime]
        ]
        for value in values:
            if self.type_extra == value[0]:
                self.value_extra = value[1]
                return self.value_extra
