import { useCallback, useState } from "react";
import { useWebSocket } from "./useWebSocket";

const API_BASE = `http://${window.location.hostname}:8000/api`;
const WS_URL = `ws://${window.location.hostname}:8000/ws`;

export function useRobotData() {
  const { state, connected } = useWebSocket(WS_URL);
  const [selectedRobotId, setSelectedRobotId] = useState<string | null>(null);
  const robots = state?.robots ?? [];

  const sendCommand = useCallback(async (robotId: string, commandType: string) => {
    await fetch(`${API_BASE}/robots/${robotId}/command`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command_type: commandType, params: {} }),
    });
  }, []);

  const broadcastCommand = useCallback(async (commandType: string) => {
    await fetch(`${API_BASE}/robots/broadcast`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command_type: commandType, params: {} }),
    });
  }, []);

  const simulationControl = useCallback(async (action: string) => {
    await fetch(`${API_BASE}/simulation/${action}`, { method: "POST" });
  }, []);

  return { robots, selectedRobotId, setSelectedRobotId, connected, simState: state, sendCommand, broadcastCommand, simulationControl };
}
