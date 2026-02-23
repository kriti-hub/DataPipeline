import PageContainer from "../components/layout/PageContainer";
import { KPI_CONFIG } from "../utils/constants";

const ICON_MAP = {
  shield: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z" />
    </svg>
  ),
  clock: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
    </svg>
  ),
  dollar: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
    </svg>
  ),
  alert: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
    </svg>
  ),
  timer: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
    </svg>
  ),
  users: (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" />
    </svg>
  ),
};

const CHART_GUIDES = [
  {
    title: "KPI Scorecards",
    description:
      "Six key performance indicators displayed as color-coded cards at the top of the dashboard. Each card shows the current metric value with a status icon.",
    howToRead: [
      "Green background = metric is within the healthy range (meeting target)",
      "Amber background = metric is in warning zone (approaching threshold)",
      "Red background = metric is in critical range (needs immediate attention)",
      "Hover over the (i) icon on each card to see the full metric definition",
    ],
  },
  {
    title: "Staffing Coverage Map",
    description:
      "A scatter/bubble chart showing all locations grouped by region. Each bubble represents a single location, where the bubble size corresponds to patient volume and the color indicates coverage score.",
    howToRead: [
      "Large red bubbles = high-volume locations that are critically understaffed (top priority)",
      "Green bubbles = well-staffed locations with coverage between 95-105%",
      "Blue bubbles = overstaffed locations (coverage > 105%) - consider redeploying staff",
      "Use region filters to focus on specific geographic areas",
    ],
  },
  {
    title: "Understaffing Hot Spots (Heatmap)",
    description:
      "A heatmap table showing the top 20 locations with the highest gap frequency, broken down by day of week. Each cell shows what percentage of shifts were understaffed on that day.",
    howToRead: [
      "Dark red cells (>15%) indicate severe, persistent understaffing on that day",
      "Look for patterns across rows (specific location always understaffed) vs columns (specific day is problematic everywhere)",
      "Hover over any cell to see the exact shift count (e.g., 12 of 80 shifts understaffed)",
      "Column patterns suggest systemic scheduling issues; row patterns suggest location-specific problems",
    ],
  },
  {
    title: "Labor Cost Per Visit Trend",
    description:
      "A line chart tracking the monthly average labor cost per patient visit over 18 months. A red dashed reference line shows the $45 industry benchmark target.",
    howToRead: [
      "Points above the red line = spending more per visit than target (inefficient)",
      "Points below the red line = labor efficiency is better than benchmark",
      "Upward trends suggest rising costs or declining visit volume",
      "Seasonal spikes (holidays, summer) are normal - persistent elevation is a concern",
    ],
  },
  {
    title: "Overtime Hotspots",
    description:
      "A horizontal bar chart ranking the top 15 locations by total overtime hours. Color coding indicates severity: red for 2,000+ hours, orange for 1,500-2,000, and yellow for under 1,500.",
    howToRead: [
      "Red bars indicate locations where overtime is a chronic, structural problem requiring headcount additions",
      "The top 3-5 locations typically account for 50-60% of all overtime costs (Pareto principle)",
      "Compare this chart with the Coverage Map - high overtime + low coverage = urgent hiring need",
      "Hover over bars to see exact overtime hours and location details",
    ],
  },
  {
    title: "Float Deployment Planner",
    description:
      "A priority-ranked action table recommending where to deploy float (temporary/traveling) staff based on gap analysis. Rankings consider total gap hours, gap rate, and worst-performing days.",
    howToRead: [
      "Red priority badges (#1-3) = deploy float staff immediately (ASAP)",
      "Amber badges (#4-7) = schedule float coverage for peak days",
      "Green badges (#8+) = monitor and backfill with PRN staff as needed",
      "The 'Worst Day' column tells you which day of the week to prioritize for each location",
    ],
  },
];

