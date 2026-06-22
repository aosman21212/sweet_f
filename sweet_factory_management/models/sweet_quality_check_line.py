from odoo import models, fields, api


class SweetQualityCheckLine(models.Model):
    _name = 'sweet.quality.check.line'
    _description = 'Quality Check Parameter Result'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    check_id = fields.Many2one('sweet.quality.check', string='Quality Check', required=True, ondelete='cascade')
    parameter_id = fields.Many2one('sweet.quality.parameter', string='Parameter', required=True)
    category = fields.Selection(related='parameter_id.category', store=True)
    parameter_type = fields.Selection(related='parameter_id.parameter_type', store=True)

    uom = fields.Char(string='UoM')
    min_value = fields.Float(string='Min')
    max_value = fields.Float(string='Max')
    measured_value = fields.Float(string='Measured Value')
    text_value = fields.Char(string='Result Text')
    boolean_value = fields.Boolean(string='Pass?')

    result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('na', 'N/A'),
    ], string='Result', default='na', compute='_compute_result', store=True)

    notes = fields.Char(string='Notes')

    @api.depends('parameter_type', 'measured_value', 'min_value', 'max_value', 'boolean_value')
    def _compute_result(self):
        for line in self:
            if line.parameter_type == 'numeric':
                if line.measured_value == 0:
                    line.result = 'na'
                elif line.min_value <= line.measured_value <= line.max_value:
                    line.result = 'pass'
                else:
                    line.result = 'fail'
            elif line.parameter_type == 'boolean':
                line.result = 'pass' if line.boolean_value else 'fail'
            else:
                line.result = 'pass' if line.text_value else 'na'

    @api.onchange('parameter_id')
    def _onchange_parameter_id(self):
        if self.parameter_id:
            self.uom = self.parameter_id.uom
            self.min_value = self.parameter_id.min_value
            self.max_value = self.parameter_id.max_value
