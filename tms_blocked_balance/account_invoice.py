# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Argil Consulting - http://www.argil.mx
############################################################################
#    Coded by: German Ponce Dominguez (german.ponce@argil.mx)


from osv import osv, fields
from tools.translate import _


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
