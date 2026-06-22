from odoo import models, fields, api


class SweetBatchIngredientLine(models.Model):
    _name = 'sweet.batch.ingredient.line'
    _description = 'Batch Ingredient Consumption Line'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    batch_id = fields.Many2one('sweet.batch', string='Batch', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Ingredient', required=True)
    product_uom_id = fields.Many2one('uom.uom', string='UoM', related='product_id.uom_id', store=True)
    ingredient_type = fields.Selection([
        ('sugar', 'Sugar'),
        ('glucose', 'Glucose/Corn Syrup'),
        ('fat', 'Fat/Oil/Butter'),
        ('flavor', 'Flavor/Essence'),
        ('color', 'Color/Dye'),
        ('acid', 'Acid'),
        ('gelling', 'Gelling Agent'),
        ('emulsifier', 'Emulsifier'),
        ('preservative', 'Preservative'),
        ('nut', 'Nuts/Seeds'),
        ('fruit', 'Fruit'),
        ('dairy', 'Dairy'),
        ('chocolate', 'Chocolate/Cocoa'),
        ('other', 'Other'),
    ], string='Type', default='other')

    planned_qty = fields.Float(string='Planned Qty', digits='Product Unit of Measure', default=1.0)
    actual_qty = fields.Float(string='Actual Qty', digits='Product Unit of Measure')
    variance = fields.Float(string='Variance', compute='_compute_variance', store=True)

    lot_id = fields.Many2one('stock.lot', string='Lot', domain="[('product_id', '=', product_id)]")
    cost_per_unit = fields.Float(string='Cost/Unit', digits='Product Price')
    line_cost = fields.Float(string='Cost', compute='_compute_line_cost', store=True, digits='Product Price')
    notes = fields.Char(string='Notes')
    state = fields.Selection(related='batch_id.state')

    @api.depends('actual_qty', 'planned_qty')
    def _compute_variance(self):
        for line in self:
            line.variance = line.actual_qty - line.planned_qty

    @api.depends('actual_qty', 'cost_per_unit')
    def _compute_line_cost(self):
        for line in self:
            line.line_cost = line.actual_qty * line.cost_per_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.cost_per_unit = self.product_id.standard_price
