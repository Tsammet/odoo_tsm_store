# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError






class TsmProduct(models.Model):
    _name = 'tsm.product'
    _description = 'Productos'
    _rec_name ='product'


    product = fields.Char('Producto', required=True)
    account = fields.Many2one('account.account', 'Cuenta') 
    image = fields.Binary('Imagen')
    price = fields.Float()
    cod = fields.Integer()
    category_id = fields.Many2one('tsm.category', 'Categoria del producto')
    brand_id = fields.Many2one('tsm.brand', 'Marca del Producto')

    def button_reasign(self):
        wizard_id = self.env['product.reasign'].create([
            {
                'old_name': self.product,
                'old_image':self.image,
                'product' : self.id
            }
        ])

        return {
        'view_mode': 'form',
        'res_model': 'product.reasign',
        'res_id': wizard_id.id,
        'type': 'ir.actions.act_window',
        'target': 'new',
        'context': self.env.context,
        'nodestroy': True
        }

class TsmCategory(models.Model):
    _name = 'tsm.category'
    _description = 'Categoria del producto'
    _rec_name ='name_category'


    name_category = fields.Char('Categoria')
    prod_ids = fields.One2many('tsm.product','category_id' ,'Producto')

    def button_reasign(self):
        wizard_id = self.env['category.reasign'].create([
            {
                'category' : self.id
            }
            ])

        return {
        'view_mode': 'form',
        'res_model': 'category.reasign',
        'res_id': wizard_id.id,
        'type': 'ir.actions.act_window',
        'target': 'new',
        'context': self.env.context,
        'nodestroy': True
        }


class TsmBrand(models.Model):
    _name = 'tsm.brand'
    _description = 'Marcas'
    _rec_name='brand'

    brand = fields.Char('Marca')
    prod_ids = fields.One2many('tsm.product', 'brand_id', 'Producto' )

    def button_reasign(self):
        wizard_id = self.env['brand.reasign'].create(
            [
                {
                    'old_brand':self.brand,
                    'brand': self.id
                }
            ]
        )
        return {
        'view_mode': 'form',
        'res_model': 'brand.reasign',
        'res_id': wizard_id.id,
        'type': 'ir.actions.act_window',
        'target': 'new',
        'context': self.env.context,
        'nodestroy': True
        }

DOCUMENT_TYPE= [
    ('Tarjeta Identidad', 'Tarjeta Identidad'),
    ('Cedula Ciudadana', 'Cedula Ciudadana'),
    ('Cedula Extranjero ', 'Cedula Extranjero')
]



class TsmCustomer(models.Model):
    _name = 'tsm.customer'
    _description = 'Clientes'
    _rec_name = 'customer_name'

    customer_name = fields.Char('Nombre del Cliente', compute='Full_Name')
    picture = fields.Binary('Foto', attachment=True)
    first_name = fields.Char('Nombres', required = True)
    last_name = fields.Char('Apellidos', required = True)
    document = fields.Selection(DOCUMENT_TYPE, 'Documento', required=True)
    no_document = fields.Integer('Número Documento', required=True)
    cell_phone= fields.Char('Telefono')
    email = fields.Char('Correo Electronico')
    invoice = fields.One2many('tsm.invoice', 'customer_ids', 'Factura')

    def button_reasign(self):
        wizard_id = self.env['customer.reasign'].create(
            [
                {
                    'old_first_name' : self.first_name,
                    'old_last_name' : self.last_name,
                    'old_document': self.document,
                    'old_no_document' : self.no_document,
                    'old_cellphone' : self.cell_phone,
                    'old_email': self.email,
                    'customer_id' : self.id
                }
            ]
        )
        return {
        'view_mode': 'form',
        'res_model': 'customer.reasign',
        'res_id': wizard_id.id,
        'type': 'ir.actions.act_window',
        'target': 'new',
        'context': self.env.context,
        'nodestroy': True
        }

    @api.one
    def Full_Name(self):
        self.customer_name = self.first_name + ' ' + self.last_name


