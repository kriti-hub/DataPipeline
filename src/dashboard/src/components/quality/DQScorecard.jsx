import { SEVERITY_COLORS, DQ_SEVERITY_WEIGHTS } from "../../utils/constants";
import { formatPercent } from "../../utils/formatters";

function getScoreStatus(score) {
  if (score >= 0.95) return { label: "Healthy", color: "text-green-700 bg-green-50 border-green-200" };
  if (score >= 0.85) return { label: "Warning", color: "text-amber-700 bg-amber-50 border-amber-200" };
  return { label: "Alert", color: "text-red-700 bg-red-50 border-red-200" };
}

export default function DQScorecard({ scores }) {
  if (!scores) return null;

  const overall = getScoreStatus(scores.overall_score);

  return (
    <div className="card p-5 h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Data Quality Scorecard</h3>
        <div className={`px-3 py-1 rounded-full text-sm font-bold border ${overall.color}`}>
          {overall.label}
        </div>
      </div>

      {/* Overall Score */}
      <div className="mb-6 text-center">
        <div className="text-4xl font-extrabold text-gray-900">
          {formatPercent(scores.overall_score, 0)}
        </div>
        <p className="text-sm text-gray-500 mt-1">
          Overall DQ Score ({scores.total_checks} checks)
        </p>
        <p className="text-xs text-gray-400 mt-0.5">
          Weighted: Critical 40% + High 30% + Medium 20% + Low 10%
        </p>
      </div>

      {/* Severity Breakdown */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {Object.entries(scores.severity_scores).map(([severity, score]) => {
          const pct = score * 100;
          const barColor = SEVERITY_COLORS[severity];
          return (
            <div key={severity} className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: barColor }} />
                <span className="text-xs font-medium text-gray-600">{severity}</span>
                <span className="text-xs text-gray-400 ml-auto">
                  {(DQ_SEVERITY_WEIGHTS[severity] * 100).toFixed(0)}%
                </span>
              </div>
              <div className="text-xl font-bold text-gray-900">{formatPercent(score, 0)}</div>
              <div className="mt-2 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${pct}%`, backgroundColor: barColor }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
