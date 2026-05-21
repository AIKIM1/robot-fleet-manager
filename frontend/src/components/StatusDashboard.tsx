import type { RobotData, SimulationState } from "../types/robot";

export default function StatusDashboard({ robots, simState, connected }: { robots: RobotData[]; simState: SimulationState | null; connected: boolean }) {
  return (
    <section style={{ display: "grid", gap: 8 }}>
      <div>연결: <b style={{ color: connected ? "#22c55e" : "#ef4444" }}>{connected ? "ON" : "OFF"}</b></div>
      <div>로봇: {robots.length}대</div>
      <div>처리: {simState?.total_parcels ?? 0}건</div>
      <div>평균 배터리: {simState?.kpis?.fleet_battery_avg ?? 0}%</div>
      <hr style={{ borderColor: "#222", width: "100%" }} />
      {robots.map((r) => (
        <div key={r.id} style={{ padding: 8, background: "#111827", borderRadius: 8 }}>
          <b>{r.name}</b><br />
          상태: {r.sensor_data.task_state}<br />
          배터리: {r.sensor_data.battery_level.toFixed(0)}%
        </div>
      ))}
    </section>
  );
}