STATE = [
    ('BORRADOR', 'BORRADOR'),
    ('VALIDADA', 'VALIDADA'),
    ('PAGADA', 'PAGADA'),
    ('CANCELADO', 'CANCELADO'),
]

PAYMENT_METHOD= [
    ('PAYPAL','paypal'),
    ('EFECTIVO','efectivo'),
    ('TARJETA','tarjeta'),
]

class TsmInvoice(models.Model):
    _name = 'tsm.invoice'
    _description = 'Factura'
    _rec_name = "no_invoice"
    
    partner = fields.Many2one('res.partner', 'Tercero')
    customer_ids = fields.Many2one('tsm.customer', 'Cliente')
    state = fields.Selection(STATE, 'Estado', default='BORRADOR')
    payment_method = fields.Selection(PAYMENT_METHOD, 'Metodo Pago')
    journal = fields.Many2one('account.journal', 'Diario')
    no_invoice = fields.Char('Núm Factura', readonly=True)
    date = fields.Date('Fecha de la Factura', default = fields.date.today())
    invoice_line = fields.One2many('tsm.invoice.line','invoice_ids','Lineas de Factura')
    total = fields.Integer('Total', compute='price_total')
    account_move_id = fields.Many2one('account.move', 'Account')

    def button_asiento(self):

        data = []

        # debito

        data.append({
            'partner_id' : self.partner.id,
            'name' : self.no_invoice,
            'account_id' : self.journal.default_debit_account_id.id,
            'debit' : self.total,
            'credit' : 0
        })

        # credito 

        for line in self.invoice_line:
            data.append({
                'partner_id' : self.partner.id,
                'name' : self.no_invoice,
                'account_id' : line.product.account.id,
                'debit' : 0,
                'credit' : line.sub_total
        })

        account_move_data = {
            'journal_id' : self.journal.id,
            'date' :self.date,
            'line_ids' : [(0,0,x) for x in data]
        }

        move_id = self.env['account.move'].create(account_move_data)
        self.account_move_id = move_id


    def button_reasign(self):
        wizard_id = self.env['invoice.reasign'].create(
            [
                {
                    'old_customer': self.customer_ids.id,
                    'old_payment_method': self.payment_method,
                    'invoice_id' : self.id
                }
            ]
        )

        return {
        'view_mode': 'form',
        'res_model': 'invoice.reasign',
        'res_id': wizard_id.id,
        'type': 'ir.actions.act_window',
        'target': 'new',
        'context': self.env.context,
        'nodestroy': True
        }


    def button_borrador(self):
        self.state = 'BORRADOR'

    def button_validado(self):
        self.state = 'VALIDADA'

    def button_pagada(self):
        self.state = 'PAGADA'
        if not self.payment_method:
            raise UserError("Por favor defina el metodo de pago")
        elif self.payment_method == 'EFECTIVO':
            raise UserError('Este tipo de pago está bloqueado temporalmente')

    def button_cancelado(self):
        self.state = 'CANCELADO'


    @api.model
    def create(self, values):
        values['no_invoice'] = self.env['ir.sequence'].next_by_code('tsm.invoice')
        res = super(TsmInvoice, self).create(values)
        return res

    @api.one
    def price_total(self):
        tot = 0
        for i in self.invoice_line:
            tot = tot + i.sub_total
        self.total = tot

class TsmInvoiceLine(models.Model):
    _name = 'tsm.invoice.line'
    _description = 'LINEA DE FACTURA'

    product = fields.Many2one('tsm.product', 'Producto')
    invoice_ids = fields.Many2one('tsm.invoice', 'Lineas de Factura')
    description = fields.Char('Descripción')
    price = fields.Integer('Precio')
    amount = fields.Integer('Cantidad')
    discount = fields.Float('Descuento')
    discount_total = fields.Integer('Descuento Total', compute='price_sub_total')
    sub_total = fields.Integer('Sub_Total', compute='price_sub_total')


    @api.onchange('product')
    def price_invoice(self):
        self.price = self.product.price
       

    @api.one
    def price_sub_total(self):
        self.discount_total = (self.price * self.amount) * (self.discount/100)
        self.sub_total = (self.price * self.amount) - (self.discount_total)

