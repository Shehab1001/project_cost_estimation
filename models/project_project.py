from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    cost_estimate_ids = fields.One2many(
        'project.cost.estimate',
        'project_id',
        string='Cost Estimates',
    )
    cost_estimate_count = fields.Integer(
        string='Cost Estimates',
        compute='_compute_cost_estimate_count',
        store=False,
    )
    latest_estimate_total = fields.Monetary(
        string='Latest Estimate Total',
        compute='_compute_latest_estimate_info',
        store=False,
        currency_field='currency_id',
    )
    latest_estimate_state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string='Latest Estimate State',
        compute='_compute_latest_estimate_info',
        store=False,
    )

    def action_open_cost_estimates(self):
        """Called by the smart button on the project form."""
        self.ensure_one()
        return {
            'name': 'Cost Estimates',
            'type': 'ir.actions.act_window',
            'res_model': 'project.cost.estimate',
            'view_mode': 'tree,kanban,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    @api.depends('cost_estimate_ids')
    def _compute_cost_estimate_count(self):
        for project in self:
            project.cost_estimate_count = len(project.cost_estimate_ids)

    @api.depends(
        'cost_estimate_ids',
        'cost_estimate_ids.estimated_total_cost',
        'cost_estimate_ids.state',
        'cost_estimate_ids.create_date',
    )
    def _compute_latest_estimate_info(self):
        for project in self:
            estimates = project.cost_estimate_ids.sorted('create_date', reverse=True)
            if estimates:
                latest = estimates[0]
                project.latest_estimate_total = latest.estimated_total_cost
                project.latest_estimate_state = latest.state
            else:
                project.latest_estimate_total = 0.0
                project.latest_estimate_state = False
