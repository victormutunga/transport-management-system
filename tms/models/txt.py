# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class Txt(models.Model):
    _name = 'txt.file'

    txt_filename = fields.Char()
    txt_binary = fields.Binary(string="Download File")
    txt_date = fields.Datetime(string="Date")
    txt_reference = fields.Char(string="Reference")
    name = fields.Char()
    sequence = fields.Many2one('ir.sequence')

    @api.model
    def create(self, values):
        txt = super(Txt, self).create(values)
        txt.name = self.env['ir.sequence'].next_by_code('Txt')
        txt.txt_filename = txt.name + ".txt"
        return txt
