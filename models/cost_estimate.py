from odoo import models, fields, api
from odoo.exceptions import UserError


class ProjectCostEstimate(models.Model):
    _name = 'project.cost.estimate'
    _description = 'Project Cost Estimate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Estimate Name',
        required=True,
        tracking=True,
        default='New Cost Estimate',
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        ondelete='cascade',
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
        copy=False,
    )
    breakdown_ids = fields.One2many(
        'project.cost.breakdown',
        'estimate_id',
        string='Cost Breakdown',
        copy=True,
    )
    estimated_total_cost = fields.Float(
        string='Estimated Total Cost',
        compute='_compute_estimated_total_cost',
        store=True,
        digits=(16, 2),
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    notes = fields.Html(
        string='Notes',
    )
    created_by = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True,
        copy=False,
    )
    submission_date = fields.Datetime(
        string='Submission Date',
        readonly=True,
        copy=False,
    )
    approval_date = fields.Datetime(
        string='Approval/Rejection Date',
        readonly=True,
        copy=False,
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approved/Rejected By',
        readonly=True,
        copy=False,
    )

    @api.depends('breakdown_ids.subtotal')
    def _compute_estimated_total_cost(self):
        for record in self:
            record.estimated_total_cost = sum(record.breakdown_ids.mapped('subtotal'))

    # ── Smart button action ────────────────────────────────────────────────
    def action_open_cost_estimates(self):
        """Open cost estimates scoped to this record's project (used by smart button)."""
        return {
            'name': 'Cost Estimates',
            'type': 'ir.actions.act_window',
            'res_model': 'project.cost.estimate',
            'view_mode': 'tree,kanban,form',
            'domain': [('project_id', '=', self.project_id.id)],
            'context': {'default_project_id': self.project_id.id},
        }

    # ── Workflow actions ───────────────────────────────────────────────────
    def action_submit(self):
        """Submit the estimate for approval. Only Project Admins can submit."""
        self._check_admin_access()
        for record in self:
            if record.state != 'draft':
                raise UserError(
                    f'Only draft estimates can be submitted. '
                    f'"{record.name}" is currently: {dict(record._fields["state"].selection).get(record.state)}.'
                )
            record.write({
                'state': 'submitted',
                'submission_date': fields.Datetime.now(),
            })
        return True

    def action_approve(self):
        """Approve the estimate. Only Approval Group members can approve."""
        self._check_approver_access()
        for record in self:
            if record.state != 'submitted':
                raise UserError(
                    f'Only submitted estimates can be approved. '
                    f'"{record.name}" is currently: {dict(record._fields["state"].selection).get(record.state)}.'
                )
            record.write({
                'state': 'approved',
                'approval_date': fields.Datetime.now(),
                'approved_by': self.env.user.id,
            })
        return True

    def action_reject(self):
        """Reject the estimate. Only Approval Group members can reject."""
        self._check_approver_access()
        for record in self:
            if record.state != 'submitted':
                raise UserError(
                    f'Only submitted estimates can be rejected. '
                    f'"{record.name}" is currently: {dict(record._fields["state"].selection).get(record.state)}.'
                )
            record.write({
                'state': 'rejected',
                'approval_date': fields.Datetime.now(),
                'approved_by': self.env.user.id,
            })
        return True

    def action_reset_to_draft(self):
        """Reset a rejected estimate back to draft. Only Admins can do this."""
        self._check_admin_access()
        for record in self:
            if record.state != 'rejected':
                raise UserError(
                    f'Only rejected estimates can be reset to draft. '
                    f'"{record.name}" is currently: {dict(record._fields["state"].selection).get(record.state)}.'
                )
            record.write({
                'state': 'draft',
                'submission_date': False,
                'approval_date': False,
                'approved_by': False,
            })
        return True

    # ── Access guards ──────────────────────────────────────────────────────
    def _check_admin_access(self):
        """Ensure the current user is a Project Admin or Cost Approver."""
        if not (
            self.env.user.has_group('project.group_project_manager')
            or self.env.user.has_group('project_cost_estimate.group_cost_approver')
        ):
            raise UserError('Only Project Administrators can perform this action.')

    def _check_approver_access(self):
        """Ensure the current user belongs to the Cost Approval Group."""
        if not self.env.user.has_group('project_cost_estimate.group_cost_approver'):
            raise UserError(
                'Only members of the Cost Approval Group can approve or reject estimates.'
            )

    def write(self, vals):
        for rec in self:

            # ✅ لو حد بيغير state
            if 'state' in vals:
                new_state = vals['state']

                # ❌ user العادي ممنوع يغير state
                if not self.env.user.has_group('project.group_project_manager') \
                        and not self.env.user.has_group('project_cost_estimate.group_cost_approver'):
                    raise UserError("You are not allowed to change the estimate state.")

                # ❌ admin بس اللي يعمل submit
                if new_state == 'submitted' and not self.env.user.has_group('project.group_project_manager'):
                    raise UserError("Only Project Admins can submit estimates.")

                # ❌ approver بس approve/reject
                if new_state in ('approved', 'rejected') and not self.env.user.has_group(
                        'project_cost_estimate.group_cost_approver'):
                    raise UserError("Only Approvers can approve or reject estimates.")

            # 🔒 read-only بعد submit
            if rec.state != 'draft':
                allowed_fields = {'state', 'approval_date', 'approved_by', 'submission_date'}
                if set(vals.keys()) - allowed_fields:
                    raise UserError("Submitted/approved/rejected estimates are read-only.")

        return super().write(vals)
