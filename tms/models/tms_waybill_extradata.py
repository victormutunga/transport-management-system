# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import date, datetime

from openerp import fields, models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

from pytz import timezone


# Extra data fields for Waybills & Negotiations
class TmsWaybillExtradata(models.Model):
    _name = "tms.waybill.extradata"
    _description = "Tms Waybill Extra Data"

    name = fields.Char('Name', size=30, required=True)
    notes = fields.Text('Notes')
    sequence = fields.Integer(
        'Sequence', help="Gives the sequence order when \
        displaying this list of categories.", default=10)
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
        'tms.waybill', 'Waybill', required=False,
        ondelete='cascade')
    # , select=True, readonly=True)
# 'agreement_id': fields.many2one('tms.agreement', 'Agreement',
# required=False, ondelete='cascade', select=True, readonly=True),

    _order = "sequence"

    def on_change_value(self, type_extra, value):
        if not type_extra and not value:
            return {}
        if type_extra == 'char' or type_extra == 'text':
            return {'value': {'value_extra': value}}
        elif type_extra == 'integer' or type_extra == 'float':
            return {'value': {'value_extra': str(value)}}
        elif type_extra == 'date':
            xdate = filter(None, map(lambda x: int(x), value.split('-')))
            return {'value': {'value_extra': date(
                xdate[0], xdate[1],
                xdate[2]).strftime(DEFAULT_SERVER_DATE_FORMAT)}}
        elif type_extra == 'datetime':
            # print "value: ", value
            xvalue = value.split(' ')
            xdate = filter(None, map(lambda x: int(x), xvalue[0].split('-')))
            xtime = map(lambda x: int(x), xvalue[1].split(':'))

            tzone = timezone(self.pool.get('res.users').browse(self).tz)
            value = tzone.localize(datetime(
                xdate[0], xdate[1], xdate[2],
                xtime[0], xtime[1], xtime[2]))

            # print value
            xvalue = value.split(' ')
            xdate = filter(None, map(lambda x: int(x), xvalue[0].split('-')))
            xtime = map(lambda x: int(x), xvalue[1].split(':'))
            return {'value': {'value_extra': datetime(
                xdate[0], xdate[1], xdate[2], xtime[0],
                xtime[1], xtime[2]).strftime(DEFAULT_SERVER_DATETIME_FORMAT)}}
        return False

TmsWaybillExtradata()
