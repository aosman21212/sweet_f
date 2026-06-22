from odoo import models, fields, api


class SweetBatchOutputLine(models.Model):
    _name = 'sweet.batch.output.line'
    _description = 'Batch Output / Finished Product Line'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    batch_id = fields.Many2one('sweet.batch', string='Batch', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_uom_id = fields.Many2one('uom.uom', string='UoM', related='product_id.uom_id', store=True)

    planned_qty = fields.Float(string='Planned Qty', digits='Product Unit of Measure', default=1.0)
    actual_qty = fields.Float(string='Actual Qty', digits='Product Unit of Measure')

    # Packaging
    packaging_type = fields.Selection([
        ('bulk', 'Bulk (kg)'),
        ('box', 'Box'),
        ('bag', 'Bag / Pouch'),
        ('tin', 'Tin / Can'),
        ('jar', 'Jar'),
        ('wrapper', 'Individual Wrapper'),
        ('display_box', 'Display Box'),
        ('gift_box', 'Gift Box'),
    ], string='Packaging', default='bulk')
    pieces_per_kg = fields.Float(string='Pieces per kg',
                                 help='Number of individual pieces per kg (for counting)')
    total_pieces = fields.Float(string='Total Pieces', compute='_compute_total_pieces', store=True)

    # Quality grade
    grade = fields.Selection([
        ('a_plus', 'Premium (A+)'),
        ('a', 'Grade A'),
        ('b', 'Grade B (Seconds)'),
        ('reject', 'Reject / Scrap'),
    ], string='Grade', default='a')

    # Lot
    lot_id = fields.Many2one('stock.lot', string='Lot/Serial', domain="[('product_id', '=', product_id)]")
    expiry_date = fields.Date(string='Expiry Date', related='batch_id.expiry_date', store=True)

    notes = fields.Char(string='Notes')
    state = fields.Selection(related='batch_id.state')

    @api.depends('actual_qty', 'pieces_per_kg')
    def _compute_total_pieces(self):
        for line in self:
            if line.pieces_per_kg:
                line.total_pieces = line.actual_qty * line.pieces_per_kg
            else:
                line.total_pieces = 0.0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.batch_id.recipe_id and self.batch_id.recipe_id.product_id:
            if self.product_id == self.batch_id.recipe_id.product_id:
                self.planned_qty = self.batch_id.planned_qty
