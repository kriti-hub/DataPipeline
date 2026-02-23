/**
 * Key Takeaway banner shown at the top of each chart.
 * Provides a quick insight and optional recommendation.
 */
export default function KeyTakeaway({ insight, recommendation }) {
  return (
    <div className="mb-4 p-3 bg-brand-50 border border-brand-200 rounded-lg">
      <div className="flex items-start gap-2">
        <svg
          className="w-4 h-4 text-brand-600 mt-0.5 flex-shrink-0"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={2}
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 18v-5.25m0 0a6.01 6.01 0 0 0 1.5-.189m-1.5.189a6.01 6.01 0 0 1-1.5-.189m3.75 7.478a12.06 12.06 0 0 1-4.5 0m3.75 2.383a14.406 14.406 0 0 1-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 1 0-7.517 0c.85.493 1.509 1.333 1.509 2.316V18"
          />
        </svg>
        <div>
          <p className="text-sm font-medium text-brand-900">{insight}</p>
          {recommendation && (
            <p className="text-xs text-brand-700 mt-1">
              <span className="font-semibold">Recommendation:</span> {recommendation}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
