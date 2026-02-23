import { useState } from "react";

/**
 * Syntax-highlighted SQL code block with copy button.
 * Uses basic keyword highlighting without requiring PrismJS at runtime.
 */
const SQL_KEYWORDS = new Set([
  "SELECT", "FROM", "WHERE", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER",
  "ON", "AND", "OR", "NOT", "IN", "AS", "WITH", "GROUP", "BY", "ORDER",
  "HAVING", "LIMIT", "OFFSET", "UNION", "ALL", "DISTINCT", "CASE", "WHEN",
  "THEN", "ELSE", "END", "OVER", "PARTITION", "WINDOW", "ROWS", "BETWEEN",
  "UNBOUNDED", "PRECEDING", "FOLLOWING", "CURRENT", "ROW", "AVG", "SUM",
  "COUNT", "MIN", "MAX", "ROUND", "COALESCE", "NULLIF", "CAST", "EXTRACT",
  "DATE_DIFF", "DATE_TRUNC", "DENSE_RANK", "ROW_NUMBER", "RANK", "LAG",
  "LEAD", "FIRST_VALUE", "LAST_VALUE", "CTE", "INSERT", "INTO", "VALUES",
  "UPDATE", "SET", "DELETE", "CREATE", "TABLE", "VIEW", "INDEX", "DROP",
  "ALTER", "ADD", "COLUMN", "PRIMARY", "KEY", "FOREIGN", "REFERENCES",
  "NULL", "TRUE", "FALSE", "IS", "LIKE", "EXISTS", "ANY", "SOME",
  "CROSS", "NATURAL", "USING", "EXCEPT", "INTERSECT", "FETCH", "NEXT",
  "RECURSIVE", "LATERAL", "GENERATE_ARRAY", "UNNEST", "STRUCT", "ARRAY",
  "FORMAT_DATE", "PARSE_DATE", "DATE", "TIMESTAMP", "INTERVAL", "DAY",
  "MONTH", "YEAR", "HOUR", "MINUTE", "SECOND", "INT64", "FLOAT64",
  "STRING", "BOOL", "BYTES", "ASC", "DESC",
]);

function highlightSQL(code) {
  return code.split("\n").map((line, li) => {
    // Handle comments
    if (line.trim().startsWith("--")) {
      return (
        <div key={li} className="text-gray-400 italic">
          {line}
        </div>
      );
    }

    const tokens = line.split(/(\b\w+\b|[^a-zA-Z0-9_\s]+|\s+)/g);
    return (
      <div key={li}>
        {tokens.map((token, ti) => {
          if (SQL_KEYWORDS.has(token.toUpperCase())) {
            return (
              <span key={ti} className="text-blue-600 font-medium">
                {token}
              </span>
            );
          }
          if (/^\d+(\.\d+)?$/.test(token)) {
            return (
              <span key={ti} className="text-amber-600">
                {token}
              </span>
            );
          }
          if (/^'.*'$/.test(token)) {
            return (
              <span key={ti} className="text-green-600">
                {token}
              </span>
            );
          }
          return <span key={ti}>{token}</span>;
        })}
      </div>
    );
  });
}

export default function SQLBlock({ sql, title }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-xl border border-gray-200 overflow-hidden">
      {title && (
        <div className="bg-gray-50 px-4 py-2 border-b border-gray-200 flex items-center justify-between">
          <span className="text-sm font-medium text-gray-600">{title}</span>
          <button
            onClick={handleCopy}
            className="text-xs px-2 py-1 rounded bg-white border border-gray-200 text-gray-500 hover:text-gray-900 hover:border-gray-300 transition-colors"
          >
            {copied ? "Copied!" : "Copy"}
          </button>
        </div>
      )}
      <pre className="bg-gray-900 text-gray-100 p-4 overflow-x-auto text-sm leading-relaxed font-mono">
        <code>{highlightSQL(sql)}</code>
      </pre>
    </div>
  );
}
