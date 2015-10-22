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


from osv import osv, fields
import time
import dateutil
import dateutil.parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from tools.translate import _
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import decimal_precision as dp
import netsvc
import openerp
import calendar
from openerp import SUPERUSER_ID

class tms_waybill(osv.osv):
    _name = 'tms.waybill'
    _inherit ='tms.waybill'
    _columns = {

        'overdue_invoice': fields.boolean('Ignorar Credito', 
            help="""Si este campo esta Activo, la Validacion de Credito para Clientes y las Facturas Vencidas, no afectara a esta Carta Porte."""),
        #'tipo_venta': fields.selection([('credit','Credito'),('cash','Contado')], 'Tipo Plazo'),

        }

    _defaults = {
        }


    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
                        'overdue_invoice': False,
                        })
        return super(tms_waybill, self).copy(cr, uid, id, default, context)

    def get_current_instance(self, cr, uid, id):
        lines = self.browse(cr,uid,id)
        obj = None
        for i in lines:
            obj = i
        return obj

    # def on_change_credito(self, cr, uid, ids, tipo_venta, partner_id, context=None):
    #     res = {}
    #     if not partner_id or not tipo_venta:
    #         return {'value':{'tipo_venta':'cash'}}
    #     partner_br = self.pool.get('res.partner').browse(cr, uid, partner_id, context=None)
    #     if partner_br.is_company == False:
    #         partner_br = partner_br.parent_id
    #     if not partner_br.property_payment_term:
    #         warning = {
    #                     'title': '%s ' % (partner_br.name,),
    #                     'message':'No tiene definido Plazo de Pago y solo podras Vender de Contado.\n Asigna Plazo ó Contacta al Administrador'}
    #         return {'value':{'tipo_venta':'cash'},'warning':warning}
    #     res.update({'payment_term':partner_br.property_payment_term.id})
    #     return {'value':res}

    def onchange_partner_id(self, cr, uid, ids, partner_id):
        if not partner_id:
            return {'value':{}}
        warning = {}
        title = False
        message = False
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=None)
        if partner.is_company == False:
            partner = partner.parent_id
        title =  _("Informacion Financiera de %s :") % partner.name
        this = self.get_current_instance(cr, uid, ids)
        message = " "
        warning = {
                'title': title,
                'message': message,
        }

        #cr.execute("select sum(amount_total) from tms_waybill where state='confirmed' and invoiced=False and partner_id=%s" % partner.id)
        # cr.execute("""select tw.id from tms_waybill as tw 
        #     join account_invoice as aci
        #     on aci.id=tw.invoice_id 
        #     where tw.state='confirmed' 
        #     and tw.partner_id=%s and aci.state='draft'""" % 
        #     partner.id)
        # waybill_confirmed_cr = cr.fetchall()
        # waybill_confirmed_ids = []
        # if waybill_confirmed_cr:
        #     waybill_confirmed_ids = [x[0] for x in waybill_confirmed_cr]
        tms_waybill_obj = self.pool.get('tms.waybill')
        
        waybill_confirmed_ids = tms_waybill_obj.search(cr, uid, [('state','=','confirmed'),('invoice_paid','=',False),('partner_id','=',partner.id)])
        waybill_amount = 0.0
        if ids:
            waybill_ids = tms_waybill_obj.search(cr, uid, [('state','=','approved'),('partner_id','=',partner.id),('id','!=',ids[0])])
        else:
            waybill_ids = tms_waybill_obj.search(cr, uid, [('state','=','approved'),('partner_id','=',partner.id)])

        if waybill_confirmed_ids:
            waybill_ids = waybill_ids + waybill_confirmed_ids
        for waybll in tms_waybill_obj.browse(cr, uid, waybill_confirmed_ids, context=None):
            if waybll.invoice_id.state in ('open','paid'):
                index_l = waybill_confirmed_ids.index(waybll.id)
                waybill_confirmed_ids.pop(index_l)
        for waybill in tms_waybill_obj.browse(cr, uid, waybill_ids, context=None):
            waybill_amount += waybill.amount_total

        credit_exc = 0.0
        if partner.credit == 0:
            credit_exc == 0.0
        elif partner.credit > 0.0:
            credit_exc = partner.credit_limit - (partner.credit+waybill_amount)
            if credit_exc < 0.0:
                credit_exc = credit_exc * (-1)

        account_voucher_obj = self.pool.get('account.voucher')
        account_voucher_ids = account_voucher_obj.search(cr, uid, [('partner_id','=',partner_id)])
        date = ''
        for voucher in account_voucher_obj.browse(cr, uid, account_voucher_ids, context=None):
            if voucher.date > date:
                date = voucher.date
        if not account_voucher_ids:
            date = 'No se ah detectado Pago'
        result =  super(tms_waybill, self).onchange_partner_id(cr, uid, ids, partner_id)
        cadena = "Total a Cobrar: $ " +  str('{:,}'.format(partner.credit if partner.credit else 00)) +'   ' + '\nLimite de Credito: $ ' + str('{:,}'.format(partner.credit_limit if partner.credit_limit else 00 )) + '   '+ '\nCredito Excedido: $ ' + str('{:,}'.format(credit_exc if credit_exc else 00)) + '   ' + '\nFecha del Ultimo Pago: ' + date + '\n Le Recomendamos Solicitar Pago.'
        warning['message'] = message + str(cadena)

        date_act = datetime.now().strftime('%Y-%m-%d')
        invoice_obj = self.pool.get('account.invoice')
        invoice_overdue_ids = invoice_obj.search(cr, uid, [('date_due','<',date_act),('state','=','open'),('residual','>',0.0),('partner_id','=',partner.id),('type','=','out_invoice')])
        if invoice_overdue_ids:
            cr.execute("select number from account_invoice where id in %s",(tuple(invoice_overdue_ids),))
            overdue_name_str = [ str(x[0]) for x in cr.fetchall()]
            warning_overdue = {
                        'title': "Error!",
                        'message': "El Cliente %s tiene las Facturas Vencidas :\n %s \n Solicitar pago o active el campo Ignorar Facturas Vencidas, de la ficha del Cliente." % (partner.name,overdue_name_str,),
                }
            value_d = result.get('value',{})
            #value_d['tipo_venta']= 'credit'

            return {'value': value_d, 'warning':warning_overdue}

        if partner.credit_limit < partner.credit:
            value_d = result.get('value',{})
            value_d['exced_credit']= True
            #value_d['tipo_venta']= 'cash'

            return {'value': value_d, 'warning':warning}
        else:
            if partner.property_payment_term:
                value_d = result.get('value',{})
                #value_d['tipo_venta']= 'credit'
                return {'value': value_d}
        return {'value': result.get('value',{})}

    def action_approve(self, cr, uid, ids, context=None):
        result =  super(tms_waybill, self).action_approve(cr, uid, ids, context=context)
        contado = False
        invoice_obj = self.pool.get('account.invoice')
        # print "############# APROBANDO CARTA PORTE >>>>>>>>"
        for order in self.browse(cr, uid, ids, context=context):
            ### REVISANDO ALBARANES POR FACTURAR ###
            partner_id = order.partner_id.id
            partner_br = order.partner_id
            if order.partner_id.is_company == False:
                partner_id = order.partner_id.parent_id.id
                partner_br = order.partner_id.parent_id
            stock_to_invoice_amount = 0.0
            stock_obj = self.pool.get('stock.picking.out')

            ### VERIFICANDO LOS LIMITES DE CREDITO
            if order.overdue_invoice:
                return result
            ###

            credit_exc = 0.0
            account_lines = 0
            ###### REVISANDO LOS VIAJES SI ESTAN FINALIZADOS ENTONCES PERMITE VALIDAR ######

            # if order.tipo_venta == 'credit':
            ####### BUSCANDO LAS CARTAS PORTE PARA APLICAR LA RESTRICCION ######
            # cr.execute("""select tw.id from tms_waybill as tw 
            # join account_invoice as aci
            # on aci.id=tw.invoice_id 
            # where tw.state='confirmed' 
            # and tw.partner_id=%s and aci.state='draft'""" % 
            # partner_br.id)
            # waybill_confirmed_cr = cr.fetchall()
            # waybill_confirmed_ids = []
            # if waybill_confirmed_cr:
            #     waybill_confirmed_ids = [x[0] for x in waybill_confirmed_cr]
            tms_waybill_obj = self.pool.get('tms.waybill')

            waybill_confirmed_ids = tms_waybill_obj.search(cr, uid, [('state','=','confirmed'),('invoice_paid','=',False),('partner_id','=',partner_br.id)])
            # print "######## WAYBILL CONFIRMED IDS >>>>>>>> ", waybill_confirmed_ids

            for waybll in tms_waybill_obj.browse(cr, uid, waybill_confirmed_ids, context=None):
                if waybll.invoice_id.state in ('open','paid'):
                    index_l = waybill_confirmed_ids.index(waybll.id)
                    waybill_confirmed_ids.pop(index_l)
            # print "########### WAYBILL FINALES A TOMAR EN CUENTA >>>>>> ", waybill_confirmed_ids
            waybill_amount = 0.0
            waybill_ids = tms_waybill_obj.search(cr, uid, [('state','=','approved'),('id','!=',ids[0]),('partner_id','=',partner_br.id)])
            # print "######### WAYBILLL IDS APROBADAS >>>>>> ", waybill_ids
            if waybill_confirmed_ids:
                waybill_ids = waybill_ids + waybill_confirmed_ids
            for waybill in tms_waybill_obj.browse(cr, uid, waybill_ids, context=None):
                waybill_amount += waybill.amount_total
            # print "################ WAYBILL AMOUNT >>>>> ", waybill_amount
            ##### END WAYBILL #####

            if order.payment_term:
                days = 0
                for line_p in order.payment_term.line_ids:
                    days = line_p.days
                    account_lines += 1
                if account_lines <= 1 and days == 0:
                    contado = True
            ## Validando y Buscando Facturas Vencidas de Acuerdo a la Fecha de Vencimiento, el Estado y el monto pendiente > 0.0
            date_act = datetime.now().strftime('%Y-%m-%d')
            invoice_overdue_ids = invoice_obj.search(cr, uid, [('date_due','<',date_act),('state','=','open'),('residual','>',0.0),('partner_id','=',partner_br.id),('type','=','out_invoice'),('id','!=',ids[0])])
            invoice_ids = invoice_obj.search(cr, uid, [('date_invoice','<=',date_act),('state','=','open'),('residual','>',0.0),('partner_id','=',partner_br.id),('type','=','out_invoice'),('id','!=',ids[0])])
            
            if partner_br.credit_limit == 0.0:
                if contado == False:
                    raise osv.except_osv(
                        _('Error de Informacion! \n El Cliente %s ' % partner_br.name),
                        _('No tiene Definido Limite de Credito se encuentra en 0.0\n Agregue un Credito o Active el campo Ignorar Credito') )

            if invoice_overdue_ids:
                ### Aqui Trataremos de Alternar que puedan desmarcar esas Facturas para que Puedan Validar la Nueva y en caso de que no entonces arrojar el mensaje
                # overdue_ignored_ids = invoice_obj.search(cr, uid, [('overdue_invoice','=',False),('id','in',tuple(invoice_overdue_ids))])
                # # print ">>>>>>>>>>>> FACTURAS QUE NO ESTAN IGNORADAS", overdue_ignored_ids
                if partner_br.overdue_invoice == False:
                    cr.execute("select number from account_invoice where id in %s",(tuple(invoice_overdue_ids),))
                    overdue_name_str = [ str(x[0]) for x in cr.fetchall()]

                    raise osv.except_osv(
                                    _('Error de Validacion! \n Las Facturas %s estan Vencidas para el Cliente %s') % (overdue_name_str, partner_br.name),
                                    _('Favor de solicitar  Pago o activar el Campo Ignorar Facturas Vencidas, de la ficha de Cliente.') )
                                    #_('Si necesita Omitir esta restriccion active el campo [Ignorar Facturas Vencidas] en la pestaña Contabilidad del Cliente') )
            #if invoice_ids:

            credit_total_partner = stock_to_invoice_amount + partner_br.credit + waybill_amount + order.amount_total
            if credit_total_partner == 0:
                credit_exc = 0.0
            elif credit_total_partner > 0.0:
                credit_exc = partner_br.credit_limit - credit_total_partner
                if credit_exc < 0.0:
                    credit_exc = credit_exc * (-1)
            if partner_br.credit_limit < credit_total_partner:
                if order.overdue_invoice == False:
                    raise osv.except_osv(
                            _('No se puede Confirmar !'),
                            _('El Cliente %s ah Excedido el Limite de Credito por la cantidad de %s \n Favor de solicitar pago o active el campo Ignorar Credito.' % (partner_br.name,str(credit_exc))))

            return  result

    def action_confirm(self, cr, uid, ids, context=None):
        contado = False
        invoice_obj = self.pool.get('account.invoice')
        for order in self.browse(cr, uid, ids, context=context):
            ### REVISANDO ALBARANES POR FACTURAR ###
            partner_id = order.partner_id.id
            partner_br = order.partner_id
            if order.partner_id.is_company == False:
                partner_id = order.partner_id.parent_id.id
                partner_br = order.partner_id.parent_id
            stock_to_invoice_amount = 0.0
            stock_obj = self.pool.get('stock.picking.out')

            ### VERIFICANDO LOS LIMITES DE CREDITO
            if order.overdue_invoice:
                return super(tms_waybill, self).action_confirm(cr, uid, ids, context)
            ###

            credit_exc = 0.0
            account_lines = 0
            ###### REVISANDO LOS VIAJES SI ESTAN FINALIZADOS ENTONCES PERMITE VALIDAR ######

            # if order.tipo_venta == 'credit':
            ####### BUSCANDO LAS CARTAS PORTE PARA APLICAR LA RESTRICCION ######
            # cr.execute("""select tw.id from tms_waybill as tw 
            # join account_invoice as aci
            # on aci.id=tw.invoice_id 
            # where tw.state='confirmed' 
            # and tw.partner_id=%s and aci.state='draft'""" % 
            # partner_br.id)
            # waybill_confirmed_cr = cr.fetchall()
            # waybill_confirmed_ids = []
            # if waybill_confirmed_cr:
            #     waybill_confirmed_ids = [x[0] for x in waybill_confirmed_cr]
            tms_waybill_obj = self.pool.get('tms.waybill')
            waybill_confirmed_ids = tms_waybill_obj.search(cr, uid, [('state','=','confirmed'),('invoice_paid','=',False),('partner_id','=',partner_br.id),('id','!=',ids[0])])
            for waybll in tms_waybill_obj.browse(cr, uid, waybill_confirmed_ids, context=None):
                if waybll.invoice_id.state in ('open','paid'):
                    index_l = waybill_confirmed_ids.index(waybll.id)
                    waybill_confirmed_ids.pop(index_l)
            waybill_amount = 0.0
            waybill_ids = tms_waybill_obj.search(cr, uid, [('state','=','approved'),('id','!=',ids[0]),('partner_id','=',partner_br.id)])
            # print "######### WAYBILLL IDS APROBADAS >>>>>> ", waybill_ids
            if waybill_confirmed_ids:
                waybill_ids = waybill_ids + waybill_confirmed_ids
            for waybill in tms_waybill_obj.browse(cr, uid, waybill_ids, context=None):
                waybill_amount += waybill.amount_total
            ##### END WAYBILL #####

            if order.payment_term:
                days = 0
                for line_p in order.payment_term.line_ids:
                    days = line_p.days
                    account_lines += 1
                if account_lines <= 1 and days == 0:
                    contado = True
            ## Validando y Buscando Facturas Vencidas de Acuerdo a la Fecha de Vencimiento, el Estado y el monto pendiente > 0.0
            date_act = datetime.now().strftime('%Y-%m-%d')
            invoice_overdue_ids = invoice_obj.search(cr, uid, [('date_due','<',date_act),('state','=','open'),('residual','>',0.0),('partner_id','=',partner_br.id),('type','=','out_invoice'),('id','!=',ids[0])])
            invoice_ids = invoice_obj.search(cr, uid, [('date_invoice','<=',date_act),('state','=','open'),('residual','>',0.0),('partner_id','=',partner_br.id),('type','=','out_invoice'),('id','!=',ids[0])])
            
            if partner_br.credit_limit == 0.0:
                if contado == False:
                    raise osv.except_osv(
                        _('Error de Informacion! \n El Cliente %s ' % partner_br.name),
                        _('No tiene Definido Limite de Credito se encuentra en 0.0\n Agregue un Credito o Active el campo Ignorar Credito') )

            if invoice_overdue_ids:
                ### Aqui Trataremos de Alternar que puedan desmarcar esas Facturas para que Puedan Validar la Nueva y en caso de que no entonces arrojar el mensaje
                # overdue_ignored_ids = invoice_obj.search(cr, uid, [('overdue_invoice','=',False),('id','in',tuple(invoice_overdue_ids))])
                # # print ">>>>>>>>>>>> FACTURAS QUE NO ESTAN IGNORADAS", overdue_ignored_ids
                if partner_br.overdue_invoice == False:
                    cr.execute("select number from account_invoice where id in %s",(tuple(invoice_overdue_ids),))
                    overdue_name_str = [ str(x[0]) for x in cr.fetchall()]

                    raise osv.except_osv(
                                    _('Error de Validacion! \n Las Facturas %s estan Vencidas para el Cliente %s') % (overdue_name_str, partner_br.name),
                                    _('Favor de solicitar  Pago o activar el Campo Ignorar Facturas Vencidas, de la ficha de Cliente.') )
                                    #_('Si necesita Omitir esta restriccion active el campo [Ignorar Facturas Vencidas] en la pestaña Contabilidad del Cliente') )
            #if invoice_ids:

            credit_total_partner = stock_to_invoice_amount + partner_br.credit + waybill_amount + order.amount_total
            if credit_total_partner == 0:
                credit_exc = 0.0
            elif credit_total_partner > 0.0:
                credit_exc = partner_br.credit_limit - credit_total_partner
                if credit_exc < 0.0:
                    credit_exc = credit_exc * (-1)
            if partner_br.credit_limit < credit_total_partner:
                if order.overdue_invoice == False:
                    raise osv.except_osv(
                            _('No se puede Confirmar !'),
                            _('El Cliente %s ah Excedido el Limite de Credito por la cantidad de %s \n Favor de solicitar pago o active el campo Ignorar Credito.' % (partner_br.name,str(credit_exc))))

        # for rec in self.browse(cr, uid, ids, context=None):
            # if order.invoice_id:
            #     order.invoice_id.write({'overdue_invoice': order.overdue_invoice,}) #'tipo_venta': rec.tipo_venta})

        result = super(tms_waybill, self).action_confirm(cr, uid, ids, context)
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.invoice_id:
                rec.invoice_id.write({'overdue_invoice': rec.overdue_invoice,})
        return result

    def write(self, cr, uid, ids, vals, context=None):
        res = super(tms_waybill, self).write(cr, uid, ids, vals, context=context)
        user_br = self.pool.get('res.users').browse(cr, uid, uid, context)
        if 'overdue_invoice' in vals:
            overdue_invoice = vals['overdue_invoice']
            if overdue_invoice == True:
                self.message_post(cr, uid, ids, 
                    body=_("Se Omitio Credito y Facturas Vencias del Cliente.<br/> Usuario: <b> %s </b>.") % (user_br.name,),  context=context)
        return res

    def create(self, cr, uid, vals, context=None):

        res = super(tms_waybill, self).create(cr, uid, vals, context=context)
        
        user_br = self.pool.get('res.users').browse(cr, uid, uid, context)
        if 'overdue_invoice' in vals:
            overdue_invoice = vals['overdue_invoice']
            if overdue_invoice == True:
                self.message_post(cr, uid, [res], 
                    body=_("Se Omitio Credito y Facturas Vencias del Cliente.<br/> Usuario: <b> %s </b>.") % (user_br.name,),  context=context)
        return res


# class tms_waybill_invoice(osv.osv):
#     _name = 'tms.waybill.invoice'
#     _inherit ='tms.waybill.invoice'
#     _columns = {
#         }

#     _defaults = {
#         }
#     def makeWaybillInvoices(self, cr, uid, ids, context=None):
#         result = super(tms_waybill_invoice, self).makeWaybillInvoices(cr, uid, ids, context)
#         tms_waybill_obj = self.pool.get('tms.waybill')
#         active_ids = context.get('active_ids',[])
#         for waybill in tms_waybill_obj.browse(cr, uid, active_ids, context=None):
#             if waybill.invoice_id:
#                 waybill.invoice_id.write({'overdue_invoice': waybill.overdue_invoice,}) #'tipo_venta': waybill.tipo_venta})
#         return result