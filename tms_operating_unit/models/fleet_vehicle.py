# -*- coding: utf-8 -*-
# © 2016 Jarsa Sistemas, S.A. de C.V.
# - Jesús Alan Ramos Rodríguez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class FleetVehicle(models.Model):
    _name = 'fleet.vehicle'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        required=True,
        default=lambda self:
            self.env['res.users'].
            operating_unit_default_get(self._uid))
