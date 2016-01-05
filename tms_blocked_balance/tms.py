# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Argil Consulting - http://www.argil.mx
############################################################################
#    Coded by: German Ponce Dominguez (german.ponce@argil.mx)


from osv import osv, fields
import netsvc
from tools.translate import _
import time
from datetime import datetime, date, timedelta
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import decimal_precision as dp

# class tms_maintenance_order_activity_invoice(osv.osv):
#     _name = 'tms.maintenance.order.activity.invoice'
#     _inherit ='tms.maintenance.order.activity.invoice'
#     _columns = {
#         }

#     _defaults = {
#         }

class tms_maintenance_order_activity_invoice(osv.osv_memory):
    _inherit ='tms.maintenance.order.activity.invoice'
    _name = 'tms.maintenance.order.activity.invoice'
    _description = 'Create Invoices from External Workshop Supplier'
###################################################################################################        

    ########## Metodos para crear la factura ##########
    def button_generate_invoices(self,cr,uid,ids,context=None):
        invoice_obj = self.pool.get('account.invoice')
        record_ids =  context.get('active_ids',[])
        invoices_to_create = {}
        
        journal_id = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'purchase')], context=None)
        journal_id = journal_id and journal_id[0] or False
        activity_obj = self.pool.get('tms.maintenance.order.activity')
        for activity in activity_obj.browse(cr, uid, record_ids):
            a = activity.maintenance_order_id.product_id.property_stock_production.valuation_out_account_id.id
            if not a:
                raise osv.except_osv(_('Error !'),
                        _('There is no expense account defined ' \
                          'for production location of product: "%s" (id:%d)') % \
                                (activity.maintenance_order_id.product_id.name, activity.maintenance_order_id.product_id.id,))
            a = self.pool.get('account.fiscal.position').map_account(cr, uid, False, a)
            
            if activity.supplier_id.id not in invoices_to_create and activity.state=='done' and (not activity.invoiced or activity.invoice_id.state=='cancel'):
                invoices_to_create.update(
                    {   
                        activity.supplier_id.id : 
                        { 
                            'header' : {
                                    'name'              : _('Invoice TMS Maintenance'),
                                    'origin'            : activity.maintenance_order_id.name,
                                    'type'              : 'in_invoice',
                                    'journal_id'        : journal_id,
                                    'reference'         : _('Maintenance Activities Invoice'),
                                    'account_id'        : activity.supplier_id.property_account_payable.id,
                                    'partner_id'        : activity.supplier_id.id,
                                    #'address_invoice_id': self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default'],
                                    #'address_contact_id': self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default'],
                                    'invoice_line'      : [],
                                    'currency_id'       : activity.supplier_id.property_product_pricelist_purchase.currency_id.id,                                     #res.currency
                                    'comment'           : _('No Comments'),
                                    #'payment_term'      : pay_term,                                    #account.payment.term
                                    'fiscal_position'   : activity.supplier_id.property_account_position.id,
                                    'date_invoice'      : time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                    'bloqueed_maintenance_invoice': True,
                                    },
                            'activity_ids' : [],
                            }
                    }
                )
                
            if activity.state =='done' and (not activity.invoiced or activity.invoice_id.state=='cancel') :
                inv_line = (0,0,{
                        'name'      : activity.maintenance_order_id.name + ', ' + activity.product_id.name, 
                        'origin'    : activity.maintenance_order_id.product_id.name,
                        'account_id': a,
                        'price_unit': (activity.cost_service_external + activity.parts_cost_external),
                        'quantity'  : 1,
                        'uos_id'    : activity.product_id.uom_id.id,
                        'product_id': activity.product_id.id,
                        'invoice_line_tax_id': [(6, 0, [x.id for x in activity.product_id.supplier_taxes_id])],
                        'note'      : _('Invoice Created from Maintenance External Workshop Tasks'),
                        #'account_analytic_id': False,
                        'vehicle_id': activity.maintenance_order_id.unit_id.id,
                        'employee_id': activity.maintenance_order_id.driver_id.id,
                        'sale_shop_id': activity.maintenance_order_id.shop_id.id,
                        'bloqueed_maintenance_invoice': True,
                       })

                invoices_to_create[activity.supplier_id.id]['header']['invoice_line'].append(inv_line)
                invoices_to_create[activity.supplier_id.id]['activity_ids'].append(activity.id)
            
        if not invoices_to_create:
            raise osv.except_osv(_('Warning!'), _("Either all Tasks are already Invoiced or they were not done by an External Workshop (Supplier)"))
        for (key, invoice) in invoices_to_create.iteritems():
            invoice_id = invoice_obj.create(cr, uid, invoice['header'])
            activity_obj.write(cr, uid, invoice['activity_ids'], {'invoice_id':invoice_id, 'invoiced':True})            
        return True

