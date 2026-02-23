import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { REGION_COLORS } from "../../utils/constants";
import { formatNumber } from "../../utils/formatters";

function getBarColor(hours) {
  if (hours >= 2000) return "#dc2626";
  if (hours >= 1500) return "#f97316";
  return "#eab308";
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-3 text-sm">
      <p className="font-semibold text-gray-900">{d.location_name}</p>
      <p className="text-gray-500">{d.region}</p>
      <p className="mt-1">Overtime: <span className="font-bold">{formatNumber(d.total_overtime, 1)} hrs</span></p>
    </div>
  );
};

export default function OvertimeWaterfall({ data }) {
  if (!data?.length) return null;

  const chartData = data.map((d) => ({
    ...d,
    shortName: d.location_name.replace("WellNow ", ""),
  }));

  return (
    <div className="card p-5">
      <h3 className="text-lg font-semibold text-gray-900 mb-1">Overtime Hotspots</h3>
      <p className="text-sm text-gray-500 mb-4">Top 15 locations by total overtime hours</p>
      <div className="flex flex-wrap gap-3 mb-4 text-xs text-gray-600">
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded" style={{ backgroundColor: "#dc2626" }} /> &ge; 2,000 hrs</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded" style={{ backgroundColor: "#f97316" }} /> 1,500 - 2,000</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded" style={{ backgroundColor: "#eab308" }} /> &lt; 1,500</span>
      </div>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, bottom: 5, left: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" horizontal={false} />
          <XAxis type="number" tick={{ fontSize: 11, fill: "#6b7280" }} tickFormatter={(v) => `${(v / 1000).toFixed(1)}k`} />
          <YAxis type="category" dataKey="shortName" tick={{ fontSize: 10, fill: "#6b7280" }} width={130} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="total_overtime" radius={[0, 4, 4, 0]} barSize={18}>
            {chartData.map((entry, i) => (
              <Cell key={i} fill={getBarColor(entry.total_overtime)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
