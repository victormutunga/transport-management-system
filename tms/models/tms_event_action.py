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
from openerp.osv import osv, fields


# Actions triggered by Events category


class tms_event_action(osv.osv):
    _name = "tms.event.action"
    _description = "Actions triggered by Events categories"
    _columns = {
        'name': fields.char('Name', size=128, required=True, translate=True),
        'event_category_ids': fields.many2many('tms.event.category', 'tms_event_action_rel', 'action_id', 'event_category_id', 'Event Categories'),
        'field_id': fields.many2one('ir.model.fields', 'Field to update'),
        'object_id': fields.related('field_id', 'model_id', type='many2one', relation='ir.model', string='Object', store=True, readonly=True),
        'get_value': fields.text('Python Code'),
        'notes': fields.text('Notes'),
        'active': fields.boolean('Active'),
    }
    _defaults = {
        'active': True,
    }
    _sql_constraints = [('name_uniq', 'unique(name)', 'Category name must be unique !')]
    _order = "name"