class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit ='account.invoice'
    _columns = {
        'bloqueed_maintenance_invoice': fields.boolean('Bloquear Importes', help='Cuando se Crea desde el TMS Facturas, en estas no se puede Modificar \
            los Importes, a menos que se desactive esta Opcion', )
        }

    _defaults = {
        }


    def write(self, cr, uid, ids, vals, context=None):
        rec = self.browse(cr, uid, ids, context=None)[0]
        if rec.bloqueed_maintenance_invoice == True and rec.type == 'in_invoice':
            if 'bloqueed_maintenance_invoice' in vals:
                bloqueed = vals['bloqueed_maintenance_invoice']
                if bloqueed == False:
                    return super(account_invoice, self).write(cr, uid, ids, vals, context)
            if 'invoice_line' in vals:
                invoice_line = vals['invoice_line']
                if invoice_line:
                    raise osv.except_osv(
                            _("ERROR!"), 
                            _("""Las Facturas Creadas desde Tareas Externas, Cartas Porte, Almacen y Compras, No pueden Modificarse.
                                Para Modificarse debe Desactivarse el Campo Bloquear Importes ubicado en este Formulario.
                                Pestaña Otra Informacion --> Bloquear Importes.

                                Solo podra realizar esta Accion el Administrador del Sistema.
                                """)
                            )
        elif rec.bloqueed_maintenance_invoice == True and rec.type == 'out_invoice':
            if 'invoice_line' in vals:
                invoice_line = vals['invoice_line']
                if invoice_line:
                    raise osv.except_osv(
                            _("ERROR!"), 
                            _("""Las Facturas Creadas desde Cartas Porte, No pueden Modificarse.
                                Para Modificarse debe Desactivarse el Campo Bloquear Importes ubicado en este Formulario.
                                Pestaña Otra Informacion --> Bloquear Importes.

                                Solo podra realizar esta Accion el Administrador del Sistema.
                                """)
                            )
        res = super(account_invoice, self).write(cr, uid, ids, vals, context)
        return res

    def create(self, cr, uid, vals, context=None):
        purchase_obj = self.pool.get('purchase.order')
        picking_obj = self.pool.get('stock.picking')
        picking_in_obj = self.pool.get('stock.picking.in')
        if 'type' in vals:
            type_inv = vals['type']
            if type_inv:
                if type_inv == 'in_invoice':
                    if 'origin' in vals:
                        origin = vals['origin']
                        if origin:
                            if ':' in origin:
                                origin = tuple(origin.split(':'))
                                purchase_ids = purchase_obj.search(cr, uid, [('name','in',origin)])
                                if purchase_ids:
                                    vals.update({'bloqueed_maintenance_invoice':True})
                                else:
                                    picking_ids = picking_obj.search(cr, uid, [('name','in',origin)])
                                    if picking_ids:
                                       vals.update({'bloqueed_maintenance_invoice':True})
                                    else:
                                        picking_in_ids = picking_in_obj.search(cr, uid, [('name','in',origin)])
                                        if picking_in_ids:
                                           vals.update({'bloqueed_maintenance_invoice':True}) 
                            else:   
                                purchase_ids = purchase_obj.search(cr, uid, [('name','=',origin)])

                                if purchase_ids:
                                    vals.update({'bloqueed_maintenance_invoice':True})
                                else:
                                    picking_ids = picking_obj.search(cr, uid, [('name','=',origin)])
                                    if picking_ids:
                                       vals.update({'bloqueed_maintenance_invoice':True})
                                    else:
                                        picking_in_ids = picking_in_obj.search(cr, uid, [('name','=',origin)])
                                        if picking_in_ids:
                                           vals.update({'bloqueed_maintenance_invoice':True}) 
        return super(account_invoice, self).create(cr, uid, vals, context=context)

