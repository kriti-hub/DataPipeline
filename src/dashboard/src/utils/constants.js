// ── Color Palettes ───────────────────────────────────────────────────
export const COVERAGE_COLORS = {
  critical: "#dc2626", // < 0.85
  warning: "#d97706", // 0.85 – 0.94
  good: "#16a34a", // 0.95 – 1.05
  over: "#2563eb", // > 1.05 (overstaffed)
};

export const REGION_COLORS = {
  Northeast: "#3b82f6",
  Midwest: "#8b5cf6",
  Southeast: "#f59e0b",
  Southwest: "#ef4444",
};

export const SEVERITY_COLORS = {
  Critical: "#dc2626",
  High: "#f97316",
  Medium: "#eab308",
  Low: "#22c55e",
};

export const STATUS_COLORS = {
  Success: "#16a34a",
  Failed: "#dc2626",
  Partial: "#d97706",
  Running: "#3b82f6",
};

// ── Chart Colors ─────────────────────────────────────────────────────
export const CHART_PALETTE = [
  "#3b82f6",
  "#8b5cf6",
  "#f59e0b",
  "#ef4444",
  "#10b981",
  "#ec4899",
  "#06b6d4",
  "#f97316",
];

// ── KPI Thresholds ───────────────────────────────────────────────────
export const KPI_CONFIG = {
  avg_coverage_score: {
    label: "Avg Coverage Score",
    format: "percent",
    good: 0.95,
    warn: 0.85,
    icon: "shield",
    description:
      "Ratio of actual staff on-site to the scheduled requirement. A score of 1.0 (100%) means every scheduled slot was filled. Below 0.85 is critical understaffing; above 1.05 indicates overstaffing.",
  },
  total_overtime_hours_30d: {
    label: "Overtime Hours (30d)",
    format: "number",
    good: 800,
    warn: 1500,
    icon: "clock",
    invertThreshold: true,
    description:
      "Total overtime hours logged across all locations in the past 30 days. Lower is better. High overtime signals chronic understaffing and increases labor costs by 1.5x the base rate.",
  },
  avg_cost_per_visit: {
    label: "Avg Cost / Visit",
    format: "currency",
    good: 42,
    warn: 50,
    icon: "dollar",
    invertThreshold: true,
    description:
      "Average labor cost divided by total patient visits. This measures workforce efficiency - how much labor spend is required to serve each patient. The $45 benchmark represents the industry target.",
  },
  shift_gap_rate: {
    label: "Shift Gap Rate",
    format: "percent",
    good: 0.1,
    warn: 0.2,
    icon: "alert",
    invertThreshold: true,
    description:
      "Percentage of scheduled shifts that had fewer staff than required. A gap occurs when actual headcount falls below the minimum staffing threshold for a shift window. Lower is better.",
  },
  avg_wait_time: {
    label: "Avg Wait Time",
    format: "minutes",
    good: 20,
    warn: 30,
    icon: "timer",
    invertThreshold: true,
    description:
      "Average patient wait time in minutes from check-in to provider contact. Directly correlated with staffing levels - understaffed locations have longer waits. Target is under 20 minutes.",
  },
  total_patient_visits_30d: {
    label: "Patient Visits (30d)",
    format: "integer",
    icon: "users",
    description:
      "Total patient visits across all locations in the past 30 days. This is a volume indicator that drives staffing needs. Higher volumes require proportionally more staff to maintain coverage.",
  },
};

// ── DQ Severity Weights ──────────────────────────────────────────────
export const DQ_SEVERITY_WEIGHTS = {
  Critical: 0.4,
  High: 0.3,
  Medium: 0.2,
  Low: 0.1,
};

// ── Region & Location Types ──────────────────────────────────────────
export const REGIONS = ["Northeast", "Midwest", "Southeast", "Southwest"];
export const LOCATION_TYPES = ["Urban", "Suburban", "Rural"];

// ── Day of Week Labels ───────────────────────────────────────────────
export const DOW_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

// ── Navigation Links ─────────────────────────────────────────────────
export const NAV_LINKS = [
  { path: "/", label: "Home" },
  { path: "/architecture", label: "Architecture" },
  { path: "/dashboard", label: "Staffing Dashboard" },
  { path: "/about-dashboard", label: "About Dashboard" },
  { path: "/data-quality", label: "Data Quality" },
  { path: "/sql-showcase", label: "SQL Showcase" },
  { path: "/how-i-built-this", label: "How I Built This" },
];

// ── Data Base URL ────────────────────────────────────────────────────
export const DATA_BASE_URL = "/data";
