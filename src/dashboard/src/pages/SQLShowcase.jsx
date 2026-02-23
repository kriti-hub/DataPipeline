import { useState } from "react";
import PageContainer from "../components/layout/PageContainer";
import SQLBlock from "../components/showcase/SQLBlock";
import ResultsTable from "../components/showcase/ResultsTable";

const QUERIES = [
  {
    id: 1,
    title: "Location Staffing Efficiency Scorecard",
    question: "Which locations have the best and worst staffing efficiency, and how do they rank within their region?",
    techniques: ["Window Functions", "CASE Classification", "Multi-table JOIN"],
    sql: `WITH location_metrics AS (
  SELECT
    dl.location_key,
    dl.location_name,
    dl.region,
    dl.location_type,
    ROUND(AVG(fs.coverage_score), 3)    AS avg_coverage,
    ROUND(SUM(fs.overtime_hours), 1)    AS total_overtime,
    ROUND(AVG(fs.cost_per_visit), 2)    AS avg_cost_per_visit,
    COUNT(DISTINCT fs.staffing_date)    AS days_measured
  FROM people_analytics.fact_daily_staffing fs
  JOIN people_analytics.dim_location dl
    ON fs.location_key = dl.location_key
  WHERE fs.staffing_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  GROUP BY dl.location_key, dl.location_name, dl.region, dl.location_type
)
SELECT
  location_name,
  region,
  location_type,
  avg_coverage,
  total_overtime,
  avg_cost_per_visit,
  CASE
    WHEN avg_coverage >= 0.95 AND total_overtime < 200 THEN 'Optimal'
    WHEN avg_coverage >= 0.85 THEN 'Adequate'
    ELSE 'Understaffed'
  END AS efficiency_tier,
  DENSE_RANK() OVER (
    PARTITION BY region
    ORDER BY avg_coverage DESC
  ) AS regional_rank
FROM location_metrics
ORDER BY region, regional_rank;`,
    columns: ["location_name", "region", "location_type", "avg_coverage", "total_overtime", "avg_cost_per_visit", "efficiency_tier", "regional_rank"],
    sampleRows: [
      { location_name: "WellNow Rochester 5", region: "Northeast", location_type: "Suburban", avg_coverage: "0.998", total_overtime: "145.2", avg_cost_per_visit: "$41.20", efficiency_tier: "Optimal", regional_rank: "1" },
      { location_name: "WellNow Buffalo 10", region: "Northeast", location_type: "Suburban", avg_coverage: "0.994", total_overtime: "158.7", avg_cost_per_visit: "$42.10", efficiency_tier: "Optimal", regional_rank: "2" },
      { location_name: "WellNow Hartford 31", region: "Northeast", location_type: "Suburban", avg_coverage: "1.406", total_overtime: "89.3", avg_cost_per_visit: "$38.50", efficiency_tier: "Optimal", regional_rank: "3" },
      { location_name: "WellNow Philadelphia 25", region: "Northeast", location_type: "Urban", avg_coverage: "0.857", total_overtime: "1969.0", avg_cost_per_visit: "$52.40", efficiency_tier: "Understaffed", regional_rank: "35" },
    ],
    explanation: "This query joins staffing facts with location dimensions to create a 90-day efficiency scorecard. Each location is classified into tiers (Optimal/Adequate/Understaffed) using CASE logic, then ranked within its region using DENSE_RANK window functions. This reveals both the best-performing locations and regional outliers that need attention.",
  },
  {
    id: 2,
    title: "Shift Gap Analysis with Float Deployment Recommendations",
    question: "Where are the chronic understaffing patterns, and which locations should receive float clinicians first?",
    techniques: ["CTEs", "DENSE_RANK", "Day-of-Week Analysis"],
    sql: `WITH gap_by_location_dow AS (
  SELECT
    dl.location_key,
    dl.location_name,
    dl.region,
    EXTRACT(DAYOFWEEK FROM fg.shift_date) AS dow,
    COUNT(*)                               AS total_shifts,
    SUM(CASE WHEN fg.gap_flag = 1 THEN 1 ELSE 0 END) AS understaffed,
    ROUND(
      SUM(CASE WHEN fg.gap_flag = 1 THEN 1 ELSE 0 END) * 100.0
      / COUNT(*), 1
    ) AS gap_pct
  FROM people_analytics.fact_shift_gap fg
  JOIN people_analytics.dim_location dl
    ON fg.location_key = dl.location_key
  WHERE fg.shift_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  GROUP BY dl.location_key, dl.location_name, dl.region, dow
),
location_priority AS (
  SELECT
    location_key,
    location_name,
    region,
    SUM(understaffed)            AS total_gaps_30d,
    ROUND(AVG(gap_pct), 1)       AS avg_gap_pct,
    DENSE_RANK() OVER (
      ORDER BY SUM(understaffed) DESC
    ) AS deploy_priority
  FROM gap_by_location_dow
  GROUP BY location_key, location_name, region
)
SELECT
  deploy_priority,
  location_name,
  region,
  total_gaps_30d,
  avg_gap_pct,
  CASE
    WHEN total_gaps_30d > 80 THEN 'Deploy float ASAP'
    WHEN total_gaps_30d > 50 THEN 'Schedule peak-day float'
    ELSE 'Monitor / PRN backfill'
  END AS recommendation
FROM location_priority
WHERE deploy_priority <= 15
ORDER BY deploy_priority;`,
    columns: ["deploy_priority", "location_name", "region", "total_gaps_30d", "avg_gap_pct", "recommendation"],
    sampleRows: [
      { deploy_priority: "1", location_name: "WellNow New York City 12", region: "Northeast", total_gaps_30d: "94", avg_gap_pct: "12.3%", recommendation: "Deploy float ASAP" },
      { deploy_priority: "2", location_name: "WellNow Richmond 68", region: "Southeast", total_gaps_30d: "89", avg_gap_pct: "11.8%", recommendation: "Deploy float ASAP" },
      { deploy_priority: "3", location_name: "WellNow Philadelphia 25", region: "Northeast", total_gaps_30d: "86", avg_gap_pct: "11.2%", recommendation: "Deploy float ASAP" },
      { deploy_priority: "4", location_name: "WellNow Orlando 74", region: "Southeast", total_gaps_30d: "82", avg_gap_pct: "10.9%", recommendation: "Deploy float ASAP" },
    ],
    explanation: "This two-CTE query first breaks down shift gaps by location and day-of-week, then aggregates to a location-level priority using DENSE_RANK. The final output produces an actionable deployment list, ranked by total gap count, with specific recommendations based on severity thresholds. Operations managers can use this directly to allocate float clinicians.",
  },
  {
    id: 3,
    title: "Overtime Hotspot Analysis & Labor Cost Impact",
    question: "Which locations are driving the most overtime, and what is the cumulative financial impact?",
    techniques: ["Aggregation", "Running Totals", "Window Functions"],
    sql: `WITH overtime_summary AS (
  SELECT
    dl.location_key,
    dl.location_name,
    dl.region,
    dl.location_type,
    ROUND(SUM(fs.overtime_hours), 1)     AS total_ot_hours,
    ROUND(SUM(fs.overtime_hours * 75), 0) AS est_ot_cost,
    ROUND(AVG(fs.cost_per_visit), 2)     AS avg_cpv,
    COUNT(DISTINCT fs.staffing_date)     AS days_with_data
  FROM people_analytics.fact_daily_staffing fs
  JOIN people_analytics.dim_location dl
    ON fs.location_key = dl.location_key
  WHERE fs.staffing_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  GROUP BY dl.location_key, dl.location_name, dl.region, dl.location_type
  HAVING SUM(fs.overtime_hours) > 0
)
SELECT
  location_name,
  region,
  location_type,
  total_ot_hours,
  est_ot_cost,
  avg_cpv,
  SUM(est_ot_cost) OVER (
    ORDER BY total_ot_hours DESC
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS cumulative_cost,
  ROUND(
    SUM(est_ot_cost) OVER (
      ORDER BY total_ot_hours DESC
      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) * 100.0 / SUM(est_ot_cost) OVER (), 1
  ) AS cumulative_pct
FROM overtime_summary
ORDER BY total_ot_hours DESC
LIMIT 15;`,
    columns: ["location_name", "region", "total_ot_hours", "est_ot_cost", "avg_cpv", "cumulative_cost", "cumulative_pct"],
    sampleRows: [
      { location_name: "WellNow New York City 12", region: "Northeast", total_ot_hours: "2,564.7", est_ot_cost: "$192,353", avg_cpv: "$54.20", cumulative_cost: "$192,353", cumulative_pct: "11.2%" },
      { location_name: "WellNow Richmond 68", region: "Southeast", total_ot_hours: "1,990.2", est_ot_cost: "$149,265", avg_cpv: "$51.80", cumulative_cost: "$341,618", cumulative_pct: "19.8%" },
      { location_name: "WellNow Philadelphia 25", region: "Northeast", total_ot_hours: "1,969.0", est_ot_cost: "$147,675", avg_cpv: "$52.40", cumulative_cost: "$489,293", cumulative_pct: "28.4%" },
      { location_name: "WellNow Boston 34", region: "Northeast", total_ot_hours: "1,819.4", est_ot_cost: "$136,455", avg_cpv: "$50.90", cumulative_cost: "$761,998", cumulative_pct: "44.2%" },
    ],
    explanation: "This query estimates the financial impact of overtime using a $75/hr blended overtime rate, then calculates running totals with window functions to show cumulative cost concentration. The Pareto-style output reveals that the top 4 locations account for ~44% of total overtime costs, highlighting where targeted interventions would have the greatest ROI.",
  },
];

