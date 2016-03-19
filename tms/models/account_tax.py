# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models

# Add special tax calculation for Mexico


class AccountTax(models.Model):
    _name = 'account.tax'
    _inherit = 'account.tax'

    def compute_all_tax_and_retention(
            self, taxes, price_unit, quantity, tax_type=None):
        res = 0.0
        precision = self.pool.get('decimal.precision').precision_get(
            'Account')
        total = round(price_unit * quantity, precision)
        for tax in taxes:
            if not (tax_type == 'negative' and tax.amount >= 0.00):
                res += round((total * tax.amount), precision)
        return {
            'res': res
        }
