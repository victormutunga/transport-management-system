# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.tools.translate import _


class TmsFactor(models.Model):
    _name = "tms.factor"
    _description = "Factors to calculate Payment (Driver/Supplier) "
    "& Client charge"

    name = fields.Char('Name', size=64, required=True)
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
