# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# import time

from openerp import models
# from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
# from openerp.tools.translate import _


class TmsExpenseCancel(models.TransientModel):

    """ To validate Expense Record Cancellation"""

    _name = 'tms.expense.cancel'
    _description = 'Validate Expense Record Cancellation'

    # def action_cancel(self):

    #     """
    #          To Validate when cancelling Expense Record
    #          @param self: The object pointer.
    #          @param cr: A database cursor
    #          @param uid: ID of the user currently logged in
    #          @param context: A standard dictionary
    #          @return : retrun view of Invoice
    #     """
    #     record_id = self.pool.get('active_ids', [])
    #     if record_id:
    #         # invoice_obj = self.pool.get('account.invoice')
    #         expense_obj = self.pool.get('tms.expense')
    #         expense_line_obj = self.pool.get('tms.expense.line')
    #         expense_loan_obj = self.pool.get('tms.expense.loan')
    #         obj_move_reconcile = self.pool.get('account.move.reconcile')
    #         for expense in expense_obj.browse(record_id):
    #             self.execute("select id from tms_expense where state <> \
    #                 'cancel' and employee_id = \
    #                 " + str(expense.employee_id.id) + " order by date desc \
    #                 limit 1")
    #             data = filter(None, map(lambda x: x[0], self.fetchall()))
    #             if len(data) > 0 and data[0] != expense.id:
    #                 raise Warning(
    #                     _('Could not cancel Expense Record!'),
    #                     _('This Expense Record is not the last one for this \
    #                         driver'))
    #             if expense.paid:
    #                 raise Warning(
    #                     _('Could not cancel Expense Record!'),
    #                     _('This Expense Record\'s is already paid'))
    #                 return False
    #             if expense.state == 'confirmed':
    #                 # Unreconcile & Cancel Invoices linked to this Travel
    #                 # Expense Record
    #                 reconcile_ids = []
    #                 invoice_ids = []
    #                 for expense_line in expense.expense_line:
    #                     if expense_line.is_invoice:
    #                         invoice_ids.append(expense_line.invoice_id.id)
    #                         for move_line in (
    #                                 expense_line.invoice_id.move_id.line_id):
    #                             if move_line.reconcile_id:
    #                                 reconcile_ids.append(
    #                                     move_line.reconcile_id.id)
    #                 if reconcile_ids:
    #                     obj_move_reconcile.unlink(reconcile_ids)
    #                 # if invoice_ids:
    #                     # wres = invoice_obj.action_cancel(invoice_ids)
    #                     # wres = invoice_obj.unlink(invoice_ids)
    #             move_id = expense.move_id.id
    #             move_state = expense.move_id.state
    #             expense_obj.write(
    #                 record_id,
    #                 {'state': 'cancel',
    #                  'cancelled_by': self,
    #                  'date_cancelled':
    #                  time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
    #                  'move_id': False})
    #             loan_ids = []
    #             for x in expense_obj.browse(record_id)[0].expense_line:
    #                 if x.loan_id.id:
    #                     loan_ids.append(x.loan_id.id)
    #             expense_line_obj.unlink(
    #                 [x.id for x in expense_obj.browse(
    #                     record_id)[0].expense_line])
    #             if len(loan_ids):
    #                 expense_loan_obj.write(
    #                     loan_ids,
    #                     {'state': 'confirmed',
    #                      'closed_by': False,
    #                      'date_closed': False})
    #             if move_id:
    #                 move_obj = self.pool.get('account.move')
    #                 if move_state == 'posted':
    #                     move_obj.button_cancel([move_id])
    #                 move_obj.unlink([move_id])
    #             travel_ids = []
    #             for travel in (expense.travel_ids
    #                            if not expense.driver_helper
    #                            else expense.travel_ids2):
    #                 travel_ids.append(travel.id)
    #             fuelvoucher_obj = self.pool.get('tms.fuelvoucher')
    #             advance_obj = self.pool.get('tms.advance')
    #             travel_obj = self.pool.get('tms.travel')
    #             record_ids = fuelvoucher_obj.search(
    #                 [('travel_id', 'in', tuple(travel_ids),),
    #                  ('employee_id', '=', expense.employee_id.id),
    #                  ('state', '!=', 'cancel')])
    #             fuelvoucher_obj.write(
    #                 record_ids,
    #                 {'expense_id': False,
    #                  'state': 'confirmed',
    #                  'closed_by': False,
    #                  'date_closed': False})
    #             record_ids = advance_obj.search(
    #                 [('travel_id', 'in', tuple(travel_ids),),
    #                  ('employee_id', '=', expense.employee_id.id),
    #                  ('state', '!=', 'cancel')])
    #             advance_obj.write(
    #                 record_ids,
    #                 {'expense_id': False,
    #                  'state': 'confirmed',
    #                  'closed_by': False,
    #                  'date_closed': False})
    #             if not expense.driver_helper:
    #                 travel_obj.write(
    #                     travel_ids,
    #                     {'expense_id': False,
    #                      'state': 'done',
    #                      'closed_by': False,
    #                      'date_closed': False})
    #             else:
    #                 travel_obj.write(travel_ids, {'expense2_id': False})
    #             if not expense.parameter_distance:
    #                 raise Warning(
    #                     _('Could not Confirm Expense Record !'),
    #                     _('Parameter to determine Vehicle distance update \
    #                         from does not exist.'))
    #             elif (expense.parameter_distance == 2 and
    #                     expense.state == 'confirmed'):
    #                 # Revisamos el parametro
    #                 # (tms_property_update_vehicle_distance)
    #                 # donde se define donde se actualizan los
    #                 # kms/millas a las unidades
    #                 self.pool.get(
    #                     'fleet.vehicle.odometer').unlink_odometer_rec(
    #                         travel_ids, expense.unit_id.id)
    #         return {'type': 'ir.actions.act_window_close'}
