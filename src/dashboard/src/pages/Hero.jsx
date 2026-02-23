import { Link } from "react-router-dom";

const STATS = [
  { value: "1,200", label: "Employees" },
  { value: "80", label: "Locations" },
  { value: "18 mo", label: "History" },
  { value: "15", label: "DQ Rules" },
  { value: "177K", label: "Records / Run" },
  { value: "9", label: "BigQuery Tables" },
];

const TECH_STACK = [
  { name: "Python / FastAPI", desc: "Simulated HRIS REST API" },
  { name: "Pandas / Pydantic", desc: "ETL pipeline + validation" },
  { name: "Google BigQuery", desc: "Cloud data warehouse" },
  { name: "Cloud Run", desc: "Containerized API hosting" },
  { name: "Cloud Functions", desc: "Serverless ETL execution" },
  { name: "React / Recharts", desc: "Interactive dashboard" },
];

export default function Hero() {
  return (
    <div className="relative overflow-hidden">
      {/* Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-brand-950 via-brand-900 to-brand-800" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(59,130,246,0.15),transparent_50%)]" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="pt-20 pb-16 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/10 text-brand-200 text-sm font-medium mb-6 backdrop-blur-sm border border-white/10">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            Live Pipeline - Running Daily on GCP
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white tracking-tight leading-tight">
            People Analytics Engineer
            <br />
            <span className="text-brand-300">Workforce Optimization</span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-brand-200 max-w-3xl mx-auto leading-relaxed">
            I built a live data pipeline that turns HRIS and scheduling data into
            actionable staffing intelligence for multi-location healthcare
            operations - the same infrastructure this role requires.
          </p>

          <div className="mt-4 text-brand-300 font-medium text-lg">
            Kriti Srivastava &middot; Senior Analyst Candidate
          </div>

          {/* CTA Buttons */}
          <div className="mt-10 flex flex-wrap justify-center gap-4">
            <Link
              to="/dashboard"
              className="px-6 py-3 bg-white text-brand-900 font-semibold rounded-xl hover:bg-brand-50 transition-all shadow-lg shadow-black/20 text-sm sm:text-base"
            >
              View Staffing Dashboard
            </Link>
            <Link
              to="/architecture"
              className="px-6 py-3 bg-white/10 text-white font-semibold rounded-xl hover:bg-white/20 transition-all backdrop-blur-sm border border-white/20 text-sm sm:text-base"
            >
              View Architecture
            </Link>
            <a
              href="https://github.com/kriti-hub/DataPipeline"
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-3 bg-white/10 text-white font-semibold rounded-xl hover:bg-white/20 transition-all backdrop-blur-sm border border-white/20 text-sm sm:text-base flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
              </svg>
              GitHub
            </a>
          </div>
        </div>

        {/* Stats Bar */}
        <div className="pb-16">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            {STATS.map(({ value, label }) => (
              <div
                key={label}
                className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center border border-white/10"
              >
                <div className="text-2xl sm:text-3xl font-bold text-white">
                  {value}
                </div>
                <div className="text-sm text-brand-300 mt-1">{label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Pipeline Flow */}
        <div className="pb-16">
          <h2 className="text-2xl font-bold text-white text-center mb-8">
            End-to-End Data Pipeline
          </h2>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-2">
            {[
              { label: "HRIS API", sub: "Cloud Run" },
              null,
              { label: "ETL Pipeline", sub: "Cloud Functions" },
              null,
              { label: "BigQuery", sub: "Data Warehouse" },
              null,
              { label: "Dashboard", sub: "React + Vercel" },
            ].map((step, i) =>
              step === null ? (
                <svg key={i} className="w-6 h-6 text-brand-400 hidden sm:block rotate-0 sm:rotate-0" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3" />
                </svg>
              ) : (
                <div key={i} className="bg-white/10 backdrop-blur-sm rounded-xl px-6 py-4 text-center border border-white/10 min-w-[140px]">
                  <div className="text-white font-semibold">{step.label}</div>
                  <div className="text-brand-300 text-xs mt-1">{step.sub}</div>
                </div>
              )
            )}
          </div>
        </div>

        {/* Tech Stack */}
        <div className="pb-20">
          <h2 className="text-2xl font-bold text-white text-center mb-8">
            Technology Stack
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {TECH_STACK.map(({ name, desc }) => (
              <div key={name} className="bg-white/5 backdrop-blur-sm rounded-xl p-5 border border-white/10 hover:bg-white/10 transition-colors">
                <div className="text-white font-semibold">{name}</div>
                <div className="text-brand-300 text-sm mt-1">{desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
