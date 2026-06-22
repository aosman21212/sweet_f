from odoo import models, fields, api


class SweetMachineLog(models.Model):
    _name = 'sweet.machine.log'
    _description = 'Machine Usage / Maintenance Log'
    _order = 'log_date desc, id desc'

    machine_id = fields.Many2one('sweet.machine', string='Machine', required=True, ondelete='cascade')
    batch_id = fields.Many2one('sweet.batch', string='Production Batch')

    log_type = fields.Selection([
        ('production', 'Production Run'),
        ('maintenance', 'Maintenance'),
        ('inspection', 'Inspection'),
        ('cleaning', 'Cleaning / Sanitation'),
        ('breakdown', 'Breakdown'),
        ('repair', 'Repair'),
    ], string='Type', required=True, default='production')

    log_date = fields.Datetime(string='Date', default=fields.Datetime.now, required=True)
    end_date = fields.Datetime(string='End Date')
    duration_hours = fields.Float(string='Duration (hrs)', compute='_compute_duration', store=True)

    performed_by = fields.Many2one('res.users', string='Performed By', default=lambda self: self.env.uid)
    description = fields.Text(string='Description')

    issue_found = fields.Char(string='Issue Found')
    action_taken = fields.Char(string='Action Taken')

    # Production metrics
    qty_produced = fields.Float(string='Qty Produced (kg)')
    downtime_minutes = fields.Integer(string='Downtime (min)')

    @api.depends('log_date', 'end_date')
    def _compute_duration(self):
        for rec in self:
            if rec.log_date and rec.end_date:
                delta = rec.end_date - rec.log_date
                rec.duration_hours = delta.total_seconds() / 3600
            else:
                rec.duration_hours = 0.0
