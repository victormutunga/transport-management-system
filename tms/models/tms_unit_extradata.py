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


from openerp import models, fields


# Units EXTRA DATA
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
