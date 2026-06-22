from odoo import models, fields, api, _


class SweetBatchCloseWizard(models.TransientModel):
    _name = 'sweet.batch.close.wizard'
    _description = 'Batch Completion Wizard'

    batch_id = fields.Many2one('sweet.batch', string='Batch', required=True)
    actual_yield = fields.Float(string='Total Yield (kg)')
    actual_cooking_temp = fields.Float(string='Actual Cooking Temp (°C)')
    actual_cooling_temp = fields.Float(string='Actual Cooling Temp (°C)')
    actual_duration = fields.Integer(string='Actual Duration (min)')

    quality_result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('conditional', 'Conditional Pass'),
    ], string='QC Result', default='pass', required=True)

    remarks = fields.Text(string='Remarks')

    def action_complete_batch(self):
        self.ensure_one()
        batch = self.batch_id
        batch.write({
            'actual_yield': self.actual_yield,
            'actual_cooking_temp': self.actual_cooking_temp,
            'actual_cooling_temp': self.actual_cooling_temp,
            'actual_duration': self.actual_duration,
            'state': 'done',
            'date_end': fields.Datetime.now(),
        })
        batch.message_post(
            body=_('Batch completed via wizard. Yield: %.2f kg. QC: %s') % (
                self.actual_yield,
                dict(self._fields['quality_result'].selection).get(self.quality_result, ''),
            )
        )
        return {'type': 'ir.actions.act_window_close'}
