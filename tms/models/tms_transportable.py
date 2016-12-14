# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models


class TmsTransportable(models.Model):
    _name = 'tms.transportable'
    _description = 'Transportable Product'

    name = fields.Char(required=True)
    uom_id = fields.Many2one(
        'product.uom', 'Unit of Measure ', required=True)
    factor_type = fields.Selection([
        ('distance', 'Distance Route (Km/Mi)'),
        ('distance_real', 'Distance Real (Km/Mi)'),
        ('weight', 'Weight'),
        ('volume', 'Volume'),
        ], required=True,)

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        copied_count = self.search_count(
            [('name', '=like', "Copy of %s" % self.name)])
        if not copied_count:
            new_name = "Copy of %s" % self.name
        else:
            new_name = "Copy of %s (%s)" % (self.name, copied_count)

        default['name'] = new_name
        return super(TmsTransportable, self).copy(default)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         _("Name must be unique")),
    ]
