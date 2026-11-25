export function EmployeeCardSkeleton() {
  return (
    <div className="employeesLoadingGrid">
      {[1, 2, 3].map((skeletonId) => (
        <div key={skeletonId} className="employeesCardSkeleton">
          <div className="employeesSkeletonRow" />
        </div>
      ))}
    </div>
  )
}