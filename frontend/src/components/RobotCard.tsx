import type { RobotData } from "../types/robot";

export default function RobotCard({ robot }: { robot: RobotData }) {
  return <div>{robot.name} - {robot.sensor_data.task_state}</div>;
}
