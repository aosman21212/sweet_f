from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SweetBatch(models.Model):
    _name = 'sweet.batch'
    _description = 'Production Batch'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_planned desc, id desc'

    name = fields.Char(string='Batch Number', readonly=True, copy=False, default='New', tracking=True)
    recipe_id = fields.Many2one('sweet.recipe', string='Recipe', required=True, tracking=True,
                                domain=[('state', '=', 'approved')])
    sweet_type = fields.Selection(related='recipe_id.sweet_type', string='Sweet Type', store=True)

    date_planned = fields.Datetime(string='Planned Date', required=True, default=fields.Datetime.now, tracking=True)
    date_start = fields.Datetime(string='Start Date', readonly=True)
    date_end = fields.Datetime(string='End Date', readonly=True)

    planned_qty = fields.Float(string='Planned Qty (kg)', required=True, default=100.0)
    actual_yield = fields.Float(string='Actual Yield (kg)', readonly=True)
    yield_variance = fields.Float(string='Yield Variance (kg)', compute='_compute_yield_variance', store=True)
    yield_percentage_actual = fields.Float(string='Actual Yield %', compute='_compute_yield_variance', store=True)

    # Expiry tracking
    production_date = fields.Date(string='Production Date')
    expiry_date = fields.Date(string='Expiry Date', compute='_compute_expiry_date', store=True)
    lot_id = fields.Many2one('stock.lot', string='Batch/Lot Number', copy=False)

    # Shift info
    shift = fields.Selection([
        ('morning', 'Morning (6:00 - 14:00)'),
        ('afternoon', 'Afternoon (14:00 - 22:00)'),
        ('night', 'Night (22:00 - 6:00)'),
    ], string='Shift')
    supervisor_id = fields.Many2one('hr.employee', string='Supervisor', tracking=True)
    operator_id = fields.Many2one('hr.employee', string='Operator')
    machine_id = fields.Many2one('sweet.machine', string='Primary Machine')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Production'),
        ('quality_check', 'Quality Check'),
        ('done', 'Done'),
        ('failed', 'Failed/Scrapped'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, copy=False)

    # Lines
    ingredient_line_ids = fields.One2many('sweet.batch.ingredient.line', 'batch_id', string='Ingredients Used')
    output_line_ids = fields.One2many('sweet.batch.output.line', 'batch_id', string='Output Products')
    quality_check_ids = fields.One2many('sweet.quality.check', 'batch_id', string='Quality Checks')

    # Computed counts
    quality_check_count = fields.Integer(compute='_compute_quality_check_count', string='QC Checks')
    quality_passed = fields.Boolean(compute='_compute_quality_passed', string='QC Passed', store=True)

    # Cost
    total_ingredient_cost = fields.Float(compute='_compute_costs', string='Total Ingredient Cost', store=True)
    cost_per_kg = fields.Float(compute='_compute_costs', string='Cost per kg', store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    # Process readings
    actual_cooking_temp = fields.Float(string='Actual Cooking Temp (°C)')
    actual_cooling_temp = fields.Float(string='Actual Cooling Temp (°C)')
    actual_duration = fields.Integer(string='Actual Duration (min)')

    notes = fields.Html(string='Notes')
    rejection_reason = fields.Text(string='Rejection/Failure Reason')

    @api.depends('actual_yield', 'planned_qty')
    def _compute_yield_variance(self):
        for rec in self:
            rec.yield_variance = rec.actual_yield - rec.planned_qty
            if rec.planned_qty:
                rec.yield_percentage_actual = (rec.actual_yield / rec.planned_qty) * 100
            else:
                rec.yield_percentage_actual = 0.0

    @api.depends('production_date', 'recipe_id.shelf_life_days')
    def _compute_expiry_date(self):
        from datetime import timedelta
        for rec in self:
            if rec.production_date and rec.recipe_id.shelf_life_days:
                rec.expiry_date = rec.production_date + timedelta(days=rec.recipe_id.shelf_life_days)
            else:
                rec.expiry_date = False

    @api.depends('quality_check_ids')
    def _compute_quality_check_count(self):
        for rec in self:
            rec.quality_check_count = len(rec.quality_check_ids)

    @api.depends('quality_check_ids', 'quality_check_ids.result')
    def _compute_quality_passed(self):
        for rec in self:
            checks = rec.quality_check_ids
            if not checks:
                rec.quality_passed = False
            else:
                rec.quality_passed = all(c.result == 'pass' for c in checks)

    @api.depends('ingredient_line_ids.actual_qty', 'ingredient_line_ids.cost_per_unit')
    def _compute_costs(self):
        for rec in self:
            total = sum(l.actual_qty * l.cost_per_unit for l in rec.ingredient_line_ids)
            rec.total_ingredient_cost = total
            if rec.actual_yield and rec.actual_yield > 0:
                rec.cost_per_kg = total / rec.actual_yield
            elif rec.planned_qty:
                rec.cost_per_kg = total / rec.planned_qty
            else:
                rec.cost_per_kg = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('sweet.batch') or 'New'
        return super().create(vals_list)

    @api.onchange('recipe_id', 'planned_qty')
    def _onchange_recipe_id(self):
        if self.recipe_id:
            self.ingredient_line_ids = [(5, 0, 0)]
            ratio = self.planned_qty / self.recipe_id.standard_batch_qty if self.recipe_id.standard_batch_qty else 1
            lines = []
            for ing in self.recipe_id.ingredient_ids:
                lines.append((0, 0, {
                    'product_id': ing.product_id.id,
                    'product_uom_id': ing.product_uom_id.id,
                    'planned_qty': ing.quantity_per_batch * ratio,
                    'ingredient_type': ing.ingredient_type,
                    'cost_per_unit': ing.cost_per_unit,
                }))
            self.ingredient_line_ids = lines

    def action_confirm(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft batches can be confirmed.'))
            if not rec.recipe_id:
                raise UserError(_('Please select a recipe.'))
            rec.write({'state': 'confirmed'})
            rec.message_post(body=_('Batch confirmed for production.'))

    def action_start(self):
        for rec in self:
            if rec.state != 'confirmed':
                raise UserError(_('Only confirmed batches can be started.'))
            rec.write({
                'state': 'in_progress',
                'date_start': fields.Datetime.now(),
                'production_date': fields.Date.today(),
            })
            rec.message_post(body=_('Production started.'))

    def action_quality_check(self):
        for rec in self:
            if rec.state != 'in_progress':
                raise UserError(_('Batch must be in production to move to quality check.'))
            rec.write({'state': 'quality_check'})
            rec.message_post(body=_('Batch moved to quality check stage.'))

    def action_done(self):
        for rec in self:
            if rec.state not in ('quality_check', 'in_progress'):
                raise UserError(_('Batch must be in quality check or in production to be marked as done.'))
            if not any(l.actual_qty > 0 for l in rec.output_line_ids):
                raise UserError(_('Please enter actual output quantities.'))
            total_output = sum(rec.output_line_ids.mapped('actual_qty'))
            rec.write({
                'state': 'done',
                'date_end': fields.Datetime.now(),
                'actual_yield': total_output,
            })
            rec.message_post(body=_('Batch completed. Total yield: %.2f kg') % total_output)

    def action_fail(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_('Completed batches cannot be failed.'))
            rec.write({'state': 'failed'})
            rec.message_post(body=_('Batch marked as failed/scrapped.'))

    def action_cancel(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_('Completed batches cannot be cancelled.'))
            rec.write({'state': 'cancelled'})

    def action_reset_draft(self):
        for rec in self:
            if rec.state not in ('confirmed', 'cancelled', 'failed'):
                raise UserError(_('Only confirmed, cancelled or failed batches can be reset.'))
            rec.write({'state': 'draft', 'date_start': False, 'date_end': False})

    def action_create_quality_check(self):
        self.ensure_one()
        qc = self.env['sweet.quality.check'].create({
            'batch_id': self.id,
            'recipe_id': self.recipe_id.id,
            'check_date': fields.Datetime.now(),
            'inspector_id': self.env.uid,
            'line_ids': [(0, 0, {
                'parameter_id': param.id,
                'uom': param.uom,
                'min_value': param.min_value,
                'max_value': param.max_value,
            }) for param in self.recipe_id.quality_parameter_ids],
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Quality Check'),
            'res_model': 'sweet.quality.check',
            'res_id': qc.id,
            'view_mode': 'form',
        }

    def action_view_quality_checks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Quality Checks'),
            'res_model': 'sweet.quality.check',
            'domain': [('batch_id', '=', self.id)],
            'view_mode': 'list,form',
        }

    def action_print_batch_report(self):
        return self.env.ref('sweet_factory_management.action_report_sweet_batch').report_action(self)
