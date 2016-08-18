# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError


class TmsFactor(models.Model):
    _name = "tms.factor"
    _description = "Factors to calculate Payment (Driver/Supplier) "
    "& Client charge"

    name = fields.Char('Name', size=64, required=True)
    route_id = fields.Many2one('tms.route', string="Route")
    travel_id = fields.Many2one('tms.travel', string='Travel')
    waybill_id = fields.Many2one(
        'tms.waybill', string='waybill', ondelete='cascade',
        select=True, readonly=True)
    category = fields.Selection([
        ('driver', 'Driver'),
        ('customer', 'Customer'),
        ('supplier', 'Supplier')], 'Type', required=True)
    factor_type = fields.Selection([
        ('distance', 'Distance Route (Km/Mi)'),
        ('distance_real', 'Distance Real (Km/Mi)'),
        ('weight', 'Weight'),
        ('travel', 'Travel'),
        ('qty', 'Quantity'),
        ('volume', 'Volume'),
        ('percent', 'Income Percent')], 'Factor Type', required=True, help="""
For next options you have to type Ranges or Fixed Amount
 - Distance Route (Km/mi)
 - Distance Real (Km/Mi)
 - Weight
 - Quantity
 - Volume
For next option you only have to type Fixed Amount:
 - Travel
For next option you only have to type Factor like 10.5 for 10.50%:
 - Income Percent
                        """)
    range_start = fields.Float('Range Start', digits=(16, 4))
    range_end = fields.Float('Range End', digits=(16, 4))
    factor = fields.Float('Factor', digits=(16, 4))
    fixed_amount = fields.Float('Fixed Amount', digits=(16, 4))
    mixed = fields.Boolean('Mixed', default=False)
    sequence = fields.Integer(
        'Sequence', help="Gives the sequence calculation for these factors.",
        default=10)
    notes = fields.Text('Notes')

    _order = "sequence"

    @api.onchange('factor_type')
    def _onchange_factor_type(self):
        values = {
            'distance': _('Distance Route (Km/Mi)'),
            'distance_real': _('Distance Real (Km/Mi)'),
            'weight': _('Weight'),
            'travel': _('Travel'),
            'qty': _('Quantity'),
            'volume': _('Volume'),
            'percent': _('Income Percent'),
        }
        if not self.factor_type:
            self.name = 'name'
        else:
            self.name = values[self.factor_type]

    @api.multi
    def get_amount(self, weight=0.0, distance=0.0, distance_real=0.0, qty=0.0,
                   volume=0.0, income=0.0):
        factor_list = {
            'weight': weight,
            'distance': distance,
            'distance_real': distance_real,
            'qty': qty,
            'volume': volume
        }
        res = 0.0
        for rec in self:
            if rec.factor_type == 'travel':
                res += rec.fixed_amount
            elif rec.factor_type == 'percent':
                amount = income * (rec.factor / 100)
                if rec.mixed:
                    res += amount + rec.fixed_amount
                else:
                    res += amount
            for key, value in factor_list.items():
                if rec.factor_type == key:
                    if rec.range_start <= value <= rec.range_end:
                        if rec.mixed:
                            res += (rec.factor * value) + rec.fixed_amount
                        else:
                            res += rec.factor * value
        if res != 0.0:
            return res
        raise ValidationError(
            _('the amount isnt between of any ranges'))
