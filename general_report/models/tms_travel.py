# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models


class TmsTravel(models.Model):
    _inherit = 'tms.travel'

    report_general_id = fields.Many2one(
        'account.general.travel',
        string='Report',
    )
