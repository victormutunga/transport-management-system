# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def unlink(self):
        for rec in self:
            advances = self.env['tms.advance'].search(
                [('payment_move_id', '=', rec.id)])
            expenses = self.env['tms.expense'].search(
                [('payment_move_id', '=', rec.id)])
            if advances:
                for advance in advances:
                    advance.paid = False
            if expenses:
                for expense in expenses:
                    expense.paid = False
            return super(AccountMove, self).unlink()
