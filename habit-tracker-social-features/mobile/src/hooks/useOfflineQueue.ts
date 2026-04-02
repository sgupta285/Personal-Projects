import { useCallback, useEffect, useState } from "react";
import { getItem, setItem } from "../services/storage";

const QUEUE_KEY = "offlineQueue";

export function useOfflineQueue() {
  const [items, setItems] = useState<string[]>([]);

  useEffect(() => {
    getItem(QUEUE_KEY).then((value) => {
      if (value) {
        setItems(JSON.parse(value));
      }
    });
  }, []);

  const enqueue = useCallback(async (item: string) => {
    const next = [...items, item];
    setItems(next);
    await setItem(QUEUE_KEY, JSON.stringify(next));
  }, [items]);

  const clear = useCallback(async () => {
    setItems([]);
    await setItem(QUEUE_KEY, JSON.stringify([]));
  }, []);

  return { items, enqueue, clear };
}
