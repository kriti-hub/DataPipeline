import { useState, useEffect, useRef } from "react";
import { DATA_BASE_URL } from "../utils/constants";

const cache = new Map();

/**
 * Custom hook to fetch pre-computed JSON from /data/*.json
 *
 * @param {string} filename - e.g. "kpis.json"
 * @returns {{ data: any, loading: boolean, error: string|null }}
 */
export function useDataLoader(filename) {
  const [data, setData] = useState(() => cache.get(filename) ?? null);
  const [loading, setLoading] = useState(!cache.has(filename));
  const [error, setError] = useState(null);
  const abortRef = useRef(null);

  useEffect(() => {
    if (cache.has(filename)) {
      setData(cache.get(filename));
      setLoading(false);
      return;
    }

    const controller = new AbortController();
    abortRef.current = controller;

    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
        const url = `${DATA_BASE_URL}/${filename}`;
        const res = await fetch(url, { signal: controller.signal });
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        const json = await res.json();
        cache.set(filename, json);
        setData(json);
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchData();

    return () => controller.abort();
  }, [filename]);

  return { data, loading, error };
}

/**
 * Fetch multiple JSON files in parallel.
 *
 * @param {string[]} filenames - e.g. ["kpis.json", "staffing_coverage.json"]
 * @returns {{ data: object, loading: boolean, error: string|null }}
 */
export function useMultiDataLoader(filenames) {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchAll() {
      try {
        setLoading(true);
        setError(null);
        const results = {};
        await Promise.all(
          filenames.map(async (f) => {
            if (cache.has(f)) {
              results[f] = cache.get(f);
              return;
            }
            const url = `${DATA_BASE_URL}/${f}`;
            const res = await fetch(url, { signal: controller.signal });
            if (!res.ok)
              throw new Error(`Failed to load ${f}: HTTP ${res.status}`);
            const json = await res.json();
            cache.set(f, json);
            results[f] = json;
          })
        );
        setData(results);
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchAll();
    return () => controller.abort();
  }, [filenames.join(",")]);

  return { data, loading, error };
}