export default function SQLShowcase() {
  const [activeView, setActiveView] = useState({});

  const toggleView = (id) => {
    setActiveView((prev) => ({
      ...prev,
      [id]: prev[id] === "results" ? "query" : "results",
    }));
  };

  return (
    <PageContainer>
      <div className="mb-8">
        <h1 className="section-heading">SQL Showcase</h1>
        <p className="section-subheading">
          Three featured analytical queries demonstrating window functions, CTEs, and business intelligence
        </p>
      </div>

      <div className="space-y-10">
        {QUERIES.map((q) => (
          <div key={q.id} className="card overflow-hidden">
            {/* Header */}
            <div className="p-5 border-b border-gray-200">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="w-8 h-8 bg-brand-600 text-white rounded-lg flex items-center justify-center text-sm font-bold">
                      {q.id}
                    </span>
                    <h2 className="text-lg font-bold text-gray-900">{q.title}</h2>
                  </div>
                  <p className="text-sm text-gray-600 italic">{q.question}</p>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {q.techniques.map((t) => (
                      <span key={t} className="badge-blue">{t}</span>
                    ))}
                  </div>
                </div>
                <button
                  onClick={() => toggleView(q.id)}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors whitespace-nowrap"
                >
                  {activeView[q.id] === "results" ? "Show Query" : "Show Results"}
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-5">
              {activeView[q.id] === "results" ? (
                <ResultsTable columns={q.columns} rows={q.sampleRows} />
              ) : (
                <SQLBlock sql={q.sql} title="BigQuery SQL" />
              )}
            </div>

            {/* Explanation */}
            <div className="px-5 pb-5">
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
                <p className="text-sm text-blue-900 font-medium mb-1">What this reveals:</p>
                <p className="text-sm text-blue-800 leading-relaxed">{q.explanation}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </PageContainer>
  );
}