class CategoryReasign(models.TransientModel):
    _name = 'category.reasign'


    new_category = fields.Char('Categoría Nueva')
    category = fields.Many2one('tsm.category', 'Categoría', readonly = True)

    def do_reasign(self):
        self.category.name_category = self.new_category

class ProductReasign(models.TransientModel):
    _name = "product.reasign"

    old_name = fields.Char('Producto Antiguo')
    new_name = fields.Char('Producto Nuevo')
    old_image = fields.Binary()
    new_image = fields.Binary()
    product = fields.Many2one('tsm.product', 'Producto', readonly=True)

    def do_reasign(self):
        if self.new_name:
            self.product.product = self.new_name
        if self.new_image:
            self.product.image = self.new_image

class BrandReasign(models.TransientModel):
    _name = 'brand.reasign'

    old_brand = fields.Char('Antigua Marca')
    new_brand = fields.Char('Nueva Marca')
    brand_id = fields.Many2one('tsm.brand', 'Marca', readonly=True)

    def do_reasign(self):
        self.brand_id.brand = self.new_brand

class CustomerReasign(models.TransientModel):
    _name = 'customer.reasign'

    new_first_name = fields.Char('Nombres Nuevos')
    new_last_name = fields.Char('Apellidos Nuevos')
    old_first_name = fields.Char('Nombres Antiguis')
    old_last_name = fields.Char('Apellidos Antiguos')
    old_document = fields.Selection(DOCUMENT_TYPE, 'Viejo Tipo Documento')
    new_document = fields.Selection(DOCUMENT_TYPE, 'Nuevo Tipo Documento')
    old_no_document = fields.Integer('Antiguo No Documento')
    new_no_document = fields.Integer('Nuevo No Documento')
    new_email = fields.Char('Email Nuevo')
    old_email = fields.Char('Antiguo Email')
    new_cellphone = fields.Char('Nuevo Telefono')
    old_cellphone = fields.Char('Antiguo Telefono')
    customer_id = fields.Many2one('tsm.customer', 'Cliente', readonly=True)

    def do_reasign(self):
        if self.new_first_name:
            self.customer_id.first_name = self.new_first_name
        if self.new_last_name:
            self.customer_id.last_name = self.new_last_name
        if self.new_document:
            self.customer_id.document = self.new_document
        if self.new_no_document:
            self.customer_id.no_document = self.new_no_document
        if self.new_email:
            self.customer_id.email = self.new_email
        if self.new_cellphone:
            self.customer_id.cell_phone = self.new_cellphone   
            

class InvoiceReasign(models.TransientModel):
    _name = 'invoice.reasign'

    new_payment_method = fields.Selection(PAYMENT_METHOD,'Metodo de Pago')
    old_payment_method = fields.Selection(PAYMENT_METHOD,'Antiguo Metodode Pago')
    new_customer = fields.Many2one('tsm.customer', "Nuevo Cliente")
    old_customer = fields.Many2one('tsm.customer', 'Antiguo Cliente', readonly=True)
    password = fields.Char('CONTRASEÑA')
    invoice_id = fields.Many2one('tsm.invoice', 'Factura', readonly=True)

    def do_reasign(self):
        passw = "123456"
        if not self.password:
            raise UserError('Digite la contraseña')
        elif self.password == passw:
            if self.new_customer:
                self.invoice_id.customer_ids = self.new_customer
            if self.new_payment_method:
                self.invoice_id.payment_method = self.new_payment_method
        else:
            raise UserError('La contraseña digitada es incorrecta')

STATE_ORDER = [
    ('BORRADOR', 'BORRADOR'),
    ('CONFIRMAR', 'CONFIRMAR'),
    ('DESPACHO', 'DESPACHO'),
    ('FACTURADO', 'FACTURADO'),
]

