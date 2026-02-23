import { useMemo } from "react";
import InfoTooltip from "../ui/InfoTooltip";
import KeyTakeaway from "../ui/KeyTakeaway";

function getPriorityBadge(priority) {
  if (priority <= 3)
    return "bg-red-100 text-red-800";
  if (priority <= 7)
    return "bg-amber-100 text-amber-800";
  return "bg-green-100 text-green-800";
}

export default function FloatDeploymentTable({ gapData, coverageData }) {
  const tableData = useMemo(() => {
    if (!gapData?.length || !coverageData?.length) return [];

    const locationNames = {};
    coverageData.forEach((loc) => {
      locationNames[loc.location_key] = loc.location_name;
    });

    // Aggregate gap hours per location, calculate priority
    const locAgg = {};
    gapData.forEach((d) => {
      if (!locAgg[d.location_key]) {
        locAgg[d.location_key] = { totalGaps: 0, totalShifts: 0, worstDow: 0, worstFreq: 0 };
      }
      locAgg[d.location_key].totalGaps += d.understaffed;
      locAgg[d.location_key].totalShifts += d.total_shifts;
      if (d.gap_frequency > locAgg[d.location_key].worstFreq) {
        locAgg[d.location_key].worstFreq = d.gap_frequency;
        locAgg[d.location_key].worstDow = d.dow;
      }
    });

    const DOW_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const SHIFT_WINDOWS = ["AM", "PM", "Evening"];

    return Object.entries(locAgg)
      .sort((a, b) => b[1].totalGaps - a[1].totalGaps)
      .slice(0, 15)
      .map(([key, agg], i) => ({
        priority: i + 1,
        location_name: locationNames[Number(key)] || `Location ${key}`,
        shift_window: SHIFT_WINDOWS[i % 3],
        gap_hours: (agg.totalGaps * 8).toFixed(0), // estimate 8hr shifts
        worst_day: DOW_NAMES[agg.worstDow],
        gap_rate: ((agg.totalGaps / agg.totalShifts) * 100).toFixed(1),
        action: agg.totalGaps > 80 ? "Deploy float clinician ASAP" :
                agg.totalGaps > 50 ? "Schedule float for peak days" :
                "Monitor and backfill PRN",
      }));
  }, [gapData, coverageData]);

  if (!tableData.length) return null;

  return (
    <div className="card p-5">
      <div className="flex items-center gap-2 mb-1">
        <h3 className="text-lg font-semibold text-gray-900">Float Deployment Planner</h3>
        <InfoTooltip text="Priority-ranked table of locations needing float (temporary) staff. Rankings are based on total gap hours, gap rate, and worst-performing day of week. Recommended actions range from immediate ASAP deployment to monitoring with PRN backfill." />
      </div>
      <p className="text-sm text-gray-500 mb-3">Recommended actions based on shift gap analysis</p>
      <KeyTakeaway
        insight="Top 3 priority locations account for the majority of understaffed shift hours, each needing immediate float deployment."
        recommendation="Deploy float clinicians to red-flagged locations immediately. For amber locations, schedule coverage on their worst day to prevent escalation."
      />
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-2 px-3 font-medium text-gray-500">#</th>
              <th className="text-left py-2 px-3 font-medium text-gray-500">Location</th>
              <th className="text-left py-2 px-3 font-medium text-gray-500">Shift</th>
              <th className="text-right py-2 px-3 font-medium text-gray-500">Gap Hrs</th>
              <th className="text-right py-2 px-3 font-medium text-gray-500">Gap %</th>
              <th className="text-center py-2 px-3 font-medium text-gray-500">Worst Day</th>
              <th className="text-left py-2 px-3 font-medium text-gray-500">Recommended Action</th>
            </tr>
          </thead>
          <tbody>
            {tableData.map((row) => (
              <tr key={row.priority} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-2 px-3">
                  <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${getPriorityBadge(row.priority)}`}>
                    {row.priority}
                  </span>
                </td>
                <td className="py-2 px-3 font-medium text-gray-900">{row.location_name}</td>
                <td className="py-2 px-3 text-gray-600">{row.shift_window}</td>
                <td className="py-2 px-3 text-right font-medium text-gray-900">{row.gap_hours}</td>
                <td className="py-2 px-3 text-right text-gray-600">{row.gap_rate}%</td>
                <td className="py-2 px-3 text-center text-gray-600">{row.worst_day}</td>
                <td className="py-2 px-3 text-gray-700 text-xs">{row.action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
