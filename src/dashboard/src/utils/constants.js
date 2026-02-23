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
  },
  total_overtime_hours_30d: {
    label: "Overtime Hours (30d)",
    format: "number",
    good: 800,
    warn: 1500,
    icon: "clock",
    invertThreshold: true, // lower is better
  },
  avg_cost_per_visit: {
    label: "Avg Cost / Visit",
    format: "currency",
    good: 42,
    warn: 50,
    icon: "dollar",
    invertThreshold: true,
  },
  shift_gap_rate: {
    label: "Shift Gap Rate",
    format: "percent",
    good: 0.1,
    warn: 0.2,
    icon: "alert",
    invertThreshold: true,
  },
  avg_wait_time: {
    label: "Avg Wait Time",
    format: "minutes",
    good: 20,
    warn: 30,
    icon: "timer",
    invertThreshold: true,
  },
  total_patient_visits_30d: {
    label: "Patient Visits (30d)",
    format: "integer",
    icon: "users",
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
  { path: "/data-quality", label: "Data Quality" },
  { path: "/sql-showcase", label: "SQL Showcase" },
  { path: "/how-i-built-this", label: "How I Built This" },
];

// ── Data Base URL ────────────────────────────────────────────────────
export const DATA_BASE_URL = "/data";
