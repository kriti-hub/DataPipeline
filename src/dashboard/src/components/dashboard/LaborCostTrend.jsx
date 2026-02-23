import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { formatCurrency, formatMonthLabel } from "../../utils/formatters";
import InfoTooltip from "../ui/InfoTooltip";
import KeyTakeaway from "../ui/KeyTakeaway";

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-3 text-sm">
      <p className="font-semibold text-gray-900">{formatMonthLabel(d.month)}</p>
      <p className="mt-1">Cost / Visit: <span className="font-medium text-brand-600">{formatCurrency(d.cost_per_visit)}</span></p>
      <p>Total Labor: <span className="font-medium">{formatCurrency(d.total_labor, 0)}</span></p>
      <p>Total Visits: <span className="font-medium">{d.total_visits.toLocaleString()}</span></p>
    </div>
  );
};

export default function LaborCostTrend({ data }) {
  if (!data?.length) return null;

  const benchmark = 45; // target benchmark
  const chartData = data.map((d) => ({
    ...d,
    monthLabel: formatMonthLabel(d.month),
  }));

  return (
    <div className="card p-5">
      <div className="flex items-center gap-2 mb-1">
        <h3 className="text-lg font-semibold text-gray-900">Labor Cost Per Visit Trend</h3>
        <InfoTooltip text="Tracks the monthly average labor cost divided by patient visits. The red dashed line shows the $45 industry benchmark. Points above the line indicate inefficiency - you're spending more labor per patient than target." />
      </div>
      <p className="text-sm text-gray-500 mb-3">Monthly cost per visit vs. ${benchmark} benchmark target</p>
      <KeyTakeaway
        insight="Labor cost per visit shows seasonal variation, typically rising during holiday months when overtime increases and visit volume dips."
        recommendation="Plan seasonal staffing adjustments 6-8 weeks ahead. Use part-time or PRN staff during low-volume periods to keep cost-per-visit near the $45 target."
      />
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
          <XAxis
            dataKey="monthLabel"
            tick={{ fontSize: 11, fill: "#6b7280" }}
            interval={2}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "#6b7280" }}
            tickFormatter={(v) => `$${v}`}
            domain={["dataMin - 2", "dataMax + 2"]}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine
            y={benchmark}
            stroke="#dc2626"
            strokeDasharray="6 4"
            label={{ value: `Target $${benchmark}`, position: "right", fill: "#dc2626", fontSize: 11 }}
          />
          <Line
            type="monotone"
            dataKey="cost_per_visit"
            stroke="#3b82f6"
            strokeWidth={2.5}
            dot={{ fill: "#3b82f6", r: 3 }}
            activeDot={{ r: 5, stroke: "#fff", strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
