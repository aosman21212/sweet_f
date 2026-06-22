from odoo import models, fields, api


class SweetRecipeIngredient(models.Model):
    _name = 'sweet.recipe.ingredient'
    _description = 'Sweet Recipe Ingredient'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    recipe_id = fields.Many2one('sweet.recipe', string='Recipe', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Ingredient', required=True)
    product_uom_id = fields.Many2one('uom.uom', string='UoM', related='product_id.uom_id', store=True)

    quantity_per_batch = fields.Float(string='Qty per Batch', default=1.0,
                                      help='Quantity needed for one standard batch')
    percentage = fields.Float(string='% of Batch', compute='_compute_percentage', store=True)

    is_key_ingredient = fields.Boolean(string='Key Ingredient')

    ingredient_type = fields.Selection([
        ('sugar', 'Sugar'),
        ('glucose', 'Glucose/Corn Syrup'),
        ('fat', 'Fat/Oil/Butter'),
        ('flavor', 'Flavor/Essence'),
        ('color', 'Color/Dye'),
        ('acid', 'Acid (Citric, Tartaric)'),
        ('gelling', 'Gelling Agent (Gelatin, Pectin)'),
        ('emulsifier', 'Emulsifier'),
        ('preservative', 'Preservative'),
        ('nut', 'Nuts/Seeds'),
        ('fruit', 'Fruit/Fruit Pulp'),
        ('dairy', 'Dairy (Milk, Cream)'),
        ('chocolate', 'Chocolate/Cocoa'),
        ('other', 'Other'),
    ], string='Type', default='other')

    cost_per_unit = fields.Float(string='Cost/Unit', compute='_compute_cost', store=True)
    line_cost = fields.Float(string='Line Cost', compute='_compute_line_cost', store=True)
    notes = fields.Char(string='Notes')

    @api.depends('quantity_per_batch', 'recipe_id.standard_batch_qty')
    def _compute_percentage(self):
        for line in self:
            if line.recipe_id.standard_batch_qty:
                line.percentage = (line.quantity_per_batch / line.recipe_id.standard_batch_qty) * 100
            else:
                line.percentage = 0.0

    @api.depends('product_id')
    def _compute_cost(self):
        for line in self:
            line.cost_per_unit = line.product_id.standard_price if line.product_id else 0.0

    @api.depends('quantity_per_batch', 'cost_per_unit')
    def _compute_line_cost(self):
        for line in self:
            line.line_cost = line.quantity_per_batch * line.cost_per_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.cost_per_unit = self.product_id.standard_price
