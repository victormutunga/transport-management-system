from openerp import models, fields, api, _
from openerp.tools.misc import formatLang
from datetime import datetime, date, time, timedelta
from dateutil.rrule import rrule, MONTHLY


class tms_context_general_ledger(models.TransientModel):
    _name = "tms.context.manager.ledger"
    _description = "A particular context for the general ledger"
    _inherit = "tms.report.context.common"

    fold_field = 'unfolded_accounts'
    unfolded_travels = fields.Many2many(
        'tms.travel',
        'context_to_travel',
        string='Unfolded Travels')

    def get_report_obj(self):
        return self.env['tms.manager.ledger']

    @api.multi
    def get_columns_names(self):
        date_from = datetime.strptime(self.date_from, "%Y-%m-%d")
        date_to = datetime.strptime(self.date_to, "%Y-%m-%d")
        names = []
        dates = rrule(MONTHLY, dtstart=date_from).between(
            date_from, date_to, inc=True)
        for date in dates:
            names.append(str(self._get_month(date.month - 1) +
                         '/' + str(date.year)))
        return names

    @api.multi
    def get_columns_types(self):
        types = []
        limit = len(self.get_columns_names())
        for x in range(limit):
            types.append("text")
        return types
