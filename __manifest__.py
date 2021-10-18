# -*- coding: utf-8 -*-
{
    'name': "NBET_Process",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'account', 'om_account_budget', 'board'],

    # always loaded
    'data': [
        'data/top.xml',
        'views/actions.xml',
        'data/groups.xml',
        'views/views.xml',
        'views/menu.xml',
        'views/dashboard.xml',
        'data/automation.xml',
        'security/ir.model.access.csv',
        'report/report_template.xml',
        'report/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
