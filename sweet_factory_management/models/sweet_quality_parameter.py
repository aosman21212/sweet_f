from odoo import models, fields


class SweetQualityParameter(models.Model):
    _name = 'sweet.quality.parameter'
    _description = 'Quality Check Parameter'
    _order = 'sequence, name'

    name = fields.Char(string='Parameter Name', required=True)
    code = fields.Char(string='Code')
    sequence = fields.Integer(default=10)

    category = fields.Selection([
        ('physical', 'Physical'),
        ('chemical', 'Chemical'),
        ('microbiological', 'Microbiological'),
        ('sensory', 'Sensory / Organoleptic'),
        ('weight', 'Weight'),
        ('packaging', 'Packaging'),
    ], string='Category', required=True, default='physical')

    parameter_type = fields.Selection([
        ('numeric', 'Numeric (Range)'),
        ('boolean', 'Pass/Fail'),
        ('text', 'Text Description'),
    ], string='Type', required=True, default='numeric')

    uom = fields.Char(string='Unit of Measure', help='e.g. %, °C, g, brix')
    min_value = fields.Float(string='Min Value')
    max_value = fields.Float(string='Max Value')
    target_value = fields.Float(string='Target Value')

    description = fields.Text(string='Description / Method')
    active = fields.Boolean(default=True)
