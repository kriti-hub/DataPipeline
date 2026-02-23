const STEPS = [
  { label: "Cloud Scheduler", sub: "Daily 6 AM UTC", color: "bg-amber-100 text-amber-700 border-amber-300" },
  { label: "HRIS API", sub: "Cloud Run", color: "bg-blue-100 text-blue-700 border-blue-300" },
  { label: "ETL Pipeline", sub: "Cloud Functions", color: "bg-purple-100 text-purple-700 border-purple-300" },
  { label: "BigQuery", sub: "Data Warehouse", color: "bg-green-100 text-green-700 border-green-300" },
  { label: "Dashboard", sub: "React + Vercel", color: "bg-pink-100 text-pink-700 border-pink-300" },
];

export default function PipelineDiagram() {
  return (
    <div className="card p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Data Flow</h2>
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        {STEPS.map((step, i) => (
          <div key={step.label} className="flex items-center gap-3">
            <div className={`flex flex-col items-center p-4 rounded-xl border-2 min-w-[130px] ${step.color}`}>
              <span className="font-semibold text-sm">{step.label}</span>
              <span className="text-xs opacity-70 mt-0.5">{step.sub}</span>
            </div>
            {i < STEPS.length - 1 && (
              <svg className="w-6 h-6 text-gray-400 hidden md:block flex-shrink-0" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
              </svg>
            )}
          </div>
        ))}
      </div>

      {/* Pipeline Stats */}
      <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: "Records / Run", value: "177,182" },
          { label: "Pipeline Duration", value: "~95 sec" },
          { label: "DQ Rules", value: "15" },
          { label: "BigQuery Tables", value: "9" },
        ].map(({ label, value }) => (
          <div key={label} className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-lg font-bold text-gray-900">{value}</div>
            <div className="text-xs text-gray-500">{label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
