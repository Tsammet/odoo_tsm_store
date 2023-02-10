# -*- coding: utf-8 -*-
{
    'name': 'Tienda',
    'version': '1.0',
    'website': 'https://www.driverp.com',
    'author': 'DrivErp',
    'category': 'Extra Tools',
    'sequence': 50,
    'summary': 'Modulo de libros',
    'depends': ['base'],
    'description': '''
        Descripcion blablablablablabla Store
    ''',
    'data': [
        'views/tsm_store_menu.xml',
        'views/tsm_store_views.xml',
        'views/tsm_store_category.xml',
        'views/tsm_store_brand.xml',
        'views/tsm_customer_views.xml',
        'views/tsm_invoice_views.xml',
        'views/tsm_sale_order.xml',
        'views/tsm_remission.xml',
        'security/ir.model.access.csv',
        'report/tsm_store_report.xml',
        'report/tsm_client_report.xml',
        'data/sequences.xml',
    ],
    'demo': [],
    'test': [],
    'application': True,
}
