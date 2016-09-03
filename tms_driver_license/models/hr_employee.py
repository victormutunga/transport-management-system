# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from datetime import datetime


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    driver_license = fields.Char(string="License ID")
    license_type = fields.Char(string="License Type")
    days_to_expire = fields.Integer(compute='_compute_days_to_expire')
    license_expiration = fields.Date()

    @api.depends('license_expiration')
    def _compute_days_to_expire(self):
        for rec in self:
            if rec.license_expiration:
                date = datetime.strptime(rec.license_expiration, '%Y-%m-%d')
            else:
                date = datetime.now()
            now = datetime.now()
            delta = date - now
            rec.days_to_expire = delta.days if delta.days > 0 else 0