class TsmSaleOrder(models.Model):
    _name = 'tsm.sale.order'
    _description = 'Orden de Venta'
    _rec_name ='consecutive'

    

    consecutive = fields.Char('CONSECUTIVO', readonly=True) 
    customer =  fields.Many2one('tsm.customer', 'Cliente')
    address = fields.Char('Dirección') 
    date_order = fields.Date('Fecha de Pedido', default = fields.date.today())
    date_dispatch = fields.Date('Fecha de Despacho')  
    sell_order_line = fields.One2many('tsm.sale.order.line', 'sale_order_id', 'Orden Venta id')
    dispatch_town= fields.Many2one('res.country.city', 'Ciudad de Despacho')
    state = fields.Selection(STATE_ORDER, 'Estado', default = "BORRADOR")
    billing_date = fields.Date('Fecha Facturación')
    invoice_id = fields.Many2one('tsm.invoice', 'Factura')
    remision_id = fields.Many2one('tsm.remission', 'remision')



   
    def button_despacho(self):

        if not self.date_dispatch:
            raise UserError("Se requiere la fecha de despacho")
        else:

            line_data = []

            for line in self.sell_order_line:
                line_data.append(
                    {
                        'product': line.prod.id,
                        'amount': line.amount
                    }
                )

            remission_data = {
                'cliente' : self.customer.id,
                'remision_line' : [(0, 0, x) for x in line_data]
            }

            create_remission = self.env['tsm.remission'].create(remission_data)
            self.remision_id = create_remission

            self.state = "DESPACHO"


    def button_facturado(self):
        if not self.billing_date:
            raise UserError("Se requiere la fecha de facturación")
        else:
            
            line_data = []

            for line in self.sell_order_line:
                line_data.append(
                    {
                        'product' : line.prod.id,
                        'description' : line.description,
                        'price' : line.price,
                        'amount' : line.amount
                    }
                )

            invoice_data = {
                'customer_ids' : self.customer.id,
                'invoice_line' : [(0, 0, x) for x in line_data]
            }

            create_invocie = self.env['tsm.invoice'].create(invoice_data)
            self.invoice_id = create_invocie

            self.state = "FACTURADO"

    def button_confirmado(self):
        if not self.sell_order_line:
            raise UserError("No tiene nada")
        else:
            self.state = "CONFIRMAR"

    @api.model
    def create(self, values):
        values['consecutive'] = self.env['ir.sequence'].next_by_code('tsm.sale.order')
        res = super(TsmSaleOrder, self).create(values)
        return res



class TsmSaleOrderLine(models.Model):
    _name = 'tsm.sale.order.line'
    _description = 'Orden de Venta linea'

    prod = fields.Many2one('tsm.product', 'Producto')
    amount = fields.Integer('Cantidad')
    description = fields.Char('Descripción')
    price = fields.Float('Precio')
    total_price = fields.Float('Total Precio', compute = "total")
    sale_order_id = fields.Many2one('tsm.sale.order', 'Orden de Venta id')

    @api.onchange('prod')
    def pricep(self):
        self.price = self.prod.price
       

    @api.one
    def total(self):
        self.total_price = self.price * self.amount


STATE_REMISSION = [
    ('BORRADOR', 'BORRADOR'),
    ('DESPACHADO', 'DESPACHADO'),
]

class TsmRemission(models.Model):
    _name = "tsm.remission"
    _description = "Remisión"

    cliente = fields.Many2one('tsm.customer', 'Cliente')
    dispatch_date = fields.Date('Fecha de Despacho', default = fields.date.today())
    persona_responsable = fields.Many2one ('res.users','Usuario Despacho')
    state = fields.Selection(STATE_REMISSION) 
    remision_line = fields.One2many('tsm.remission.line', 'remission_id', 'Remision Id')


class TsmRemissionLine(models.Model):
    _name = 'tsm.remission.line'
    _description = "Tabla"

    product = fields.Many2one('tsm.product', 'Producto')
    amount = fields.Integer('Cantidad')
    remission_id = fields.Many2one('tsm.remission', 'Remision')

# cuando se despacha se crea la remision 