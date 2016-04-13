# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

from openerp import fields, models
from openerp import netsvc
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _


# Wizard que permite hacer una copia de la carta porte al momento de cancelarla
class TmsWaybillCancel(models.TransientModel):

    """ To create a copy of Waybill when cancelled"""

    _name = 'tms.waybill.cancel'
    _description = 'Make a copy of Cancelled Waybill'

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=(lambda self, cr, uid, context: self.pool.get(
            'res.users').browse(cr, uid, uid).company_id.id))
    copy_waybill = fields.Boolean(
        'Create copy of this waybill?', required=False)
    sequence_id = fields.Many2one('ir.sequence', 'Sequence', required=False)
    date_order = fields.Date(
        'Date', required=False, default=(fields.date.context_today))

    def make_copy(self):

        """
             To copy Waybills when cancelling them
             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param context: A standard dictionary
             @return : retrun view of Invoice
        """

        record_id = self.pool.get('active_ids', [])

        # print record_id

        if record_id:
            # print "Si entra..."
            for record in self.browse(self):
                # print record.company_id.name
                # print record.date_order
                waybill_obj = self.pool.get('tms.waybill')
                for waybill in waybill_obj.browse(record_id):
                    # print waybill.name
                    if waybill.invoiced and waybill.invoice_paid:
                        raise Warning(
                            _('Could not cancel Waybill !'),
                            _('This Waybill\'s Invoice is already paid'))
                        # return False
                    elif (waybill.invoiced and waybill.invoice_id and
                          waybill.invoice_id.id and waybill.invoice_id.state !=
                          'cancel' and waybill.billing_policy == 'manual'):
                        raise Warning(
                            _('Could not cancel Waybill !'),
                            _('This Waybill is already Invoiced'))
                        # return False
                    elif (waybill.waybill_type == 'outsourced' and
                          waybill.supplier_invoiced and
                          waybill.supplier_invoice_paid):
                        raise Warning(
                            _('Could not cancel Waybill !'),
                            _('This Waybill\'s Supplier Invoice is already \
                                paid'))
                        # return False

                    elif (waybill.billing_policy == 'automatic' and
                          waybill.invoiced and not waybill.invoice_paid):
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(
                            'account.invoice', waybill.invoice_id.id,
                            'invoice_cancel')
                        invoice_obj = self.pool.get('account.invoice')
                        invoice_obj.unlink([waybill.invoice_id.id])
        #            elif waybill.state in ('draft','approved','confirmed') and
        #               waybill.travel_id.state in ('closed'):
        #                raise Warning(
        #                        _('Could not cancel Advance !'),
        #                        _('This Waybill is already linked to Travel
        #            Expenses record'))
                    # print "record_id:", record_id
                    elif (waybill.waybill_type == 'outsourced' and
                          waybill.supplier_invoiced):
                        raise Warning(
                            _('Could not cancel Waybill !'),
                            _('This Waybill\'s Supplier Invoice is already \
                            created. First, cancel Supplier Invoice and \
                            then try again'))

                    if waybill.move_id.id:
                        move_obj = self.pool.get('account.move')
                        if waybill.move_id.state != 'draft':
                            move_obj.button_cancel([waybill.move_id.id])
                        move_obj.unlink([waybill.move_id.id])

                    waybill_obj.write(record_id, {
                        'move_id': False,
                        'state': 'cancel',
                        'cancelled_by': self,
                        'date_cancelled':
                        time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

                    if record.copy_waybill:
                        default = {}
                        default.update({
                            'replaced_waybill_id': waybill.id,
                            'move_id': False})
                        if record.sequence_id.id:
                            default.update({
                                'sequence_id': record.sequence_id.id})
                        if record.date_order:
                            default.update({'date_order': record.date_order})
                        waybill = waybill_obj.copy(record_id[0])
        return {'type': 'ir.actions.act_window_close'}

TmsWaybillCancel()
