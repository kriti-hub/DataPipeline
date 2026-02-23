import { useState, useMemo } from "react";
import PageContainer from "../components/layout/PageContainer";
import KPICard from "../components/dashboard/KPICard";
import CoverageMap from "../components/dashboard/CoverageMap";
import GapHeatmap from "../components/dashboard/GapHeatmap";
import LaborCostTrend from "../components/dashboard/LaborCostTrend";
import OvertimeWaterfall from "../components/dashboard/OvertimeWaterfall";
import FloatDeploymentTable from "../components/dashboard/FloatDeploymentTable";
import DateRangeFilter from "../components/dashboard/DateRangeFilter";
import { useMultiDataLoader } from "../hooks/useDataLoader";
import { KPI_CONFIG } from "../utils/constants";

const DATA_FILES = [
  "kpis.json",
  "staffing_coverage.json",
  "shift_gaps.json",
  "labor_cost_trends.json",
  "overtime_hotspots.json",
];

export default function StaffingDashboard() {
  const { data, loading, error } = useMultiDataLoader(DATA_FILES);
  const [filters, setFilters] = useState({ regions: [], locationTypes: [] });

  const kpis = data["kpis.json"];
  const coverage = data["staffing_coverage.json"];
  const gaps = data["shift_gaps.json"];
  const costTrends = data["labor_cost_trends.json"];
  const overtime = data["overtime_hotspots.json"];

  const filteredCoverage = useMemo(() => {
    if (!coverage) return [];
    return coverage.filter((loc) => {
      if (filters.regions?.length && !filters.regions.includes(loc.region)) return false;
      if (filters.locationTypes?.length && !filters.locationTypes.includes(loc.location_type)) return false;
      return true;
    });
  }, [coverage, filters]);

  const filteredGaps = useMemo(() => {
    if (!gaps) return [];
    const locKeys = new Set(filteredCoverage.map((l) => l.location_key));
    if (locKeys.size === 0) return gaps;
    return gaps.filter((g) => locKeys.has(g.location_key));
  }, [gaps, filteredCoverage]);

  if (loading) {
    return (
      <PageContainer>
        <div className="flex items-center justify-center py-32">
          <div className="text-center">
            <div className="w-8 h-8 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin mx-auto" />
            <p className="mt-4 text-gray-500">Loading dashboard data...</p>
          </div>
        </div>
      </PageContainer>
    );
  }

  if (error) {
    return (
      <PageContainer>
        <div className="text-center py-32">
          <p className="text-red-600 font-medium">Failed to load data</p>
          <p className="text-gray-500 text-sm mt-1">{error}</p>
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <div className="mb-6">
        <h1 className="section-heading">Staffing Optimization Dashboard</h1>
        <p className="section-subheading">
          Real-time workforce intelligence across 80 locations &middot; 1,200 employees &middot; 18 months of data
        </p>
      </div>

      <div className="mb-6">
        <DateRangeFilter filters={filters} onChange={setFilters} />
      </div>

      {kpis && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          {Object.keys(KPI_CONFIG).map((key) => (
            <KPICard key={key} metricKey={key} value={kpis[key]} />
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <CoverageMap data={filteredCoverage.length ? filteredCoverage : coverage} />
        <GapHeatmap data={filteredGaps.length ? filteredGaps : gaps} coverageData={coverage} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <LaborCostTrend data={costTrends} />
        <OvertimeWaterfall data={overtime} />
      </div>

      <div className="mb-6">
        <FloatDeploymentTable gapData={gaps} coverageData={coverage} />
      </div>
    </PageContainer>
  );
}
