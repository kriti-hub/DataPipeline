/**
 * Renders sample query results as a styled table.
 */
export default function ResultsTable({ columns, rows }) {
  if (!rows?.length) return null;

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-gray-50 border-b border-gray-200">
            {columns.map((col) => (
              <th key={col} className="text-left py-2 px-3 font-medium text-gray-600 whitespace-nowrap">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri} className="border-b border-gray-100 hover:bg-gray-50">
              {columns.map((col) => (
                <td key={col} className="py-2 px-3 text-gray-700 whitespace-nowrap">
                  {row[col] ?? "--"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
