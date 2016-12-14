# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models


class TmsUnitExpiry(models.Model):
    _name = "tms.unit.expiry"
    _description = "Expiry Extra Data for Units"

    unit_id = fields.Many2one(
        'fleet.vehicle', 'Unit Name', required=True, ondelete='cascade',
        select=True)
    expiry_id = fields.Many2one(
        'tms.unit.category',
        string='Field',
        required=True)
    extra_value = fields.Date('Value', required=True)
    name = fields.Char('Valor', size=10, required=True)

    _sql_constraints = [
        ('name_uniq',
         'unique(unit_id,expiry_id)',
         'Expiry Data Field must be unique for each unit !'),
    ]
