{
    'name': 'Project Cost Estimation v1.2',
    'version': '17.0.1.0.0',
    'category': 'Project',
    'summary': 'Manage cost estimations for projects with approval workflow',
    'description': """
Project Cost Estimation
=======================
This module adds cost estimation functionality to Odoo Projects.

Features:
- Create cost estimates linked to projects
- Cost breakdown lines with quantity x unit price
- Approval workflow: draft -> submitted -> approved/rejected
- Role-based access: Project Users, Admins, and Approval Group
- Smart button on project form view
- Kanban views for estimates and project cards
    """,
    'author': 'Custom',
    'depends': ['project'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        # breakdown sub-view MUST be loaded before the estimate form that
        # embeds breakdown_ids, so Odoo resolves the inline list correctly.
        'views/cost_breakdown_views.xml',
        'views/cost_estimate_views.xml',
        'views/project_views_inherit.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
