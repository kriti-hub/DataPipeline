import { useMemo } from "react";
import { DOW_LABELS } from "../../utils/constants";
import InfoTooltip from "../ui/InfoTooltip";
import KeyTakeaway from "../ui/KeyTakeaway";

function getHeatColor(frequency) {
  if (frequency >= 0.15) return "bg-red-500 text-white";
  if (frequency >= 0.10) return "bg-red-400 text-white";
  if (frequency >= 0.07) return "bg-orange-400 text-white";
  if (frequency >= 0.05) return "bg-amber-300 text-gray-800";
  if (frequency >= 0.03) return "bg-yellow-200 text-gray-700";
  return "bg-green-100 text-gray-600";
}

export default function GapHeatmap({ data, coverageData }) {
  const locationNames = useMemo(() => {
    if (!coverageData) return {};
    const map = {};
    coverageData.forEach((loc) => { map[loc.location_key] = loc.location_name; });
    return map;
  }, [coverageData]);

  // Get top 20 locations by total gap frequency for a readable heatmap
  const topLocations = useMemo(() => {
    if (!data?.length) return [];
    const locTotals = {};
    data.forEach((d) => {
      locTotals[d.location_key] = (locTotals[d.location_key] || 0) + d.gap_frequency;
    });
    return Object.entries(locTotals)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 20)
      .map(([key]) => Number(key));
  }, [data]);

  const heatmapData = useMemo(() => {
    if (!data?.length) return {};
    const map = {};
    data.forEach((d) => {
      if (!map[d.location_key]) map[d.location_key] = {};
      map[d.location_key][d.dow] = d;
    });
    return map;
  }, [data]);

  if (!data?.length) return null;

  return (
    <div className="card p-5">
      <div className="flex items-center gap-2 mb-1">
        <h3 className="text-lg font-semibold text-gray-900">Understaffing Hot Spots</h3>
        <InfoTooltip text="Heatmap showing the percentage of shifts that were understaffed at each location by day of week. Darker red cells indicate higher gap frequency, meaning more shifts fell below minimum staffing thresholds." />
      </div>
      <p className="text-sm text-gray-500 mb-3">Gap frequency by location and day of week (top 20)</p>
      <KeyTakeaway
        insight="Weekend shifts (Sat/Sun) and Monday mornings consistently show the highest gap rates across top locations."
        recommendation="Adjust scheduling templates to increase weekend staffing. Consider incentive pay for weekend shifts to reduce gap frequency."
      />
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr>
              <th className="text-left py-2 px-2 font-medium text-gray-500 w-48">Location</th>
              {DOW_LABELS.map((d) => (
                <th key={d} className="text-center py-2 px-1 font-medium text-gray-500 w-14">{d}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {topLocations.map((locKey) => (
              <tr key={locKey} className="border-t border-gray-100">
                <td className="py-1.5 px-2 text-gray-700 font-medium truncate max-w-[180px]">
                  {locationNames[locKey] || `Location ${locKey}`}
                </td>
                {DOW_LABELS.map((_, dow) => {
                  const cell = heatmapData[locKey]?.[dow];
                  const freq = cell?.gap_frequency || 0;
                  return (
                    <td key={dow} className="py-1.5 px-1 text-center">
                      <div
                        className={`rounded px-1 py-0.5 ${getHeatColor(freq)}`}
                        title={`${(freq * 100).toFixed(1)}% (${cell?.understaffed || 0} / ${cell?.total_shifts || 0} shifts)`}
                      >
                        {(freq * 100).toFixed(0)}%
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* Legend */}
      <div className="flex flex-wrap gap-2 mt-4 text-xs text-gray-500">
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-green-100" /> &lt;3%</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-yellow-200" /> 3-5%</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-amber-300" /> 5-7%</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-orange-400" /> 7-10%</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-red-400" /> 10-15%</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-red-500" /> &gt;15%</span>
      </div>
    </div>
  );
}
