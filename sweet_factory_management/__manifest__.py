# -*- coding: utf-8 -*-
# =============================================================================
#  Sweet Factory Management
# -----------------------------------------------------------------------------
#  Location  : King Abdulaziz Branch Road, Riyadh, Saudi Arabia
#  Email     : sales@leapai.ai
#  Phone     : +966 53 553 3627
#  Website   : https://leapai.ai
#  Developer : Abdulkaraim Osman — Tech Manager | Backend Engineer | DevOps Engineer
#              at Bab International Corp For Specialized Services
#  LinkedIn  : https://www.linkedin.com/in/abdulkaraim-o-385b7a110/
# =============================================================================
{
    'name': 'Sweet Factory Management',
    'version': '19.0.1.0.0',
    'summary': 'Complete Sweet & Confectionery Factory ERP - Recipes, Batches, QC, Machines',
    'description': 'Full ERP for sweet and confectionery factories',
    'author': 'LeapAI',
    'maintainer': 'Abdulkaraim Osman',
    'support': 'sales@leapai.ai',
    'website': 'https://www.leapai.ai',
    'license': 'LGPL-3',
    'category': 'Manufacturing',
    'depends': ['mrp', 'stock', 'mail', 'account', 'purchase', 'sale_management', 'hr'],
    'data': [
        'security/sweet_factory_security.xml',
        'security/ir.model.access.csv',
        'data/sweet_sequence_data.xml',
        'views/sweet_dashboard_views.xml',
        'views/sweet_recipe_views.xml',
        'views/sweet_batch_views.xml',
        'views/sweet_quality_views.xml',
        'views/sweet_machine_views.xml',
        'views/sweet_config_views.xml',
        'views/sweet_menus.xml',
        'report/sweet_batch_report.xml',
        'report/sweet_batch_report_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sweet_factory_management/static/src/components/dashboard/dashboard.js',
            'sweet_factory_management/static/src/components/dashboard/dashboard.xml',
            'sweet_factory_management/static/src/components/dashboard/dashboard.scss',
        ],
    },
    'demo': ['demo/sweet_demo.xml'],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/screenshot.jpg',
    ],
    'i18n': ['i18n/ar.po', 'i18n/en.po'],
    'application': True,
    'installable': True,
}
