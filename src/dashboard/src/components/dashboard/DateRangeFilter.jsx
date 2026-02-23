import { REGIONS, LOCATION_TYPES } from "../../utils/constants";

export default function DateRangeFilter({ filters, onChange }) {
  const toggleArrayItem = (key, item) => {
    const current = filters[key] || [];
    const next = current.includes(item)
      ? current.filter((x) => x !== item)
      : [...current, item];
    onChange({ ...filters, [key]: next });
  };

  return (
    <div className="card p-4 flex flex-wrap items-center gap-4">
      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1.5">Region</label>
        <div className="flex flex-wrap gap-1.5">
          {REGIONS.map((r) => {
            const active = (filters.regions || []).includes(r);
            return (
              <button key={r} onClick={() => toggleArrayItem("regions", r)}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${active ? "bg-brand-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>
                {r}
              </button>
            );
          })}
        </div>
      </div>
      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1.5">Location Type</label>
        <div className="flex flex-wrap gap-1.5">
          {LOCATION_TYPES.map((t) => {
            const active = (filters.locationTypes || []).includes(t);
            return (
              <button key={t} onClick={() => toggleArrayItem("locationTypes", t)}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${active ? "bg-brand-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>
                {t}
              </button>
            );
          })}
        </div>
      </div>
      {((filters.regions?.length > 0) || (filters.locationTypes?.length > 0)) && (
        <button onClick={() => onChange({ regions: [], locationTypes: [] })}
          className="px-3 py-1 rounded-lg text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 transition-colors ml-auto">
          Clear Filters
        </button>
      )}
    </div>
  );
}
