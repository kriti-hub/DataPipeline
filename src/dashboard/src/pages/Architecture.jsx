import PageContainer from "../components/layout/PageContainer";
import PipelineDiagram from "../components/architecture/PipelineDiagram";

const COMPONENTS = [
  {
    name: "Simulated HRIS API",
    tech: "Python, FastAPI, Faker",
    infra: "Cloud Run (GCP)",
    desc: "REST API generating realistic healthcare workforce data. 7 endpoints with API key auth, Pydantic validation, and deterministic seed-based generation. Simulates what Workday or ADP would provide in production.",
    color: "border-blue-400 bg-blue-50",
  },
  {
    name: "ETL Pipeline",
    tech: "Python, Pandas, Pydantic",
    infra: "Cloud Functions 2nd Gen",
    desc: "Four-stage orchestrated pipeline: Extract (paginated API calls with retry), Validate (15 DQ rules from YAML), Transform (SCD Type 2 dims + facts), Load (BigQuery with TRUNCATE/APPEND strategy).",
    color: "border-purple-400 bg-purple-50",
  },
  {
    name: "Data Warehouse",
    tech: "Google BigQuery",
    infra: "GCP (US multi-region)",
    desc: "9 tables across 3 layers: 4 dimension tables (employee, location, job, date), 2 fact tables (daily_staffing, shift_gap), 3 utility tables (pipeline_runs, data_quality_log, quarantine).",
    color: "border-green-400 bg-green-50",
  },
  {
    name: "Cloud Scheduler",
    tech: "GCP Cloud Scheduler",
    infra: "Cron: daily 6 AM UTC",
    desc: "Automated daily trigger for the ETL pipeline. Sends HTTP POST to Cloud Function endpoint, enabling fully hands-off pipeline execution.",
    color: "border-amber-400 bg-amber-50",
  },
  {
    name: "Dashboard Data Export",
    tech: "Python, Cloud Storage",
    infra: "GCS Buckets",
    desc: "Pipeline Stage 5 exports 7 pre-computed JSON files to Cloud Storage: KPIs, coverage, gaps, overtime, cost trends, DQ scores, and pipeline runs.",
    color: "border-teal-400 bg-teal-50",
  },
  {
    name: "React Dashboard",
    tech: "React 18, Recharts, Tailwind",
    infra: "Vercel (Edge CDN)",
    desc: "6-page interactive analytics dashboard consuming pre-computed JSON. Features KPI cards, geographic scatter plots, heatmaps, trend lines, and deployment planning tables.",
    color: "border-pink-400 bg-pink-50",
  },
];

export default function Architecture() {
  return (
    <PageContainer>
      <div className="mb-8">
        <h1 className="section-heading">Architecture Deep Dive</h1>
        <p className="section-subheading">
          End-to-end cloud-native data pipeline running on Google Cloud Platform
        </p>
      </div>

      {/* Pipeline Diagram */}
      <PipelineDiagram />

      {/* Component Cards */}
      <div className="mt-10">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Component Details</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {COMPONENTS.map((c) => (
            <div key={c.name} className={`rounded-xl border-l-4 p-5 bg-white shadow-sm ${c.color.split(" ")[0]}`}>
              <h3 className="font-bold text-gray-900">{c.name}</h3>
              <div className="flex flex-wrap gap-2 mt-2">
                <span className="badge-blue">{c.tech}</span>
                <span className="badge bg-gray-100 text-gray-600">{c.infra}</span>
              </div>
              <p className="text-sm text-gray-600 mt-3 leading-relaxed">{c.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Cost Breakdown */}
      <div className="mt-10 card p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Cost Breakdown</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { service: "Cloud Run", cost: "$0", note: "Free tier: 2M requests/mo" },
            { service: "Cloud Functions", cost: "$0", note: "Free tier: 2M invocations/mo" },
            { service: "BigQuery", cost: "$0", note: "Free tier: 1TB queries, 10GB storage" },
            { service: "Cloud Storage", cost: "$0", note: "Free tier: 5GB, minimal JSON files" },
          ].map(({ service, cost, note }) => (
            <div key={service} className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-900">{service}</span>
                <span className="text-green-600 font-bold">{cost}</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">{note}</p>
            </div>
          ))}
        </div>
        <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
          <p className="text-sm text-green-800 font-medium">
            Total Monthly Cost: $0 - fully within GCP Free Tier
          </p>
        </div>
      </div>
    </PageContainer>
  );
}
