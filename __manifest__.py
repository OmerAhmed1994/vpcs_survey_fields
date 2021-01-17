# -*- coding: utf-8 -*-
{
    'name': 'Survey - Extra Fields',
    'version': '12.0.0.1',
    'author': 'VperfectCS',
    'maintainer': 'VperfectCS',
    'website': 'http://www.vperfectcs.com',
    'summary': '''Survey''',
    'description': '''
VPS Survey
======================
This module provides more types of surveys and their related results.

Fields Type:
- Name (First Name, Middle Name, Last Name)
- Relational Field with any Model (Many2one)
- Address Field (Street, Street2, City, State, Country, Zip)
- Document Uploader (Binary)
- Online Signature

With Validation, Result Preview, Graph View etc.

Tags:
- survey
- survey_extend
- survey_crm
    ''',
    'category': 'Survey',
    'depends': ['survey', 'document', 'web'],
    'images': ['static/description/banner.png'],
    'data': [
        'views/survey_views.xml',
        'views/survey_templates.xml',
        'views/survey_result.xml'
    ],
    'license': 'OPL-1',
    'support': 'info@vperfectcs.com',
    'sequence': 1,
    'application': False,
    'price': 39,
    'currency': 'EUR',
}
