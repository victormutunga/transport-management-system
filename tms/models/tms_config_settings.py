# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class TmsConfigSettings(models.TransientModel):
    _name = "tms.config.settings"
    _inherit = "res.config.settings"

    module_tms_agreement = fields.Boolean(
        string="Manage contracts and agreements",
        help="This module helps to quote efficiently considering special"
        " parameters, operative and administrative costs, it also automate "
        "the creation of documents (Travels, Fuel Vouchers, Advances and "
        "Waybills).")
    module_tms_analysis = fields.Boolean(
        string="Business inteligence",
        help="This module add Business Inteligence features to TMS module")
    module_tms_driver_license = fields.Boolean(
        string='Manage driver licence',
        help="This module add driver license to employees and block a travel "
        "if the license is about to expire")
    module_tms_maintenance = fields.Boolean(
        string="Fleet Maintenance",
        help="This module allow you to manage an Fleet Maintenance Workshop")
    module_tms_vehicle_insurance = fields.Boolean(
        string="Manage vehicle insurances",
        help="This module add insurance to vehicles and block a travel "
        "if the insurance is about to expire")
    module_tms_event = fields.Boolean(
        string="Add events to travels",
        help="Track the events thats happened during a travel")
    module_tms_operating_unit = fields.Boolean(
        string="Manage operating units",
        help="An Operating Unit is an organizational entity part of a "
        "company, but that operates as an independent unit. Organizationally, "
        "an Operating Unit divides a company from a Business/Divisional "
        "axis, while Departments divide a company from a functional axis"
        " perspective.")
    module_tms_driver_loan = fields.Boolean(
        string="Manage driver loans",
        help="")
    module_tms_internal_fuel = fields.Boolean(
        string="Manage internal fuel",
        help="")
    module_tms_operations = fields.Boolean(
        string="Manage operations or projects",
        help="")
    module_tms_second_driver = fields.Boolean(
        string="Manage second driver",
        help="")
    module_tms_toll_stations = fields.Boolean(
        string="Manage toll stations",
        help="")
