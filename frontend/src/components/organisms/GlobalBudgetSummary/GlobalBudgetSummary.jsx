import { Button } from '../../atoms/Button'
import { Icon } from '../../atoms/Icon'
import { MonthSelector } from '../../molecules/MonthSelector'
import { ProgressBar } from '../../molecules/ProgressBar'
import { formatCurrency } from '../../../utils/format'
import './GlobalBudgetSummary.css'

export function GlobalBudgetSummary({
  overview,
  selectedPeriod,
  onPeriodChange,
  onOpenConfigureGlobal,
}) {
  const currentDate = new Date(selectedPeriod)
  const year = currentDate.getFullYear()

  const totalAmount = overview?.totalAmount || 0
  const allocatedToDepartments = overview?.allocatedToDepartments || 0
  const unallocatedAmount = overview?.unallocatedAmount || 0

  const allocatedPercentage =
    totalAmount > 0 ? (allocatedToDepartments / totalAmount) * 100 : 0

  return (
    <section className="budgetSummarySection">
      <header className="budgetSummaryHeader">
        <div className="budgetSummaryHeaderContent">
          <h1 className="budgetSummaryTitle">Presupuestos</h1>
          <p className="budgetSummarySubtitle">
            Ejercicio {year} · Presupuesto mensual, saldo asignado y consumo real.
          </p>
        </div>

        <div className="budgetSummaryHeaderActions">
          <MonthSelector
            selectedPeriod={selectedPeriod}
            onPeriodChange={onPeriodChange}
          />
          <Button
            variant="secondary"
            size="md"
            onClick={onOpenConfigureGlobal}
            icon={<Icon name="wallet" size={18} />}
          >
            Configurar presupuesto global
          </Button>
        </div>
      </header>

      <div className="budgetPeriodNotice">
        <Icon name="info" size={16} className="budgetPeriodNoticeIcon" />
        <span className="budgetPeriodNoticeText">
          Periodo mensual no acumulativo: el saldo no utilizado no pasa al mes siguiente.
        </span>
      </div>

      <div className="budgetMetricsGrid">
        <article className="budgetMetricCard">
          <div className="budgetMetricHeader">
            <span className="budgetMetricLabel">Presupuesto global</span>
            <div className="budgetMetricIconWrapper">
              <Icon name="wallet" size={20} />
            </div>
          </div>
          <div className="budgetMetricValue">{formatCurrency(totalAmount)}</div>
          <span className="budgetMetricHint">Techo mensual disponible</span>
        </article>

        <article className="budgetMetricCard">
          <div className="budgetMetricHeader">
            <span className="budgetMetricLabel">Repartido a grupos</span>
            <div className="budgetMetricIconWrapper">
              <Icon name="groups" size={20} />
            </div>
          </div>
          <div className="budgetMetricValue">
            {formatCurrency(allocatedToDepartments)}
          </div>
          <span className="budgetMetricHint">
            Suma de asignaciones departamentales
          </span>
        </article>

        <article className="budgetMetricCard">
          <div className="budgetMetricHeader">
            <span className="budgetMetricLabel">Sin repartir (Disponible)</span>
            <div className="budgetMetricIconWrapper">
              <Icon name="piggyBank" size={20} />
            </div>
          </div>
          <div
            className={`budgetMetricValue ${
              unallocatedAmount < 0 ? 'budgetMetricValueNegative' : ''
            }`}
          >
            {formatCurrency(unallocatedAmount)}
          </div>
          <span className="budgetMetricHint">
            Margen libre para nuevos grupos
          </span>
        </article>

        <article className="budgetMetricCard">
          <div className="budgetMetricHeader">
            <span className="budgetMetricLabel">Distribución global</span>
            <div className="budgetMetricIconWrapper">
              <Icon name="dashboard" size={20} />
            </div>
          </div>
          <div className="budgetMetricProgressWrapper">
            <ProgressBar value={allocatedPercentage} max={100} showLabel={true} />
          </div>
          <span className="budgetMetricHint">
            {allocatedPercentage.toFixed(1)}% repartido del global
          </span>
        </article>
      </div>
    </section>
  )
}