class tms_waybill_supplier_invoice(osv.osv_memory):
    _inherit = 'tms.waybill.supplier_invoice'
    _name = 'tms.waybill.supplier_invoice'
   
    _columns = {

                }
                
    def makeWaybillInvoices(self, cr, uid, ids, context=None):

        """
             To get Waybills and create Invoices
             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param context: A standard dictionary
             @return : retrun view of Invoice
        """

        if context is None:
            record_ids = ids
        else:
            record_ids =  context.get('active_ids',[])

        if record_ids:
            res = False
            invoices = []
            factor = self.pool.get('tms.factor')
            property_obj=self.pool.get('ir.property')
            partner_obj=self.pool.get('res.partner')
            fpos_obj = self.pool.get('account.fiscal.position')
            prod_obj = self.pool.get('product.product')
            account_jrnl_obj=self.pool.get('account.journal')
            invoice_obj=self.pool.get('account.invoice')
            waybill_obj=self.pool.get('tms.waybill')
            travel_obj=self.pool.get('tms.travel')

            journal_id = account_jrnl_obj.search(cr, uid, [('type', '=', 'purchase'),('tms_supplier_journal','=', 1)], context=None)
            if not journal_id:
                raise osv.except_osv('Error !',
                                 _('You have not defined TMS Supplier Purchase Journal...'))
            journal_id = journal_id and journal_id[0]


            prod_id = prod_obj.search(cr, uid, [('tms_category', '=', 'freight'),('tms_default_supplier_freight','=', 1),('active','=', 1)], limit=1)
            if not prod_id:
                raise osv.except_osv(
                    _('Missing configuration !'),
                    _('There is no product defined as Freight !!!'))
            
            product = prod_obj.browse(cr, uid, prod_id,  context=None)[0]
            
            #print "product.name : ", product.name
            prod_account = product.product_tmpl_id.property_account_expense.id
            if not prod_account:
                prod_account = product.categ_id.property_account_expense_categ.id
                if not prod_account:
                    raise osv.except_osv(_('Error !'),
                                         _('There is no expense account defined ' \
                                               'for this product: "%s" (id:%d)') % \
                                             (product.name, product.id,))
                    
            prod_account = fpos_obj.map_account(cr, uid, False, prod_account)
                
            cr.execute("select distinct supplier_id, currency_id from tms_waybill where waybill_type='outsourced' and supplier_invoice_id is null and (state='confirmed' or (state='approved' and billing_policy='automatic')) and id IN %s",(tuple(record_ids),))
            data_ids = cr.fetchall()
            if not len(data_ids):
                raise osv.except_osv(_('Warning !'),
                                     _('Not all selected records are Confirmed yet or already invoiced or selected records are not from Outsourced Freights...'))
            #print data_ids


            for data in data_ids:
                partner = partner_obj.browse(cr,uid,data[0])
 
                cr.execute("select id from tms_waybill where waybill_type='outsourced' and supplier_invoice_id is null and (state='confirmed' or (state='approved' and billing_policy='automatic')) and supplier_id=" + str(data[0]) + ' and currency_id=' + str(data[1]) + " and id IN %s", (tuple(record_ids),))
                waybill_ids = filter(None, map(lambda x:x[0], cr.fetchall()))
                
                notes = "Cartas Porte"
                inv_amount = 0.0
                empl_name = ''

                inv_lines = []
                for waybill in waybill_obj.browse(cr,uid,waybill_ids):
                    currency_id = waybill.currency_id.id

                    inv_line = (0,0, {
                            'name': product.name  + ' - Viaje: ' + (waybill.travel_id.name or _('Sin Viaje')) + ' - ' + _('Waybill: ') + waybill.name,
                            'origin': waybill.name,
                            'account_id': prod_account,
                            'price_unit': waybill.supplier_amount,
                            'quantity': 1.0,
                            'uos_id': product.uom_id.id,
                            'product_id': product.id,
                            'invoice_line_tax_id': [(6, 0, [x.id for x in product.supplier_taxes_id])],
                            'note': 'Carta Porte de Permisionario ' + (waybill.travel_id.name or _('Sin Viaje') ),
                            'account_analytic_id': False,
                            })
                    inv_lines.append(inv_line)
                    
                    notes += '\n' + waybill.name
                    departure_address_id = waybill.departure_address_id.id
                    arrival_address_id = waybill.arrival_address_id.id

                    a = waybill.supplier_id.property_account_payable.id
                    if not a:
                        raise osv.except_osv(_('Warning !'),
                                             _('Supplier << %s >> has not Payable Account defined.') % (waybill.supplier_id.name))


                    if waybill.supplier_id.id and waybill.supplier_id.property_supplier_payment_term.id:
                        pay_term = waybill.supplier_id.property_supplier_payment_term.id
                    else:
                        pay_term = False

                inv = {
                    'name'              : 'Fletes de Permisionario',
                    'origin'            : waybill.name,
                    'type'              : 'in_invoice',
                    'journal_id'        : journal_id,
                    'reference'         : 'Factura de Cartas Porte de Permisionario',
                    'account_id'        : a,
                    'partner_id'        : waybill.supplier_id.id,
                    'departure_address_id' : departure_address_id,
                    'arrival_address_id'   : arrival_address_id,
                    'address_invoice_id': self.pool.get('res.partner').address_get(cr, uid, [waybill.supplier_id.id], ['default'])['default'],
                    'address_contact_id': self.pool.get('res.partner').address_get(cr, uid, [waybill.supplier_id.id], ['default'])['default'],
                    'invoice_line'      : [x for x in inv_lines],
                    #'comment'           : 'Factura de Cartas Porte de Permisionario',
                    'payment_term'      : pay_term,
                    'fiscal_position'   : waybill.supplier_id.property_account_position.id,
                    'comment'           : 'Cartas Porte Permisionario'+notes,
                    'tms_type'          : 'invoice' if waybill.billing_policy == 'manual' else 'waybill',
                    'bloqueed_maintenance_invoice': True, # Bloquear los Importes
                }
                #print "inv: " , inv

                travel_obj.write(cr, uid, [waybill.travel_id.id], {'closed_by': uid, 'date_closed' : time.strftime(DEFAULT_SERVER_DATETIME_FORMAT), 'state':'closed'})

                inv_id = invoice_obj.create(cr, uid, inv)
                invoices.append(inv_id)
 
                waybill_obj.write(cr,uid,waybill_ids, {'supplier_invoice_id': inv_id, 'supplier_invoiced_by':uid, '  supplier_invoiced_date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})               

            ir_model_data = self.pool.get('ir.model.data')
            act_obj = self.pool.get('ir.actions.act_window')
            result = ir_model_data.get_object_reference(cr, uid, 'account', 'action_invoice_tree2')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            result['domain'] = "[('id','in', [" + ','.join(map(str, invoices)) + "])]"
            return result

    def makeWaybillSupplierInvoices(self, cr, uid, ids, context=None):

        """
             To get Waybills and create Invoices
             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param context: A standard dictionary
             @return : retrun view of Invoice
        """

        if context is None:
            record_ids = ids
        else:
            record_ids =  context.get('active_ids',[])

        if record_ids:
            res = False
            invoices = []
            factor = self.pool.get('tms.factor')
            property_obj=self.pool.get('ir.property')
            partner_obj=self.pool.get('res.partner')
            fpos_obj = self.pool.get('account.fiscal.position')
            prod_obj = self.pool.get('product.product')
            account_jrnl_obj=self.pool.get('account.journal')
            invoice_obj=self.pool.get('account.invoice')
            waybill_obj=self.pool.get('tms.waybill')
            travel_obj=self.pool.get('tms.travel')

            journal_id = account_jrnl_obj.search(cr, uid, [('type', '=', 'purchase'),('tms_supplier_journal','=', 1)], context=None)
            if not journal_id:
                raise osv.except_osv('Error !',
                                 _('You have not defined TMS Supplier Purchase Journal...'))
            journal_id = journal_id and journal_id[0]


            prod_id = prod_obj.search(cr, uid, [('tms_category', '=', 'freight'),('tms_default_supplier_freight','=', 1),('active','=', 1)], limit=1)
            if not prod_id:
                raise osv.except_osv(
                    _('Missing configuration !'),
                    _('There is no product defined as Freight !!!'))
            
            product = prod_obj.browse(cr, uid, prod_id,  context=None)[0]
            
            #print "product.name : ", product.name
            prod_account = product.product_tmpl_id.property_account_expense.id
            if not prod_account:
                prod_account = product.categ_id.property_account_expense_categ.id
                if not prod_account:
                    raise osv.except_osv(_('Error !'),
                                         _('There is no expense account defined ' \
                                               'for this product: "%s" (id:%d)') % \
                                             (product.name, product.id,))
                    
            prod_account = fpos_obj.map_account(cr, uid, False, prod_account)
                
            cr.execute("select distinct supplier_id, currency_id from tms_waybill where waybill_type='outsourced' and supplier_invoice_id is null and (state='confirmed' or (state='approved' and billing_policy='automatic')) and id IN %s",(tuple(record_ids),))
            data_ids = cr.fetchall()
            if not len(data_ids):
                raise osv.except_osv(_('Warning !'),
                                     _('Not all selected records are Confirmed yet or already invoiced or selected records are not from Outsourced Freights...'))
            #print data_ids


            for data in data_ids:
                partner = partner_obj.browse(cr,uid,data[0])
 
                cr.execute("select id from tms_waybill where waybill_type='outsourced' and supplier_invoice_id is null and (state='confirmed' or (state='approved' and billing_policy='automatic')) and supplier_id=" + str(data[0]) + ' and currency_id=' + str(data[1]) + " and id IN %s", (tuple(record_ids),))
                waybill_ids = filter(None, map(lambda x:x[0], cr.fetchall()))
                
                notes = "Cartas Porte"
                inv_amount = 0.0
                empl_name = ''

                inv_lines = []
                for waybill in waybill_obj.browse(cr,uid,waybill_ids):
                    currency_id = waybill.currency_id.id

                    inv_line = (0,0, {
                            'name': product.name  + ' - Viaje: ' + (waybill.travel_id.name or _('Sin Viaje')) + ' - ' + _('Waybill: ') + waybill.name,
                            'origin': waybill.name,
                            'account_id': prod_account,
                            'price_unit': waybill.supplier_amount,
                            'quantity': 1.0,
                            'uos_id': product.uom_id.id,
                            'product_id': product.id,
                            'invoice_line_tax_id': [(6, 0, [x.id for x in product.supplier_taxes_id])],
                            'note': 'Carta Porte de Permisionario ' + (waybill.travel_id.name or _('Sin Viaje') ),
                            'account_analytic_id': False,
                            })
                    inv_lines.append(inv_line)
                    
                    notes += '\n' + waybill.name
                    departure_address_id = waybill.departure_address_id.id
                    arrival_address_id = waybill.arrival_address_id.id

                    a = waybill.supplier_id.property_account_payable.id
                    if not a:
                        raise osv.except_osv(_('Warning !'),
                                             _('Supplier << %s >> has not Payable Account defined.') % (waybill.supplier_id.name))


                    if waybill.supplier_id.id and waybill.supplier_id.property_supplier_payment_term.id:
                        pay_term = waybill.supplier_id.property_supplier_payment_term.id
                    else:
                        pay_term = False

                inv = {
                    'name'              : 'Fletes de Permisionario',
                    'origin'            : waybill.name,
                    'type'              : 'in_invoice',
                    'journal_id'        : journal_id,
                    'reference'         : 'Factura de Cartas Porte de Permisionario',
                    'account_id'        : a,
                    'partner_id'        : waybill.supplier_id.id,
                    'departure_address_id' : departure_address_id,
                    'arrival_address_id'   : arrival_address_id,
                    'address_invoice_id': self.pool.get('res.partner').address_get(cr, uid, [waybill.supplier_id.id], ['default'])['default'],
                    'address_contact_id': self.pool.get('res.partner').address_get(cr, uid, [waybill.supplier_id.id], ['default'])['default'],
                    'invoice_line'      : [x for x in inv_lines],
                    'comment'           : 'Factura de Cartas Porte de Permisionario',
                    'payment_term'      : pay_term,
                    'fiscal_position'   : waybill.supplier_id.property_account_position.id,
                    'comment'           : notes,
                    'tms_type'          : 'invoice' if waybill.billing_policy == 'manual' else 'waybill',
                    'bloqueed_maintenance_invoice': True, # Bloquear los Importes
                }
                #print "inv: " , inv

                travel_obj.write(cr, uid, [waybill.travel_id.id], {'closed_by': uid, 'date_closed' : time.strftime(DEFAULT_SERVER_DATETIME_FORMAT), 'state':'closed'})

                inv_id = invoice_obj.create(cr, uid, inv)
                invoices.append(inv_id)
 
                waybill_obj.write(cr,uid,waybill_ids, {'supplier_invoice_id': inv_id, 'supplier_invoiced_by':uid, '  supplier_invoiced_date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})               

            ir_model_data = self.pool.get('ir.model.data')
            act_obj = self.pool.get('ir.actions.act_window')
            result = ir_model_data.get_object_reference(cr, uid, 'account', 'action_invoice_tree2')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            result['domain'] = "[('id','in', [" + ','.join(map(str, invoices)) + "])]"
            return result


class tms_waybill_invoice(osv.osv_memory):
    _inherit = 'tms.waybill.invoice'
    _name = 'tms.waybill.invoice'
   
    _columns = {

                }

    def makeWaybillInvoices(self, cr, uid, ids, context=None):
        """
             To get Waybills and create Invoices
             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param context: A standard dictionary
             @return : retrun view of Invoice
        """

        if context is None:
            record_ids = ids
        else:
            record_ids =  context.get('active_ids',[])
        
        
        group_lines = self.browse(cr,uid, ids)[0].group_line_product
            
        if record_ids:
            res = False
            invoices = []
            shipped_grouped_obj = self.pool.get('tms.waybill.shipped_grouped')
            property_obj=self.pool.get('ir.property')
            partner_obj=self.pool.get('res.partner')
            user_obj=self.pool.get('res.users')
            account_fiscal_obj=self.pool.get('account.fiscal.position')
            invoice_line_obj=self.pool.get('account.invoice.line')
            account_jrnl_obj=self.pool.get('account.journal')
            invoice_obj=self.pool.get('account.invoice')
            waybill_obj=self.pool.get('tms.waybill')

            journal_id = account_jrnl_obj.search(cr, uid, [('type', '=', 'sale')], context=None)
            journal_id = journal_id and journal_id[0] or False

            cr.execute("select distinct partner_id, currency_id from tms_waybill where (invoice_id is null or (select account_invoice.state from account_invoice where account_invoice.id = tms_waybill.invoice_id)='cancel') and (state='confirmed' or (state='approved' and billing_policy='automatic')) and id IN %s",(tuple(record_ids),))
            data_ids = cr.fetchall()
            if not len(data_ids):
                raise osv.except_osv(_('Warning !'),
                                     _('Not all selected records are Confirmed yet or already invoiced...'))            
            #print data_ids

            for data in data_ids:
                if not data[0]:
                    raise osv.except_osv(_('Warning !'),
                                     _('You have not defined Client account...'))            
                    
                partner = partner_obj.browse(cr,uid,data[0])
                cr.execute("select id from tms_waybill where (invoice_id is null or (select account_invoice.state from account_invoice where account_invoice.id = tms_waybill.invoice_id)='cancel') and (state='confirmed' or (state='approved' and billing_policy='automatic')) and partner_id=" + str(data[0]) + ' and currency_id=' + str(data[1]) + " and id IN %s", (tuple(record_ids),))
                waybill_ids = filter(None, map(lambda x:x[0], cr.fetchall()))
                #print "waybill_ids : ", waybill_ids
                inv_lines = []
                notes = _("Waybills")
                inv_amount = 0.0
                empl_name = ''
                product_shipped_grouped = {}
                for waybill in waybill_obj.browse(cr,uid,waybill_ids):
                    fpos = waybill.partner_id.property_account_position.id or False
                    fpos = fpos and account_fiscal_obj.browse(cr, uid, fpos, context=context) or False

                    for shipped_prod in waybill.waybill_shipped_product:
                        # *****                            
                        val={'product_name' : shipped_prod.product_id.name,
                            'product_id'    : shipped_prod.product_id.id,
                            'product_uom'   : shipped_prod.product_uom.id,
                            'quantity'      : shipped_prod.product_uom_qty,
                            }
                        key = (val['product_id'], val['product_uom'], val['product_name'])
                        if not key in product_shipped_grouped:
                            product_shipped_grouped[key] = val
                        else:
                            product_shipped_grouped[key]['quantity'] += val['quantity']
                        # *****

                    currency_id = waybill.currency_id.id
                    notas_list = []
                    for line in waybill.waybill_line:
                        if line.line_type=='product':
                            if line.product_id:
                                a = line.product_id.product_tmpl_id.property_account_income.id
                                if not a:
                                    a = line.product_id.categ_id.property_account_income_categ.id
                                if not a:
                                    a = property_obj.get(cr, uid,
                                        'property_account_income_categ', 'product.category',
                                        context=context).id
                                if not a:
                                    raise osv.except_osv(_('Error !'),
                                            _('There is no income account defined ' \
                                                    'for this product: "%s" (id:%d)') % \
                                                    (line.product_id.name, line.product_id.id,))

                                a = account_fiscal_obj.map_account(cr, uid, False, a)
                               
           
                               
                                inv_line = (0,0, {
                                    'name': line.name,
                                    'origin': line.waybill_id.name,
                                    'account_id': a,
                                    'price_unit': line.price_unit,
                                    'quantity': line.product_uom_qty,
                                    'uos_id': line.product_uom.id,
                                    'product_id': line.product_id.id,
                                    'invoice_line_tax_id': [(6, 0, [_w for _w in account_fiscal_obj.map_tax(cr, uid, fpos, line.product_id.taxes_id)])],
                                    'vehicle_id'    : line.waybill_id.travel_id.unit_id.id if line.waybill_id.travel_id else False,
                                    'employee_id'   : line.waybill_id.travel_id.employee_id.id if line.waybill_id.travel_id else False,
                                    'sale_shop_id'  : line.waybill_id.shop_id.id,
                                    'note': line.notes,
                                    #'account_analytic_id': False,
                                    })
                                inv_lines.append(inv_line)
                               
                       
                        # notes += ', ' + line.waybill_id.name
                        if line.waybill_id.name not in notas_list:
                            notas_list.append(line.waybill_id.name)
                    notes = ""
                    if notas_list:
                        for n in notas_list:
                            notes = notes+', '+n
                    # ***** 
                    #print "inv_lines: ", inv_lines
                    if group_lines:
                        #print "Si entra a agrupar lineas de Cartas Porte"
                        line_grouped = {}
                        for xline in inv_lines:
                            val={
                                    'name': xline[2]['name'],
                                    'origin': xline[2]['origin'],
                                    'account_id': xline[2]['account_id'],
                                    'price_unit': xline[2]['price_unit'],
                                    'quantity': xline[2]['quantity'],
                                    'uos_id': xline[2]['uos_id'],
                                    'product_id': xline[2]['product_id'],
                                    'invoice_line_tax_id': xline[2]['invoice_line_tax_id'],
                                    'note': xline[2]['note'],
                                    #'vehicle_id': xline[2]['vehicle_id'],
                                    #'employee_id': xline[2]['employee_id'],
                                    #'sale_shop_id': xline[2]['sale_shop_id'],
                                }
                            #print "val: ", val
                            key = (val['product_id'], val['uos_id'])#, val['vehicle_id'], val['employee_id'], val['sale_shop_id'])
                            #print "key: ", key
                            if not key in line_grouped:
                                line_grouped[key] = val
                            else:
                                line_grouped[key]['price_unit'] += val['price_unit']
                                        
                        #print "line_grouped: ", line_grouped
                        inv_lines = []
                        for t in line_grouped.values():
                            #print "t: ", t
                            vals = (0,0, {
                                    'name'          : t['name'],
                                    'origin'        : t['origin'],
                                    'account_id'    : t['account_id'],
                                    'price_unit'    : t['price_unit'],
                                    'quantity'      : t['quantity'],
                                    'uos_id'        : t['uos_id'],
                                    'product_id'    : t['product_id'],
                                    'invoice_line_tax_id': t['invoice_line_tax_id'],
                                    'note'          : t['note'],
                                    #'vehicle_id'    : t['vehicle_id'],
                                    #'employee_id'   : t['employee_id'],
                                    #'sale_shop_id'  : t['sale_shop_id'],
                                        }
                                    )
                            inv_lines.append(vals)
                        #print "inv_lines: ", inv_lines
                            
                # ******


                    # ****

                    departure_address_id = waybill.departure_address_id.id
                    arrival_address_id = waybill.arrival_address_id.id
                a = partner.property_account_receivable.id
                if partner and partner.property_payment_term.id:
                    pay_term = partner.property_payment_term.id
                else:
                    pay_term = False

                inv = {
                    'name'              : 'Factura',
                    'origin'            : 'Fact. de Cartas Porte',
                    'type'              : 'out_invoice',
                    'journal_id'        : journal_id,
                    'reference'         : 'Fact. de Cartas Porte',
                    'account_id'        : a,
                    'partner_id'        : waybill.partner_id.id,
                    'departure_address_id' : departure_address_id,
                    'arrival_address_id'   : arrival_address_id,
                    'address_invoice_id': self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default'],
                    'address_contact_id': self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default'],
                    'invoice_line'      : [x for x in inv_lines],
                    #'comment'           : 'Fact. de Cartas Porte',
                    'payment_term'      : pay_term,
                    'fiscal_position'   : partner.property_account_position.id,
                    'pay_method_id'     : partner.pay_method_id.id,
                    'acc_payment'       : partner.bank_ids[0].id if partner.bank_ids and partner.bank_ids[0] else False,
                    'comment'           : 'Cartas Porte'+notes,
                    'tms_type'          : 'invoice' if waybill.billing_policy == 'manual' else 'waybill',
                    'bloqueed_maintenance_invoice': True, # Bloquear los Importes
                }

                inv_id = invoice_obj.create(cr, uid, inv)
                invoices.append(inv_id)
                # ******
                #print "product_shipped_grouped: ", product_shipped_grouped
                for t in product_shipped_grouped.values():
                    #print "t: ", t
                    vals = {
                            'invoice_id'  : inv_id,
                            'product_id'  : t['product_id'],
                            'product_uom' : t['product_uom'],
                            'quantity'    : t['quantity'],
                            }
                    res = shipped_grouped_obj.create(cr, uid, vals)
                # ******
                waybill_obj.write(cr,uid,waybill_ids, {'invoice_id': inv_id, 'state':'confirmed', 'confirmed_by':uid, 'date_confirmed':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})               

            ir_model_data = self.pool.get('ir.model.data')
            act_obj = self.pool.get('ir.actions.act_window')
            result = ir_model_data.get_object_reference(cr, uid, 'account', 'action_invoice_tree1')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            result['domain'] = "[('id','in', [" + ','.join(map(str, invoices)) + "])]"
            return result
    