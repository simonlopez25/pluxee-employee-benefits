import { useEffect, useMemo, useState } from 'react'
import { AdminLayout } from '../../components/templates/AdminLayout'
import { GlobalBudgetSummary } from '../../components/organisms/GlobalBudgetSummary'
import { GlobalBudgetModal } from '../../components/organisms/GlobalBudgetModal'
import { DepartmentBudgetsTable } from '../../components/organisms/DepartmentBudgetsTable'
import { DepartmentBudgetModal } from '../../components/organisms/DepartmentBudgetModal'
import { Icon } from '../../components/atoms/Icon'
import { Button } from '../../components/atoms/Button'
import {
  getActiveBenefits,
  getActiveDepartments,
  getMonthlyBudgets,
  saveBenefitReferences,
  saveDepartmentBudget,
  saveGlobalBudget,
} from '../../services/budgetService'
import './BudgetsPage.css'

const getInitialPeriod = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}-01`
}

export function BudgetsPage() {
  const [selectedPeriod, setSelectedPeriod] = useState(getInitialPeriod)
  const [overview, setOverview] = useState(null)
  const [activeDepartments, setActiveDepartments] = useState([])
  const [activeBenefits, setActiveBenefits] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState(null)
  const [successMessage, setSuccessMessage] = useState(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const [isGlobalModalOpen, setIsGlobalModalOpen] = useState(false)
  const [isSubmittingGlobal, setIsSubmittingGlobal] = useState(false)
  const [globalApiError, setGlobalApiError] = useState(null)

  const [isDeptModalOpen, setIsDeptModalOpen] = useState(false)
  const [selectedDeptForModal, setSelectedDeptForModal] = useState(null)
  const [isSubmittingDept, setIsSubmittingDept] = useState(false)
  const [deptApiError, setDeptApiError] = useState(null)

  useEffect(() => {
    let isCancelled = false
    const loadBudgetData = async () => {
      try {
        const [overviewData, deptsData, benefitsData] = await Promise.all([
          getMonthlyBudgets(selectedPeriod),
          getActiveDepartments(),
          getActiveBenefits(),
        ])

        if (!isCancelled) {
          setOverview(overviewData)
          setActiveDepartments(deptsData)
          setActiveBenefits(benefitsData)
          setErrorMessage(null)
        }
      } catch (error) {
        if (!isCancelled) {
          setErrorMessage(
            error.message || 'Error al cargar los presupuestos del mes'
          )
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadBudgetData()

    return () => {
      isCancelled = true
    }
  }, [selectedPeriod, refreshTrigger])

  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => {
        setSuccessMessage(null)
      }, 4000)
      return () => clearTimeout(timer)
    }
  }, [successMessage])

  const mergedDepartments = useMemo(() => {
    if (!activeDepartments || activeDepartments.length === 0) {
      return overview?.departments || []
    }

    const budgetMap = new Map()
    if (overview?.departments) {
      overview.departments.forEach((dept) => {
        budgetMap.set(dept.departmentId, dept)
      })
    }

    return activeDepartments.map((dept) => {
      if (budgetMap.has(dept.id)) {
        return budgetMap.get(dept.id)
      }
      return {
        id: `unallocated-${dept.id}`,
        departmentId: dept.id,
        departmentName: dept.name,
        period: selectedPeriod,
        allocatedAmount: 0,
        consumedAmount: 0,
        availableAmount: 0,
        usagePercentage: 0,
        benefitReferences: [],
      }
    })
  }, [activeDepartments, overview, selectedPeriod])

  const handlePeriodChange = (newPeriod) => {
    setIsLoading(true)
    setSelectedPeriod(newPeriod)
  }

  const handleOpenGlobalModal = () => {
    setGlobalApiError(null)
    setIsGlobalModalOpen(true)
  }

  const handleCloseGlobalModal = () => {
    if (!isSubmittingGlobal) {
      setIsGlobalModalOpen(false)
      setGlobalApiError(null)
    }
  }

  const handleSaveGlobal = async (totalAmount) => {
    setIsSubmittingGlobal(true)
    setGlobalApiError(null)
    try {
      await saveGlobalBudget(selectedPeriod, totalAmount)
      setSuccessMessage('Presupuesto global actualizado correctamente')
      setIsGlobalModalOpen(false)
      setIsLoading(true)
      setRefreshTrigger((prev) => prev + 1)
    } catch (error) {
      setGlobalApiError(
        error.message || 'Error al guardar el presupuesto global'
      )
    } finally {
      setIsSubmittingGlobal(false)
    }
  }

  const handleOpenDeptModal = (dept) => {
    setSelectedDeptForModal(dept)
    setDeptApiError(null)
    setIsDeptModalOpen(true)
  }

  const handleCloseDeptModal = () => {
    if (!isSubmittingDept) {
      setIsDeptModalOpen(false)
      setSelectedDeptForModal(null)
      setDeptApiError(null)
    }
  }

  const handleSaveDepartment = async ({ allocatedAmount, references }) => {
    if (!selectedDeptForModal) return

    setIsSubmittingDept(true)
    setDeptApiError(null)
    try {
      await saveDepartmentBudget(
        selectedDeptForModal.departmentId,
        selectedPeriod,
        allocatedAmount
      )

      if (Array.isArray(references) && references.length > 0) {
        await saveBenefitReferences(
          selectedDeptForModal.departmentId,
          selectedPeriod,
          references
        )
      }

      setSuccessMessage(
        `Presupuesto de ${selectedDeptForModal.departmentName} actualizado correctamente`
      )
      setIsDeptModalOpen(false)
      setSelectedDeptForModal(null)
      setIsLoading(true)
      setRefreshTrigger((prev) => prev + 1)
    } catch (error) {
      setDeptApiError(
        error.message || 'Error al guardar el presupuesto del departamento'
      )
    } finally {
      setIsSubmittingDept(false)
    }
  }

  const availableCeilingForSelectedDept = useMemo(() => {
    if (!overview || !selectedDeptForModal) return 0
    const currentAllocated = selectedDeptForModal.allocatedAmount || 0
    return Number(overview.unallocatedAmount || 0) + Number(currentAllocated)
  }, [overview, selectedDeptForModal])

  const handleRetry = () => {
    setIsLoading(true)
    setRefreshTrigger((prev) => prev + 1)
  }

  return (
    <AdminLayout>
      <div className="budgetsPageContainer">
        <GlobalBudgetSummary
          overview={overview}
          selectedPeriod={selectedPeriod}
          onPeriodChange={handlePeriodChange}
          onOpenConfigureGlobal={handleOpenGlobalModal}
        />

        {successMessage && (
          <div className="budgetsAlertSuccess" role="status">
            <Icon name="check" size={16} className="budgetsAlertIcon" />
            <span className="budgetsAlertText">{successMessage}</span>
            <button
              type="button"
              className="budgetsAlertDismiss"
              onClick={() => setSuccessMessage(null)}
            >
              <Icon name="close" size={14} />
            </button>
          </div>
        )}

        {errorMessage && (
          <div className="budgetsAlertError" role="alert">
            <Icon name="close" size={16} className="budgetsAlertIcon" />
            <span className="budgetsAlertText">{errorMessage}</span>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRetry}
              className="budgetsRetryButton"
            >
              Reintentar
            </Button>
          </div>
        )}

        {isLoading ? (
          <div className="budgetsTableSkeleton">
            <div className="skeletonTableHeader" />
            {[1, 2, 3].map((item) => (
              <div key={item} className="skeletonTableRow" />
            ))}
          </div>
        ) : (
          <DepartmentBudgetsTable
            departments={mergedDepartments}
            onEditDepartment={handleOpenDeptModal}
          />
        )}

        <GlobalBudgetModal
          isOpen={isGlobalModalOpen}
          period={selectedPeriod}
          currentTotal={overview?.totalAmount || 0}
          allocatedFloor={overview?.allocatedToDepartments || 0}
          onClose={handleCloseGlobalModal}
          onSubmit={handleSaveGlobal}
          isSubmitting={isSubmittingGlobal}
          apiError={globalApiError}
        />

        <DepartmentBudgetModal
          isOpen={isDeptModalOpen}
          department={selectedDeptForModal}
          availableCeiling={availableCeilingForSelectedDept}
          activeBenefits={activeBenefits}
          onClose={handleCloseDeptModal}
          onSubmit={handleSaveDepartment}
          isSubmitting={isSubmittingDept}
          apiError={deptApiError}
        />
      </div>
    </AdminLayout>
  )
}
