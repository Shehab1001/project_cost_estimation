from odoo import models, fields, api


class ProjectCostBreakdown(models.Model):
    _name = 'project.cost.breakdown'
    _description = 'Project Cost Breakdown Line'
    _order = 'sequence, id'

    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )

    estimate_id = fields.Many2one(
        'project.cost.estimate',
        string='Cost Estimate',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(
        string='Description',
        required=True,
        placeholder='e.g. UI Design, Backend Development...',
    )

    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0,
        digits=(16, 2),
    )

    unit_price = fields.Float(
        string='Unit Price',
        required=True,
        default=0.0,
        digits=(16, 2),
    )
    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True,
        digits=(16, 2),
    )
    currency_id = fields.Many2one(
        related='estimate_id.currency_id',
        string='Currency',
        store=True,
        readonly=True,
    )

    state = fields.Selection(
        related='estimate_id.state',
        string='Estimate State',
        store=True,
        readonly=True,
    )

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
