/**
 * Format a number as a percentage string.
 * @param {number} value - Decimal (0.959 → "95.9%")
 * @param {number} decimals - Decimal places (default 1)
 */
export function formatPercent(value, decimals = 1) {
  if (value == null) return "--";
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format a number with comma separators.
 * @param {number} value
 * @param {number} decimals
 */
export function formatNumber(value, decimals = 0) {
  if (value == null) return "--";
  return value.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * Format a number as USD currency.
 * @param {number} value
 * @param {number} decimals
 */
export function formatCurrency(value, decimals = 2) {
  if (value == null) return "--";
  return `$${value.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}`;
}

/**
 * Format a number with a "min" suffix.
 * @param {number} value
 */
export function formatMinutes(value) {
  if (value == null) return "--";
  return `${value.toFixed(1)} min`;
}

/**
 * Format an ISO timestamp as a readable date string.
 * @param {string} isoString
 * @param {object} opts - Intl.DateTimeFormat options
 */
export function formatDate(isoString, opts = {}) {
  if (!isoString) return "--";
  const d = new Date(isoString);
  return d.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    ...opts,
  });
}

/**
 * Format an ISO timestamp as a readable date + time string.
 * @param {string} isoString
 */
export function formatDateTime(isoString) {
  if (!isoString) return "--";
  const d = new Date(isoString);
  return d.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short",
  });
}

/**
 * Format a duration in seconds to a human-friendly string.
 * @param {number} seconds
 */
export function formatDuration(seconds) {
  if (seconds == null) return "--";
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const m = Math.floor(seconds / 60);
  const s = (seconds % 60).toFixed(0);
  return `${m}m ${s}s`;
}

/**
 * Return time-ago string (e.g. "2 hours ago").
 * @param {string} isoString
 */
export function timeAgo(isoString) {
  if (!isoString) return "--";
  const now = new Date();
  const then = new Date(isoString);
  const diffMs = now - then;
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin} min ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  return `${diffDay}d ago`;
}

/**
 * Format a KPI value based on its configured format type.
 * @param {number} value
 * @param {string} format - One of: percent, currency, number, integer, minutes
 */
export function formatKPI(value, format) {
  switch (format) {
    case "percent":
      return formatPercent(value);
    case "currency":
      return formatCurrency(value);
    case "number":
      return formatNumber(value, 1);
    case "integer":
      return formatNumber(value, 0);
    case "minutes":
      return formatMinutes(value);
    default:
      return String(value ?? "--");
  }
}

/**
 * Get a month label from YYYY-MM string.
 * @param {string} monthStr - e.g. "2025-03"
 */
export function formatMonthLabel(monthStr) {
  if (!monthStr) return "";
  const [year, month] = monthStr.split("-");
  const d = new Date(Number(year), Number(month) - 1);
  return d.toLocaleDateString("en-US", { month: "short", year: "2-digit" });
}
