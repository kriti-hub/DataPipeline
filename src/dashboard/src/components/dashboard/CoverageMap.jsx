import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { COVERAGE_COLORS, REGION_COLORS } from "../../utils/constants";
import { formatPercent, formatNumber } from "../../utils/formatters";
import InfoTooltip from "../ui/InfoTooltip";
import KeyTakeaway from "../ui/KeyTakeaway";

function getCoverageColor(coverage) {
  if (coverage < 0.85) return COVERAGE_COLORS.critical;
  if (coverage < 0.95) return COVERAGE_COLORS.warning;
  if (coverage <= 1.05) return COVERAGE_COLORS.good;
  return COVERAGE_COLORS.over;
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-3 text-sm">
      <p className="font-semibold text-gray-900">{d.location_name}</p>
      <p className="text-gray-500">{d.region} &middot; {d.location_type} &middot; {d.state}</p>
      <div className="mt-2 space-y-1">
        <p>Coverage: <span className="font-medium">{formatPercent(d.avg_coverage)}</span></p>
        <p>Visits: <span className="font-medium">{formatNumber(d.total_visits)}</span></p>
        <p>Avg Wait: <span className="font-medium">{d.avg_wait} min</span></p>
      </div>
    </div>
  );
};

export default function CoverageMap({ data }) {
  if (!data?.length) return null;

  // Create a scatter layout: use location_key for x spread, region grouping for y
  const regionOrder = { Northeast: 4, Midwest: 3, Southeast: 2, Southwest: 1 };
  const plotData = data.map((d) => ({
    ...d,
    x: d.location_key,
    y: regionOrder[d.region] || 0,
    z: d.total_visits,
  }));

  return (
    <div className="card p-5">
      <div className="flex items-center gap-2 mb-1">
        <h3 className="text-lg font-semibold text-gray-900">Staffing Coverage Map</h3>
        <InfoTooltip text="Each bubble represents a location. Size indicates patient volume and color shows coverage score. Red means critically understaffed (<85%), amber is warning (85-94%), green is good (95-105%), and blue is overstaffed (>105%)." />
      </div>
      <p className="text-sm text-gray-500 mb-3">Bubble size = patient volume, color = coverage score</p>
      <KeyTakeaway
        insight="Identify locations with red or amber bubbles that have high patient volume - these need immediate staffing attention."
        recommendation="Prioritize float staff deployment to large, critically understaffed locations to reduce patient wait times and gap rates."
      />
      <div className="flex flex-wrap gap-3 mb-4">
        {Object.entries(COVERAGE_COLORS).map(([key, color]) => (
          <div key={key} className="flex items-center gap-1.5 text-xs text-gray-600">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
            {key === "critical" ? "< 85%" : key === "warning" ? "85-94%" : key === "good" ? "95-105%" : "> 105%"}
          </div>
        ))}
      </div>
      <ResponsiveContainer width="100%" height={360}>
        <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 20 }}>
          <XAxis
            type="number"
            dataKey="x"
            name="Location"
            tick={false}
            axisLine={false}
            label={{ value: "Locations", position: "insideBottom", offset: -5, className: "text-xs fill-gray-400" }}
          />
          <YAxis
            type="number"
            dataKey="y"
            domain={[0, 5]}
            ticks={[1, 2, 3, 4]}
            tickFormatter={(v) => ["", "Southwest", "Southeast", "Midwest", "Northeast"][v] || ""}
            tick={{ fontSize: 11, fill: "#6b7280" }}
            axisLine={false}
            width={80}
          />
          <ZAxis type="number" dataKey="z" range={[40, 250]} />
          <Tooltip content={<CustomTooltip />} />
          <Scatter data={plotData}>
            {plotData.map((entry, i) => (
              <Cell key={i} fill={getCoverageColor(entry.avg_coverage)} fillOpacity={0.7} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
