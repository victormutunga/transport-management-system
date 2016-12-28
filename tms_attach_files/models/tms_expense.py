# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class TmsExpense(models.Model):
    _inherit = 'tms.expense'

    @api.multi
    def action_confirm(self):
        super(TmsExpense, self).action_confirm()
        for rec in self:
            for line in rec.expense_line_ids:
                if line.is_invoice:
                    rec.with_context(active_id=line.invoice_id.id)
                    vals = {
                        'file_xml_sign': line.xml_file,
                        'file_pdf': line.pdf_file,
                        'xml_name': line.xml_filename,
                        'pdf_name': line.pdf_filename,
                    }
                    wiz = self.env['oml.attachment.wizard'].create(vals)
                    wiz.attach()
