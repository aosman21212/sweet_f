from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SweetRecipe(models.Model):
    _name = 'sweet.recipe'
    _description = 'Sweet Recipe / Formula'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Recipe Name', required=True, tracking=True)
    code = fields.Char(string='Recipe Code', copy=False)

    sweet_type = fields.Selection([
        ('hard_candy', 'Hard Candy'),
        ('soft_candy', 'Soft Candy / Toffee'),
        ('chocolate', 'Chocolate'),
        ('gummy', 'Gummy / Jelly'),
        ('lollipop', 'Lollipop'),
        ('marshmallow', 'Marshmallow'),
        ('caramel', 'Caramel'),
        ('nougat', 'Nougat'),
        ('fudge', 'Fudge'),
        ('praline', 'Praline'),
        ('other', 'Other'),
    ], string='Sweet Type', required=True, tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('archived', 'Archived'),
    ], string='Status', default='draft', tracking=True)

    # Standard batch size
    standard_batch_qty = fields.Float(string='Standard Batch Size (kg)', default=100.0)
    product_id = fields.Many2one('product.product', string='Finished Product',
                                 domain=[('type', 'in', ['consu', 'product'])])
    yield_percentage = fields.Float(string='Yield %', default=95.0,
                                    help='Expected output vs input, e.g. 95 means 95% of input becomes product')

    # Nutritional info
    calories_per_100g = fields.Float(string='Calories per 100g')
    sugar_content = fields.Float(string='Sugar Content %')
    fat_content = fields.Float(string='Fat Content %')

    # Allergens
    contains_nuts = fields.Boolean(string='Contains Nuts')
    contains_dairy = fields.Boolean(string='Contains Dairy')
    contains_gluten = fields.Boolean(string='Contains Gluten')
    contains_eggs = fields.Boolean(string='Contains Eggs')
    contains_soy = fields.Boolean(string='Contains Soy')

    # Shelf life
    shelf_life_days = fields.Integer(string='Shelf Life (days)', default=365)
    storage_temp = fields.Char(string='Storage Temperature')

    # Process parameters
    cooking_temp = fields.Float(string='Cooking Temperature (°C)')
    cooking_duration = fields.Integer(string='Cooking Duration (min)')
    cooling_temp = fields.Float(string='Cooling Temperature (°C)')

    # Ingredients
    ingredient_ids = fields.One2many('sweet.recipe.ingredient', 'recipe_id', string='Ingredients')
    ingredient_count = fields.Integer(compute='_compute_ingredient_count', string='# Ingredients')

    # Quality parameters
    quality_parameter_ids = fields.Many2many('sweet.quality.parameter', string='Quality Parameters')

    # Batches
    batch_ids = fields.One2many('sweet.batch', 'recipe_id', string='Production Batches')
    batch_count = fields.Integer(compute='_compute_batch_count', string='# Batches')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', store=True)
    notes = fields.Html(string='Instructions')

    # Cost estimate
    estimated_cost_per_kg = fields.Float(string='Est. Cost/kg', compute='_compute_estimated_cost', store=True)

    @api.depends('ingredient_ids', 'ingredient_ids.cost_per_unit', 'ingredient_ids.quantity_per_batch', 'standard_batch_qty')
    def _compute_estimated_cost(self):
        for rec in self:
            if rec.standard_batch_qty:
                total_ingredient_cost = sum(
                    (line.quantity_per_batch * line.cost_per_unit) for line in rec.ingredient_ids
                )
                rec.estimated_cost_per_kg = total_ingredient_cost / rec.standard_batch_qty
            else:
                rec.estimated_cost_per_kg = 0.0

    @api.depends('ingredient_ids')
    def _compute_ingredient_count(self):
        for rec in self:
            rec.ingredient_count = len(rec.ingredient_ids)

    @api.depends('batch_ids')
    def _compute_batch_count(self):
        for rec in self:
            rec.batch_count = len(rec.batch_ids)

    def action_approve(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft recipes can be approved.'))
            if not rec.ingredient_ids:
                raise UserError(_('Please add ingredients before approving.'))
            rec.write({'state': 'approved'})
            rec.message_post(body=_('Recipe approved for production.'))

    def action_archive(self):
        self.write({'state': 'archived'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_view_batches(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Production Batches'),
            'res_model': 'sweet.batch',
            'domain': [('recipe_id', '=', self.id)],
            'view_mode': 'list,form',
        }
