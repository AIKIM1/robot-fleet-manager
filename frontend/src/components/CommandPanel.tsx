import type { RobotData } from "../types/robot";

export default function CommandPanel({ robots, selectedRobotId, onSendCommand, onBroadcast, onSimControl }: {
  robots: RobotData[];
  selectedRobotId: string | null;
  onSendCommand: (robotId: string, command: string) => void;
  onBroadcast: (command: string) => void;
  onSimControl: (action: string) => void;
}) {
  const target = selectedRobotId ?? robots[0]?.id;
  return (
    <section style={{ marginTop: 16, display: "grid", gap: 8 }}>
      <button disabled={!target} onClick={() => target && onSendCommand(target, "stop")}>선택 로봇 정지</button>
      <button disabled={!target} onClick={() => target && onSendCommand(target, "charge")}>선택 로봇 충전</button>
      <button onClick={() => onBroadcast("resume")}>전체 재개</button>
      <button onClick={() => onSimControl("reset")}>시뮬레이션 초기화</button>
    </section>
  );
}
