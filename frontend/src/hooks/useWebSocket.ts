import { useEffect, useState } from "react";
import type { SimulationState } from "../types/robot";

export function useWebSocket(url: string) {
  const [state, setState] = useState<SimulationState | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    let ws: WebSocket | undefined;

    const connect = () => {
      ws = new WebSocket(url);
      ws.onopen = () => setConnected(true);
      ws.onmessage = (event) => setState(JSON.parse(event.data));
      ws.onclose = () => {
        setConnected(false);
        timer = setTimeout(connect, 2000);
      };
      ws.onerror = () => ws?.close();
    };

    connect();
    return () => {
      if (timer) clearTimeout(timer);
      ws?.close();
    };
  }, [url]);

  return { state, connected };
}
