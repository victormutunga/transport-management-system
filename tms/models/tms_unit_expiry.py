
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


from openerp import fields, models
# Units for Transportation EXPIRY EXTRA DATA


class TmsUnitExpiry(models.Model):
    _name = "tms.unit.expiry"
    _description = "Expiry Extra Data for Units"

    unit_id = fields.Many2one(
        'fleet.vehicle', 'Unit Name', required=True, ondelete='cascade',
        select=True)
    expiry_id = fields.Many2one(
        'tms.unit.category',
        string='Field',
        domain="[('type','=','expiry')]",
        required=True)
    extra_value = fields.Date('Value', required=True)
    name = fields.Char('Valor', size=10, required=True)

    _sql_constraints = [
        ('name_uniq',
         'unique(unit_id,expiry_id)',
         'Expiry Data Field must be unique for each unit !'),
    ]

    def on_change_extra_value(self, extra_value):
        # return {'value': {
        #     'name': extra_value[8:] + '/' +
        #     extra_value[5:-3] + '/' + extra_value[:-6]}}
        return 'comida'
