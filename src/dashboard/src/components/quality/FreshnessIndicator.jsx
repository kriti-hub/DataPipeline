import { formatDateTime, timeAgo } from "../../utils/formatters";

export default function FreshnessIndicator({ pipelineRuns }) {
  const latestRun = pipelineRuns?.length
    ? pipelineRuns.reduce((a, b) =>
        new Date(b.completed_at || 0) > new Date(a.completed_at || 0) ? b : a
      )
    : null;

  if (!latestRun) {
    return (
      <div className="card p-5">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Data Freshness</h3>
        <p className="text-gray-500 text-sm">No pipeline runs found</p>
      </div>
    );
  }

  const completedAt = latestRun.completed_at ? new Date(latestRun.completed_at) : null;
  const hoursAgo = completedAt ? (Date.now() - completedAt.getTime()) / 3600000 : Infinity;

  let statusColor, statusText, ringColor;
  if (hoursAgo <= 24) {
    statusColor = "text-green-700 bg-green-50";
    ringColor = "border-green-400";
    statusText = "Fresh";
  } else if (hoursAgo <= 48) {
    statusColor = "text-amber-700 bg-amber-50";
    ringColor = "border-amber-400";
    statusText = "Stale";
  } else {
    statusColor = "text-red-700 bg-red-50";
    ringColor = "border-red-400";
    statusText = "Critical";
  }

  return (
    <div className="card p-5 h-full">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Freshness</h3>
      <div className="flex flex-col items-center">
        <div className={`w-24 h-24 rounded-full border-4 ${ringColor} flex items-center justify-center`}>
          <div className={`px-3 py-1 rounded-full text-sm font-bold ${statusColor}`}>
            {statusText}
          </div>
        </div>
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-500">Last successful run</p>
          <p className="font-medium text-gray-900">{timeAgo(latestRun.completed_at)}</p>
          <p className="text-xs text-gray-400 mt-1">{formatDateTime(latestRun.completed_at)}</p>
        </div>
        <div className="mt-4 w-full space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">Status</span>
            <span className={`font-medium ${latestRun.status === "Success" ? "text-green-600" : "text-red-600"}`}>
              {latestRun.status}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Duration</span>
            <span className="font-medium text-gray-900">{latestRun.run_duration_seconds}s</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Records</span>
            <span className="font-medium text-gray-900">{latestRun.records_loaded?.toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
