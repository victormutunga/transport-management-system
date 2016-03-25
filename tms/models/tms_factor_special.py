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

import time

from openerp import fields, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class TmsFactorSpecial(models.Model):
    _name = "tms.factor.special"
    _description = "Python Code calculate Payment (Driver/Supplier) & \
                        Client charge"

    name = fields.Char('Special Name', size=200, required=True),
    active = fields.Boolean('Active', default=True),
    date = fields.Date('Date', required=True,
                       default=time.strftime(DEFAULT_SERVER_DATE_FORMAT)),
    description = fields.Text('Description'),
    python_code = fields.Text('Python Code', required=True),
    factor_ids = fields.One2many('tms.factor', 'factor_special_id', 'Factor'),
    type = fields.Selection([
        ('salary', 'Driver Salary'),
        ('salary_distribution', 'Salary Distribution'),
        ('retention', 'Salary Retentions & Discounts'),
        ('supplier', 'Supplier Payment'), ], 'Type', required=True, help="""
Driver Salary => Use this for special Driver Salary calculation
Salary Distribution => Useful in some countries, you can make a Wage
distribution on several expenses, so Salary is masked for Tax purposes
Salary Retentions & Discounts => Use this for Driver Tax retentions
Supplier => Use this to calculate Supplier Travel Payment
                """),
    company_id = fields.Many2one('res.company', 'Company', required=False),
