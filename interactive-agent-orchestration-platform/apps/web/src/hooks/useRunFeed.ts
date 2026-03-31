import { useEffect, useMemo, useState } from "react";
import { mockRuns, mockSummary } from "../lib/mockData";

export function useRunFeed() {
  const [runs, setRuns] = useState(mockRuns);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setRuns((current) => [...current]);
    }, 4000);

    return () => window.clearInterval(timer);
  }, []);

  const summary = useMemo(() => mockSummary, [runs]);

  return { runs, summary };
}
