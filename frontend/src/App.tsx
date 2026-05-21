import RobotViewer3D from "./components/RobotViewer3D";
import StatusDashboard from "./components/StatusDashboard";
import CommandPanel from "./components/CommandPanel";
import { useRobotData } from "./hooks/useRobotData";

export default function App() {
  const data = useRobotData();
  return (
    <main style={{ height: "100vh", display: "grid", gridTemplateColumns: "1fr 360px", background: "#08090f", color: "#e5e7eb", fontFamily: "system-ui", overflow: "hidden" }}>
      <section style={{ minHeight: 0 }}>
        <RobotViewer3D robots={data.robots} selectedRobotId={data.selectedRobotId} onSelectRobot={data.setSelectedRobotId} />
      </section>
      <aside style={{ padding: 16, borderLeft: "1px solid #222", overflow: "auto" }}>
        <h1 style={{ fontSize: 20, margin: "0 0 12px" }}>Robot Fleet Manager</h1>
        <StatusDashboard robots={data.robots} simState={data.simState} connected={data.connected} />
        <CommandPanel robots={data.robots} selectedRobotId={data.selectedRobotId} onSendCommand={data.sendCommand} onBroadcast={data.broadcastCommand} onSimControl={data.simulationControl} />
      </aside>
    </main>
  );
}
