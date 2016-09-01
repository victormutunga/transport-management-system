# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models


class TmsUnitKit(models.Model):
    _name = "tms.unit.kit"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Units Kits"

    name = fields.Char('Name', required=True)
    unit_id = fields.Many2one('fleet.vehicle', 'Unit', required=True)
    trailer1_id = fields.Many2one('fleet.vehicle', 'Trailer 1', required=True)
    dolly_id = fields.Many2one('fleet.vehicle', 'Dolly')
    trailer2_id = fields.Many2one('fleet.vehicle', 'Trailer 2')
    employee_id = fields.Many2one(
        'hr.employee', 'Driver', domain=[('driver', '=', True)])
    date_start = fields.Datetime('Date start', required=True)
    date_end = fields.Datetime('Date end', required=True)
    notes = fields.Text('Notes')
    active = fields.Boolean('Active', default=(lambda *a: True))

    _sql_constraints = [
        ('name_uniq', 'unique(unit_id,name)',
         'Kit name number must be unique for each unit !'),
    ]
    _order = "name desc, date_start desc"
