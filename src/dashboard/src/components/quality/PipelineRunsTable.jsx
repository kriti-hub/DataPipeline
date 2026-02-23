import { STATUS_COLORS } from "../../utils/constants";
import { formatDateTime, formatDuration, formatNumber } from "../../utils/formatters";

export default function PipelineRunsTable({ runs }) {
  if (!runs?.length) {
    return (
      <div className="card p-5">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Pipeline Run History</h3>
        <p className="text-gray-500 text-sm">No pipeline runs recorded yet.</p>
      </div>
    );
  }

  return (
    <div className="card p-5">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Pipeline Run History</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-2 px-3 font-medium text-gray-500">Run ID</th>
              <th className="text-left py-2 px-3 font-medium text-gray-500">Started</th>
              <th className="text-center py-2 px-3 font-medium text-gray-500">Status</th>
              <th className="text-right py-2 px-3 font-medium text-gray-500">Duration</th>
              <th className="text-right py-2 px-3 font-medium text-gray-500">Extracted</th>
              <th className="text-right py-2 px-3 font-medium text-gray-500">Validated</th>
              <th className="text-right py-2 px-3 font-medium text-gray-500">Quarantined</th>
              <th className="text-right py-2 px-3 font-medium text-gray-500">Loaded</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={run.run_id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-2 px-3 font-mono text-xs text-gray-600">
                  {run.run_id.slice(0, 16)}
                </td>
                <td className="py-2 px-3 text-gray-700 text-xs">
                  {formatDateTime(run.started_at)}
                </td>
                <td className="py-2 px-3 text-center">
                  <span
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
                    style={{
                      backgroundColor: `${STATUS_COLORS[run.status]}15`,
                      color: STATUS_COLORS[run.status],
                    }}
                  >
                    <span
                      className="w-1.5 h-1.5 rounded-full"
                      style={{ backgroundColor: STATUS_COLORS[run.status] }}
                    />
                    {run.status}
                  </span>
                </td>
                <td className="py-2 px-3 text-right text-gray-700">
                  {formatDuration(run.run_duration_seconds)}
                </td>
                <td className="py-2 px-3 text-right font-medium text-gray-900">
                  {formatNumber(run.records_extracted)}
                </td>
                <td className="py-2 px-3 text-right text-gray-700">
                  {formatNumber(run.records_validated)}
                </td>
                <td className="py-2 px-3 text-right">
                  <span className={run.records_quarantined > 0 ? "text-amber-600 font-medium" : "text-gray-400"}>
                    {formatNumber(run.records_quarantined)}
                  </span>
                </td>
                <td className="py-2 px-3 text-right font-medium text-gray-900">
                  {formatNumber(run.records_loaded)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {runs.length === 1 && (
        <p className="text-xs text-gray-400 mt-3 text-center">
          Additional runs will appear here as the daily pipeline executes.
        </p>
      )}
    </div>
  );
}