export default function AboutDashboard() {
  return (
    <PageContainer>
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="section-heading">About the Staffing Optimization Dashboard</h1>
        <p className="section-subheading">
          Understanding the metrics, charts, and insights that drive workforce decisions
        </p>
      </div>

      {/* Dashboard Overview */}
      <div className="card p-6 mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-3">What is This Dashboard?</h2>
        <p className="text-gray-700 leading-relaxed mb-4">
          The Staffing Optimization Dashboard is a real-time analytics tool designed for healthcare operations leaders
          who manage multi-location urgent care networks. It transforms raw HRIS, scheduling, and patient volume data
          into actionable intelligence that helps answer three critical questions:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          {[
            {
              q: "Where are we understaffed?",
              a: "Coverage Map and Heatmap reveal which locations and days of week have the highest gap rates.",
              icon: "M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z",
            },
            {
              q: "How much is it costing us?",
              a: "Labor Cost Trend and Overtime Hotspots quantify the financial impact of staffing imbalances.",
              icon: "M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z",
            },
            {
              q: "What should we do about it?",
              a: "Float Deployment Planner provides priority-ranked, actionable recommendations for each location.",
              icon: "M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z",
            },
          ].map(({ q, a, icon }) => (
            <div key={q} className="bg-gray-50 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <div className="p-1.5 bg-brand-100 rounded-lg text-brand-600">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
                  </svg>
                </div>
                <h3 className="font-semibold text-gray-900 text-sm">{q}</h3>
              </div>
              <p className="text-sm text-gray-600">{a}</p>
            </div>
          ))}
        </div>
        <div className="p-3 bg-brand-50 rounded-lg border border-brand-200">
          <p className="text-sm text-brand-800">
            <span className="font-semibold">Why it matters:</span> Healthcare staffing imbalances directly impact patient
            wait times, employee burnout, overtime costs, and quality of care. This dashboard provides the data foundation
            for evidence-based staffing decisions rather than relying on intuition or historical patterns alone.
          </p>
        </div>
      </div>

      {/* KPI Definitions */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-6">KPI Definitions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(KPI_CONFIG).map(([key, config]) => (
            <div key={key} className="card p-5">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-brand-50 rounded-lg text-brand-600 flex-shrink-0">
                  {ICON_MAP[config.icon]}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{config.label}</h3>
                  <p className="text-sm text-gray-600 mt-1 leading-relaxed">{config.description}</p>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {config.good != null && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-100 text-green-800 text-xs font-medium">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                        Good: {config.invertThreshold ? "<=" : ">="} {config.format === "percent" ? `${(config.good * 100).toFixed(0)}%` : config.format === "currency" ? `$${config.good}` : config.format === "minutes" ? `${config.good} min` : config.good.toLocaleString()}
                      </span>
                    )}
                    {config.warn != null && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 text-xs font-medium">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                        Warning: {config.invertThreshold ? "<=" : ">="} {config.format === "percent" ? `${(config.warn * 100).toFixed(0)}%` : config.format === "currency" ? `$${config.warn}` : config.format === "minutes" ? `${config.warn} min` : config.warn.toLocaleString()}
                      </span>
                    )}
                    {config.invertThreshold && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-gray-100 text-gray-600 text-xs">
                        Lower is better
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Chart Interpretation Guide */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-6">How to Interpret Each Chart</h2>
        <div className="space-y-4">
          {CHART_GUIDES.map((guide, i) => (
            <div key={i} className="card p-5">
              <div className="flex items-start gap-3">
                <span className="w-7 h-7 bg-brand-600 text-white rounded-lg flex items-center justify-center text-sm font-bold flex-shrink-0">
                  {i + 1}
                </span>
                <div>
                  <h3 className="font-bold text-gray-900">{guide.title}</h3>
                  <p className="text-sm text-gray-600 mt-1 leading-relaxed">{guide.description}</p>
                  <div className="mt-3">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">How to Read</p>
                    <ul className="space-y-1.5">
                      {guide.howToRead.map((item, j) => (
                        <li key={j} className="flex items-start gap-2 text-sm text-gray-600">
                          <span className="w-1.5 h-1.5 rounded-full bg-brand-400 mt-1.5 flex-shrink-0" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Data Freshness Note */}
      <div className="card p-6 bg-gradient-to-r from-gray-50 to-brand-50 border-brand-200">
        <h2 className="text-lg font-bold text-gray-900 mb-2">Data Freshness & Pipeline</h2>
        <p className="text-sm text-gray-600 leading-relaxed">
          Dashboard data is refreshed daily via an automated ETL pipeline running on Google Cloud.
          The pipeline extracts data from the HRIS API, validates it against 15 data quality rules,
          transforms it into dimensional models, and loads it into BigQuery. Pre-computed JSON summaries
          are then exported for the dashboard. Visit the{" "}
          <a href="/data-quality" className="text-brand-600 font-medium hover:underline">Data Quality</a>{" "}
          page to monitor pipeline health and data freshness.
        </p>
      </div>
    </PageContainer>
  );
}
