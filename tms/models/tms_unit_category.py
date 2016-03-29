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


# Master catalog used for:
# - Unit Types
# - Unit Brands
# - Unit / Motor Models
# - Motor Type
# - Extra Data for Units (Like Insurance Policy, Unit Invoice, etc
# - Unit Status (Still not defined if is keeped or not
# - Documentacion expiraton  for Transportation Units
class TmsUnitCategory(models.Model):
    _name = "tms.unit.category"
    _description = "Types, Brands, Models, Motor Type for Transport Units"

    def name_get(self):
        # if not len(self):
        #     return []
        # reads = self.read(['name', 'parent_id'])
        # res = []
        # for record in reads:
        #     name = record['name']
        #     if record['parent_id']:
        #         name = record['parent_id'][1] + ' / ' + name
        #     res.append((record['id'], name))
        # return res
        return 'comida'

    def _name_get_fnc(self, prop, unknow_none):
        # res = self.name_get(self)
        # return dict(res)
        return 'comida'

    name = fields.Char('Name', size=30, required=True, translate=True)
    complete_name = fields.Char(
        compute='_name_get_fnc', method=True, size=300, string='Complete Name',
        store=True)
    parent_id = fields.Many2one(
        'tms.unit.category', 'Parent Category', select=True)
    child_id = fields.One2many(
        'tms.unit.category', 'parent_id', string='Child Categories')
    sequence = fields.Integer(
        'Sequence', help="Gives the sequence order when displaying this list \
            of categories.")
    type = fields.Selection([
        ('view', 'View'),
        ('unit_type', 'Unit Type'),
        ('brand', 'Motor Brand'),
        ('motor', 'Motor Model'),
        ('extra_data', 'Extra Data'),
        ('unit_status', 'Unit Status'),
        ('expiry', 'Expiry'),
        ('active_cause', 'Active / Inactive Causes'),
        ('red_tape', 'Red Tape Types'), ],
        'Category Type', required=True, help="""Category Types:
 - View: Use this to define tree structure
 - Type: Use this to define Unit types, like Tractor, Trailers, dolly, van,
        etc.
 - Brand: Units brands
 - Motor: Motors
 - Extra Data: Use to define several extra fields for unit catalog.
 - Expiry: Use it to define several extra fields for units related to document
    expiration (Ex. Insurance Validity, Plates Renewal, etc)
 - Active / Inactive Causes: Use to define causes for a unit to be
    Active / Inactive (Ex: Highway Accident, Sold, etc)
 - Red Tape Types: Use it to define all kind of Red Tapes like Unit
    registration, Traffic Violations, etc.
"""
    )
    fuel_efficiency_drive_unit = fields.Float(
        'Fuel Efficiency Drive Unit', required=False, digits=(14, 4))
    fuel_efficiency_1trailer = fields.Float(
        'Fuel Efficiency One Trailer', required=False, digits=(14, 4))
    fuel_efficiency_2trailer = fields.Float(
        'Fuel Efficiency Two Trailer', required=False, digits=(14, 4))
    notes = fields.Text('Notes')
    active = fields.Boolean('Active', default=True)
    mandatory = fields.Boolean(
        'Mandatory',
        help="This field is used only when field <Category Type> = expiry")
    # company_id = fields.Many2one('res.company', 'Company', required=False)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Category name number must be unique !'),
    ]

    _order = "sequence"

    def _check_recursion(self):
        # level = 100
        # while len(self):
        #     self.execute('select distinct parent_id from tms_unit_category \
        #         where id IN %s', (tuple(self),))
        #     self = filter(None, map(lambda x: x[0], self.fetchall()))
        #     if not level:
        #         return False
        #     level -= 1
        # return True
        return 'comida'

    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive categories.',
            ['parent_id'])
    ]

    def child_get(self):
        # return [self]
        return 'comida'

    def copy(self):
        # categ = self.browse(self)
        # if not self:
        #     default = {}
        # default['name'] = categ['name'] + ' (copy)'
        # return super(TmsUnitCategory, self).copy(self, id, default)
        return 'comida'
