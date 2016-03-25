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

# Events category


class TmsEventCategory(models.Model):
    _name = "tms.event.category"
    _description = "Events categories"

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name', 'parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    name = fields.Char('Name', size=64, required=True, translate=True)
    gps_code = fields.Char(
        'GPS Code', size=64,
        help="This is used to link a Code from a GPS message")
    gps_type = fields.Selection([('in', 'Received from GPS'),
                                 ('out', 'Sent to GPS'),
                                 ('none', 'None'),
                                 ], 'GPS Type')
    complete_name = fields.Char(
        compute=_name_get_fnc, method=True, size=300,
        string='Complete Name', store=True)
    parent_id = fields.Many2one('tms.event.category', 'Parent Category',
                                select=True)
    child_id = fields.One2many('tms.event.category', 'parent_id',
                               string='Child Categories')
    action_ids = fields.Many2many(
        'tms.event.action', 'tms_event_action_rel',
        'event_category_id', 'action_id', 'Actions')
    notes = fields.Text('Notes')
    active = fields.Boolean('Active')
    company_id = fields.Many2one('res.company', 'Company', required=False)

    _defaults = {
        'active': True,
        'gps_type': 'none',
    }

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Category name must be unique !')]

    _order = "name"

    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from tms_event_category \
                where id IN %s', (tuple(ids)))
            ids = filter(None, map(lambda x: x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True
    _constraints = [
        (_check_recursion,
         'Error ! You can not create recursive categories.', ['parent_id'])
    ]

    def child_get(self, cr, uid, ids):
        return [ids]
