# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class TmsUnitExtradata(models.Model):
    _name = "tms.unit.extradata"
    _description = "Extra Data for Units"
    _rec_name = "extra_value"

    unit_id = fields.Many2one(
        'fleet.vehicle', 'Unit Name', required=True, ondelete='cascade',
        select=True,)
    extra_data_id = fields.Many2one(
        'tms.unit.category', 'Field', domain="[('type','=','extra_data')]",
        required=True)
    extra_value = fields.Char('Valor', size=64, required=True)

    _sql_constraints = [
        ('name_uniq',
            'unique(unit_id,extra_data_id)',
            'Extra Data Field must be unique for each unit !'),
    ]
