# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class TmsExpenseLine(models.Model):
    _inherit = 'tms.expense.line'

    xml_file = fields.Binary()
    xml_filename = fields.Char()
    pdf_file = fields.Binary()
    pdf_filename = fields.Char()
