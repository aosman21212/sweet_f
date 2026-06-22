from odoo import models, api
from datetime import date


class SweetDashboard(models.AbstractModel):
    _name = 'sweet.dashboard'
    _description = 'Sweet Factory Dashboard'

    @api.model
    def get_dashboard_data(self):
        today = date.today()
        month_start = today.replace(day=1)

        Batch = self.env['sweet.batch']
        Recipe = self.env['sweet.recipe']
        QC = self.env['sweet.quality.check']
        Machine = self.env['sweet.machine']

        # ── Recipes ─────────────────────────────────────
        total_recipes = Recipe.search_count([])
        active_recipes = Recipe.search_count([('state', '=', 'approved')])
        draft_recipes = Recipe.search_count([('state', '=', 'draft')])

        # ── Batches ──────────────────────────────────────
        batches_draft = Batch.search_count([('state', '=', 'draft')])
        batches_confirmed = Batch.search_count([('state', '=', 'confirmed')])
        batches_in_progress = Batch.search_count([('state', '=', 'in_progress')])
        batches_quality_check = Batch.search_count([('state', '=', 'quality_check')])
        batches_done = Batch.search_count([('state', '=', 'done')])
        batches_failed = Batch.search_count([('state', 'in', ['failed', 'cancelled'])])
        batches_this_month = Batch.search_count([
            ('date_planned', '>=', month_start.strftime('%Y-%m-%d 00:00:00'))
        ])

        # ── Quality Checks ───────────────────────────────
        qc_passed = QC.search_count([('result', '=', 'pass')])
        qc_failed = QC.search_count([('result', '=', 'fail')])
        qc_conditional = QC.search_count([('result', '=', 'conditional')])
        qc_pending = QC.search_count([('result', '=', 'pending')])

        # ── Machines ─────────────────────────────────────
        machines_available = Machine.search_count([('state', '=', 'available')])
        machines_running = Machine.search_count([('state', '=', 'running')])
        machines_maintenance = Machine.search_count([('state', '=', 'maintenance')])
        machines_breakdown = Machine.search_count([('state', '=', 'breakdown')])

        # ── Avg Yield (done batches) ──────────────────────
        done_batches = Batch.search([('state', '=', 'done'), ('yield_percentage_actual', '>', 0)])
        avg_yield = (
            sum(done_batches.mapped('yield_percentage_actual')) / len(done_batches)
            if done_batches else 0.0
        )

        # ── Recent Batches ────────────────────────────────
        recent_batches = Batch.search([], order='id desc', limit=8)
        recent_batches_data = []
        for b in recent_batches:
            recent_batches_data.append({
                'id': b.id,
                'name': b.name,
                'recipe': b.recipe_id.name if b.recipe_id else '',
                'state': b.state,
                'yield_pct': round(b.yield_percentage_actual, 1),
                'planned_date': b.date_planned.strftime('%Y-%m-%d') if b.date_planned else '',
            })

        return {
            # Recipes
            'total_recipes': total_recipes,
            'active_recipes': active_recipes,
            'draft_recipes': draft_recipes,
            # Batches
            'batches_draft': batches_draft,
            'batches_confirmed': batches_confirmed,
            'batches_in_progress': batches_in_progress,
            'batches_quality_check': batches_quality_check,
            'batches_done': batches_done,
            'batches_failed': batches_failed,
            'batches_this_month': batches_this_month,
            # QC
            'qc_passed': qc_passed,
            'qc_failed': qc_failed,
            'qc_conditional': qc_conditional,
            'qc_pending': qc_pending,
            # Machines
            'machines_available': machines_available,
            'machines_running': machines_running,
            'machines_maintenance': machines_maintenance,
            'machines_breakdown': machines_breakdown,
            # KPIs
            'avg_yield': round(avg_yield, 1),
            # Recent
            'recent_batches': recent_batches_data,
        }
