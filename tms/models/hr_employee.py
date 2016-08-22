# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models


class HrEmployee(models.Model):
    _description = 'Employees'
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    tms_category = fields.Selection(
        [('driver', 'Driver')], 'TMS Category',
        help='Used to define if this person will be used as a Driver '
        '(Freights related) or Mechanic (Maintenance related)', required=False)
    tms_advance_account_id = fields.Many2one(
        'account.account', 'Advance Account')
    tms_expense_negative_balance_account_id = fields.Many2one(
        'account.account', 'Negative Balance Account')
    base_id = fields.Many2one(
        'tms.base', 'Base')
