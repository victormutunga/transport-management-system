# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from openerp import api, fields, models

class TmsTollImport(models.TransientModel):
    _name = 'tms.toll.import'

    filename = fields.Char(size=255)
    file = fields.Binary(
        string='Upload the data',
        required=True)

    @api.multi
    def update_tollstation_expense(self):
        document = base64.b64decode(self.file)
        lines = document.split('\n')
        lines.remove('')
        for line in lines:
                split_line = line.split('|')
                flag = split_line[0].split('\t')
                if len(flag) == 2:
                    split_line[0] = flag[1]
                if split_line[5][-1] == '.':
                    split_line[5].remove('.')
                datetime = str(split_line[2] + ' ' + split_line[3])
                num_tag = split_line[0].replace('.', '')
                exists = self.env['tms.toll.data'].search([
                    ('date', '=', datetime),
                    ('num_tag', '=', num_tag)])
                if not exists:
                    self.env['tms.toll.data'].create({
                        'num_tag': num_tag,
                        'economic_number': split_line[1],
                        'date': datetime,
                        'toll_station': split_line[4],
                        'import_rate': split_line[5],
                        })
        return {
            'name': 'Toll station data',
            'view_type': 'form',
            'view_mode': 'tree',
            'target': 'current',
            'res_model': 'tms.toll.data',
            'type': 'ir.actions.act_window'
        }
