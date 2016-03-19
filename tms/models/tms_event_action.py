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


# Actions triggered by Events category


class TmsEventAction(models.Model):
    _name = "tms.event.action"
    _description = "Actions triggered by Events categories"

    name = fields.Char('Name', size=128, required=True, translate=True)
    event_category_ids = fields.Many2many(
        'tms.event.category', 'tms_event_action_rel', 'action_id',
        'event_category_id', 'Event Categories')
    field_id = fields.Many2one('ir.model.fields', 'Field to update')
    object_id = fields.Many2one(
        compute='field_id.model_id', relation='ir.model', string='Object',
        store=True, readonly=True)
    get_value = fields.Text('Python Code')
    notes = fields.Text('Notes')
    active = fields.Boolean('Active', default=True)

    _defaults = {
        'active': True,
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Category name must be unique !')]
    _order = "name"
