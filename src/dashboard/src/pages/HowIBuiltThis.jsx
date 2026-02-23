import PageContainer from "../components/layout/PageContainer";

const PHASES = [
  {
    phase: "Step 0",
    title: "Architecture & Documentation",
    duration: "Day 1",
    items: [
      "Designed BigQuery schema: 4 dimensions, 2 facts, 3 utility tables",
      "Created data dictionary, lineage docs, and Mermaid architecture diagrams",
      "Defined 15 data quality rules in externalized YAML",
      "Set up repo structure following enterprise conventions",
    ],
    color: "border-gray-400",
  },
  {
    phase: "Phase 1",
    title: "Simulated HRIS API",
    duration: "Day 1-2",
    items: [
      "Built FastAPI application with 7 REST endpoints",
      "Faker-based deterministic data generation (MASTER_SEED=42)",
      "1,200 employees, 80 locations, 18 months of history",
      "API key auth, Pydantic v2 strict mode, multi-stage Docker",
      "52 tests passing (generators, auth, endpoints)",
    ],
    color: "border-blue-400",
  },
  {
    phase: "Phase 2",
    title: "ETL Pipeline",
    duration: "Day 2-3",
    items: [
      "Four-stage orchestrator with run_id tracking",
      "Paginated extraction with exponential backoff retry",
      "15 DQ rules with quarantine and severity scoring",
      "SCD Type 2 dimensions + TRUNCATE/APPEND load strategy",
      "Dashboard data export: 7 pre-computed JSON files",
      "38 unit tests + integration test (177K records in 10s)",
    ],
    color: "border-purple-400",
  },
  {
    phase: "Phase 2.5",
    title: "GCP Deployment",
    duration: "Day 3",
    items: [
      "API deployed to Cloud Run (containerized, auto-scaling)",
      "ETL pipeline on Cloud Functions 2nd Gen (1024MB, 540s timeout)",
      "Cloud Scheduler for daily 6 AM UTC automated runs",
      "BigQuery dataset live with 9 tables + initial data load",
      "Secret Manager for API key, Cloud Storage for staging",
      "First successful E2E run: 177K records, 95s",
    ],
    color: "border-green-400",
  },
  {
    phase: "Phase 3",
    title: "React Dashboard",
    duration: "Day 3-4",
    items: [
      "Vite + React 18 + Tailwind CSS + Recharts",
      "6 pages: Hero, Architecture, Staffing Dashboard, DQ Monitor, SQL Showcase, Process",
      "5 interactive visualizations with real pipeline data",
      "Region and location type filters with real-time updates",
      "Vercel deployment for global edge delivery",
    ],
    color: "border-pink-400",
  },
];

const CHALLENGES = [
  {
    problem: "Cloud Run PORT mismatch",
    solution: "Cloud Run injects PORT=8080 but Dockerfile hardcoded 8000. Switched to shell-form CMD with $PORT variable expansion.",
  },
  {
    problem: "Cloud Function import paths",
    solution: "ETL uses absolute imports (from src.etl.*) but Cloud Functions deploys from a subdirectory. Created staging directory deploy pattern that preserves the src/ package structure.",
  },
  {
    problem: "BigQuery type strictness",
    solution: "pyarrow rejects Python strings for DATE/TIMESTAMP columns. Added explicit pd.to_datetime() casts before load_table_from_dataframe.",
  },
  {
    problem: "Cloud Function memory OOM",
    solution: "512MB wasn't enough for 177K-record DataFrames during transform. Bumped to 1024MB based on Cloud Logging memory traces.",
  },
  {
    problem: ".env parsing on bash",
    solution: "export $(grep | xargs) pattern broke on blank lines and quoted values. Switched all 7 deploy scripts to set -a; source .env; set +a.",
  },
];

export default function HowIBuiltThis() {
  return (
    <PageContainer>
      <div className="mb-8">
        <h1 className="section-heading">How I Built This</h1>
        <p className="section-subheading">
          AI-assisted development process, timeline, and lessons learned
        </p>
      </div>

      {/* AI Narrative */}
      <div className="card p-6 mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-3">AI-Assisted Development</h2>
        <p className="text-gray-700 leading-relaxed">
          This entire project was built using Claude Code (Anthropic's AI coding assistant) as a pair programming partner.
          I provided the product requirements, architectural decisions, and domain context. Claude helped with
          code generation, debugging, and deployment automation. The result demonstrates how modern AI tools
          can dramatically accelerate data engineering work while maintaining enterprise-quality standards.
        </p>
        <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: "Total Dev Time", value: "~4 days" },
            { label: "Lines of Code", value: "~5,000+" },
            { label: "Test Coverage", value: "90 tests" },
            { label: "GCP Services", value: "7 services" },
          ].map(({ label, value }) => (
            <div key={label} className="bg-gray-50 rounded-lg p-3 text-center">
              <div className="text-lg font-bold text-gray-900">{value}</div>
              <div className="text-xs text-gray-500">{label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Timeline */}
      <div className="mb-10">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Development Timeline</h2>
        <div className="space-y-4">
          {PHASES.map((p) => (
            <div key={p.phase} className={`card p-5 border-l-4 ${p.color}`}>
              <div className="flex items-center gap-3 mb-3">
                <span className="px-2.5 py-0.5 bg-gray-100 rounded-full text-xs font-bold text-gray-700">
                  {p.phase}
                </span>
                <h3 className="font-bold text-gray-900">{p.title}</h3>
                <span className="text-xs text-gray-400 ml-auto">{p.duration}</span>
              </div>
              <ul className="space-y-1.5">
                {p.items.map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                    <span className="w-1.5 h-1.5 rounded-full bg-gray-400 mt-1.5 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Challenges */}
      <div className="mb-10">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Challenges & Solutions</h2>
        <div className="space-y-3">
          {CHALLENGES.map((c, i) => (
            <div key={i} className="card p-4">
              <div className="flex items-start gap-3">
                <span className="w-6 h-6 bg-red-100 text-red-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126Z" />
                  </svg>
                </span>
                <div>
                  <p className="font-medium text-gray-900 text-sm">{c.problem}</p>
                  <p className="text-sm text-gray-600 mt-1">{c.solution}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* GitHub CTA */}
      <div className="card p-6 text-center bg-gradient-to-r from-brand-50 to-purple-50 border-brand-200">
        <h2 className="text-xl font-bold text-gray-900 mb-2">View the Source Code</h2>
        <p className="text-gray-600 mb-4">
          Full codebase, documentation, and infrastructure scripts on GitHub
        </p>
        <a
          href="https://github.com/kriti-hub/DataPipeline"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-xl font-semibold hover:bg-gray-800 transition-colors"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
          </svg>
          View on GitHub
        </a>
      </div>
    </PageContainer>
  );
}
