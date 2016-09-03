# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, models
from openerp.exceptions import ValidationError


class TmsTravel(models.Model):
    _inherit = 'tms.travel'

    @api.multi
    def action_progress(self):
        val = self.env['ir.config_parameter'].get_param(
            'driver_license_security_days')
        days = int(val) or 0
        for rec in self:
            if rec.employee_id.days_to_expire <= days:
                raise ValidationError(
                    _("You can not Dispatch this Travel because %s "
                      "Driver's License Validity (%s) is expired or"
                      " about to expire in next %s day(s)") % (
                        rec.employee_id.name,
                        rec.employee_id.license_expiration, val))
        return super(TmsTravel, self).action_progress()
