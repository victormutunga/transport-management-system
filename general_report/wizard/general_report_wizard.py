# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, exceptions, models
from datetime import datetime, date, time, timedelta
now = datetime.now()


class ReportGeneralWizard(models.TransientModel):
    _name = 'report.general.report'

    month = fields.Selection(
        selection="_get_month", string="Month", default="1")
    year = fields.Selection(
        selection="_get_year", string="Year", default="2016")
    mode_type = fields.Selection(selection=[
            ('print', 'Print'),
            ('view', 'View'),
        ])
    vehicle_id = fields.Many2many(
        'fleet.vehicle',
        string='Vehicle',
    )

    def _get_month(self):
        return [
            ('1', 'January'),
            ('2', 'February'),
            ('3', 'March'),
            ('4', 'April'),
            ('5', 'May'),
            ('6', 'June'),
            ('7', 'July'),
            ('8', 'August'),
            ('9', 'September'),
            ('10', 'October'),
            ('11', 'November'),
            ('12', 'December')]

    def _get_year(self):
        years = []
        for year in list(range(2016, (now.year + 1))):
            years.append(
                (str(year), str(year))
            )
        return years

    @api.multi
    def create_report(self):
        for rec in self:
            if rec.vehicle_id:
                obj_travel.search([
                    ('state', '=', 'closed'),
                    ('unit_id', 'in', [x.id for x in rec.vehicle_id])
                ])
            else:
                obj_travel = self.env['tms.travel'].search([
                    ('state', '=', 'closed')])

            obj_report = self.env['report.general.travel']
            obj_report.search([]).unlink()
            for year in list(range(int(rec.year), (now.year + 1))):
                parent_id = obj_report.create({
                    'name': str(year),
                })
                for month in list(range(int(rec.month), 13)):
                    if ((month >= int(rec.month) and year != now.year) or
                            (month <= now.month and year == now.year)):
                        travels = [
                            travel for travel in obj_travel if
                            datetime.strptime(
                                travel.date, "%Y-%m-%d %H:%M:%S").month ==
                            month and
                            datetime.strptime(
                                travel.date, "%Y-%m-%d %H:%M:%S").year == year]
                        if travels:
                            child_id = obj_report.create({
                                'name': rec._get_month()[month-1][1],
                                'parent_id': parent_id.id
                            })
                            for travel in travels:
                                obj_report.create({
                                    'name': travel.name,
                                    'parent_id': child_id.id,
                                    'travel_id': travel.id,
                                })
            obj_report.search([
                ('parent_id', '=', False),
                ('child_ids', '=', False)]).unlink()
            mod_obj = self.env['ir.model.data']
            act_obj = self.env['ir.actions.act_window']
            result = mod_obj.get_object_reference(
                'general_report', 'open_view_report_general_travel_form')
            id = result and result[1] or False
            result = act_obj.search_read([('id', '=', id)])[0]
            return result
