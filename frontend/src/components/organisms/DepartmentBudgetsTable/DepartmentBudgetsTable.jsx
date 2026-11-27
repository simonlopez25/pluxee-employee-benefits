import { Badge } from '../../atoms/Badge/Badge'
import { Button } from '../../atoms/Button'
import { Icon } from '../../atoms/Icon'
import { ProgressBar } from '../../molecules/ProgressBar'
import { formatCurrency } from '../../../utils/format'
import './DepartmentBudgetsTable.css'

export function DepartmentBudgetsTable({ departments = [], onEditDepartment }) {
  if (departments.length === 0) {
    return (
      <div className="deptTableEmptyState">
        <Icon name="groups" size={32} className="deptTableEmptyIcon" />
        <h3 className="deptTableEmptyTitle">No hay departamentos activos</h3>
        <p className="deptTableEmptySubtitle">
          Crea departamentos desde la sección de administración para asignarles presupuestos.
        </p>
      </div>
    )
  }

  return (
    <div className="deptTableCard">
      <div className="deptTableHeaderRow">
        <h2 className="deptTableTitle">Presupuestos por Departamento</h2>
        <span className="deptTableCountBadge">{departments.length} grupos</span>
      </div>

      <div className="deptTableResponsiveWrapper">
        <table className="deptTable">
          <thead>
            <tr>
              <th className="deptTh">Grupo</th>
              <th className="deptTh">Asignado</th>
              <th className="deptTh">Disponible</th>
              <th className="deptTh">Consumido</th>
              <th className="deptTh deptThUsage">Uso del asignado</th>
              <th className="deptTh deptThActions">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {departments.map((dept) => {
              const hasBudget = dept.allocatedAmount > 0
              const references = dept.benefitReferences || []

              return (
                <tr key={dept.departmentId} className="deptTr">
                  <td className="deptTd deptTdName">
                    <div className="deptNameContainer">
                      <span className="deptGroupName">{dept.departmentName}</span>
                      {!hasBudget && (
                        <Badge variant="inactive" className="deptUnassignedBadge">
                          Sin asignar
                        </Badge>
                      )}
                      {references.length > 0 && (
                        <div className="deptReferencesList">
                          {references.map((ref) => (
                            <span
                              key={ref.benefitId}
                              className="deptReferencePill"
                            >
                              {ref.benefitName}: {formatCurrency(ref.indicativeAmount)}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </td>

                  <td className="deptTd deptTdAmount">
                    <span className="deptAmountText">
                      {formatCurrency(dept.allocatedAmount)}
                    </span>
                  </td>

                  <td className="deptTd deptTdAmount">
                    <span
                      className={`deptAmountText ${
                        dept.availableAmount < 0 ? 'deptAmountNegative' : ''
                      }`}
                    >
                      {formatCurrency(dept.availableAmount)}
                    </span>
                  </td>

                  <td className="deptTd deptTdAmount">
                    <span className="deptAmountText">
                      {formatCurrency(dept.consumedAmount)}
                    </span>
                  </td>

                  <td className="deptTd deptTdProgress">
                    <ProgressBar
                      value={dept.usagePercentage}
                      max={100}
                      showLabel={true}
                    />
                  </td>

                  <td className="deptTd deptTdActions">
                    <Button
                      variant={hasBudget ? 'outline' : 'secondary'}
                      size="sm"
                      onClick={() => onEditDepartment(dept)}
                      icon={
                        <Icon name={hasBudget ? 'edit' : 'plus'} size={14} />
                      }
                    >
                      {hasBudget ? 'Configurar' : 'Asignar'}
                    </Button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
