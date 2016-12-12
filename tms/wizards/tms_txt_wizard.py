# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, fields, models
import base64


class TmsTxtExpense(models.TransientModel):

    _name = 'tms.txt.wizard'
    _description = 'Create txt for expenses'

    @api.model
    def _txt_values(self, line, active_model):
        if active_model == 'tms.expense':
            list_lines = [
                line.employee_id.name,
                str(line.amount_balance),
            ]
        elif active_model == 'tms.waybill':
            list_lines = [
                'hola invoice'
            ]
        return list_lines

    @api.multi
    def generate_file(self):
        active_model = self._context.get('active_model').encode('utf-8')
        active_ids = self.env[active_model].browse(
            self._context.get('active_ids'))
        if not active_ids:
            return {}
        lines = []
        names = []
        for line in active_ids:
            line_value = ', '.join(self._txt_values(line, active_model))
            names.append(line.name)
            lines.append(line_value)

        txt = self.env['txt.file'].create({
            'txt_binary': base64.encodestring(', '.join(lines)),
            'txt_date': fields.Datetime.now(),
            'txt_reference': "File of: " + ', '.join(names),
            'name': 'hola'
        })
        return {
            'name': 'Txt File',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'res_model': 'txt.file',
            'res_id': txt.id,
            'type': 'ir.actions.act_window'
        }
