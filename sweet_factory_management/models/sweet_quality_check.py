from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SweetQualityCheck(models.Model):
    _name = 'sweet.quality.check'
    _description = 'Quality Control Inspection'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'check_date desc, id desc'

    name = fields.Char(string='Reference', readonly=True, copy=False, default='New')
    batch_id = fields.Many2one('sweet.batch', string='Batch', required=True)
    recipe_id = fields.Many2one('sweet.recipe', string='Recipe', related='batch_id.recipe_id', store=True)
    sweet_type = fields.Selection(related='batch_id.sweet_type', store=True)

    check_date = fields.Datetime(string='Check Date', default=fields.Datetime.now, required=True)
    inspector_id = fields.Many2one('res.users', string='Inspector', default=lambda self: self.env.uid, required=True)

    check_stage = fields.Selection([
        ('in_process', 'In-Process Check'),
        ('final', 'Final Product Check'),
        ('packaging', 'Packaging Check'),
    ], string='Check Stage', default='final', required=True)

    result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('conditional', 'Conditional Pass'),
        ('pending', 'Pending'),
    ], string='Result', default='pending', tracking=True)

    line_ids = fields.One2many('sweet.quality.check.line', 'check_id', string='Parameters')

    # Sensory evaluation
    taste_score = fields.Integer(string='Taste Score (1-10)')
    color_score = fields.Integer(string='Color Score (1-10)')
    texture_score = fields.Integer(string='Texture Score (1-10)')
    aroma_score = fields.Integer(string='Aroma Score (1-10)')
    overall_score = fields.Float(string='Overall Score', compute='_compute_overall_score', store=True)

    # Defects
    defect_type = fields.Selection([
        ('none', 'No Defects'),
        ('color', 'Color Defect'),
        ('size', 'Size/Shape Defect'),
        ('texture', 'Texture Defect'),
        ('taste', 'Taste/Flavor Defect'),
        ('contamination', 'Contamination'),
        ('packaging', 'Packaging Defect'),
        ('other', 'Other'),
    ], string='Defect Type', default='none')
    defect_qty = fields.Float(string='Defect Qty (kg)')

    remarks = fields.Text(string='Remarks')
    corrective_action = fields.Text(string='Corrective Action')

    @api.depends('taste_score', 'color_score', 'texture_score', 'aroma_score')
    def _compute_overall_score(self):
        for rec in self:
            scores = [s for s in [rec.taste_score, rec.color_score, rec.texture_score, rec.aroma_score] if s]
            rec.overall_score = sum(scores) / len(scores) if scores else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('sweet.quality.check') or 'New'
        return super().create(vals_list)

    def action_pass(self):
        for rec in self:
            if any(l.result == 'fail' for l in rec.line_ids):
                raise UserError(_('Cannot pass: some parameters have failed results.'))
            rec.write({'result': 'pass'})
            rec.message_post(body=_('Quality check PASSED.'))

    def action_fail(self):
        for rec in self:
            rec.write({'result': 'fail'})
            rec.message_post(body=_('Quality check FAILED.'))

    def action_conditional_pass(self):
        self.write({'result': 'conditional'})
