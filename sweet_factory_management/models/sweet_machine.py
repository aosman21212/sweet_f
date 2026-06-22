from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SweetMachine(models.Model):
    _name = 'sweet.machine'
    _description = 'Production Machine / Equipment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Machine Name', required=True, tracking=True)
    code = fields.Char(string='Machine Code')

    machine_type = fields.Selection([
        ('cooker', 'Sugar Cooker / Kettle'),
        ('mixer', 'Mixer / Blender'),
        ('extruder', 'Extruder / Former'),
        ('wrapper', 'Wrapping Machine'),
        ('depositor', 'Depositor / Moulding'),
        ('cooling', 'Cooling Tunnel / Belt'),
        ('coating', 'Coating / Enrobing'),
        ('packaging', 'Packaging Machine'),
        ('conveyor', 'Conveyor Belt'),
        ('weigher', 'Weighing Machine'),
        ('other', 'Other'),
    ], string='Machine Type', required=True)

    state = fields.Selection([
        ('available', 'Available'),
        ('running', 'Running'),
        ('maintenance', 'Under Maintenance'),
        ('breakdown', 'Breakdown'),
        ('retired', 'Retired'),
    ], string='Status', default='available', tracking=True)

    manufacturer = fields.Char(string='Manufacturer')
    model_number = fields.Char(string='Model Number')
    serial_number = fields.Char(string='Serial Number')
    purchase_date = fields.Date(string='Purchase Date')
    capacity_per_hour = fields.Float(string='Capacity (kg/hour)')

    location = fields.Char(string='Location / Section')

    # Maintenance
    last_maintenance_date = fields.Date(string='Last Maintenance Date', tracking=True)
    next_maintenance_date = fields.Date(string='Next Maintenance Date', tracking=True)
    maintenance_interval_days = fields.Integer(string='Maintenance Interval (days)', default=30)

    # Log
    log_ids = fields.One2many('sweet.machine.log', 'machine_id', string='Usage / Maintenance Logs')
    log_count = fields.Integer(compute='_compute_log_count', string='Logs')
    total_runtime_hours = fields.Float(compute='_compute_total_runtime', string='Total Runtime (hrs)', store=True)

    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)

    @api.depends('log_ids')
    def _compute_log_count(self):
        for rec in self:
            rec.log_count = len(rec.log_ids)

    @api.depends('log_ids', 'log_ids.duration_hours')
    def _compute_total_runtime(self):
        for rec in self:
            rec.total_runtime_hours = sum(
                l.duration_hours for l in rec.log_ids if l.log_type == 'production'
            )

    def action_start_maintenance(self):
        for rec in self:
            rec.write({'state': 'maintenance'})
            self.env['sweet.machine.log'].create({
                'machine_id': rec.id,
                'log_type': 'maintenance',
                'log_date': fields.Datetime.now(),
                'performed_by': self.env.uid,
                'description': 'Maintenance started',
            })
            rec.message_post(body=_('Machine moved to maintenance.'))

    def action_set_available(self):
        for rec in self:
            rec.write({
                'state': 'available',
                'last_maintenance_date': fields.Date.today(),
            })
            rec.message_post(body=_('Machine is now available.'))

    def action_report_breakdown(self):
        for rec in self:
            rec.write({'state': 'breakdown'})
            rec.message_post(body=_('Machine breakdown reported.'))

    def action_view_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Machine Logs'),
            'res_model': 'sweet.machine.log',
            'domain': [('machine_id', '=', self.id)],
            'view_mode': 'list,form',
        }
