export type TaskState = "IDLE" | "PICKING" | "MOVING" | "DROPPING" | "RETURNING" | "CHARGING" | "WAITING_CHARGE";

export interface SensorData {
  carrying_parcel: boolean;
  parcel_destination: string;
  parcel_id: string;
  task_state: TaskState;
  parcels_sorted: number;
  target_position: number[];
  battery_level: number;
  battery_charging: boolean;
  charging_station_id: number;
  current_speed: number;
  total_distance: number;
  parcel_weight: number;
  parcel_size_category: string;
  errors_count: number;
  uptime_seconds: number;
  obstacle_detected: boolean;
  joint_angles: number[];
  joint_velocities: number[];
  forces: number[];
  torques: number[];
}

export interface RobotData {
  id: string;
  name: string;
  status: string;
  position: [number, number, number];
  sensor_data: SensorData;
}

export interface SimulationState {
  step: number;
  sim_time: number;
  robots: RobotData[];
  zone_counts?: Record<string, number>;
  total_parcels?: number;
  paused?: boolean;
  kpis?: {
    throughput_per_hour: number;
    accuracy_rate: number;
    fleet_battery_avg: number;
    uptime_percent: number;
    total_errors: number;
    total_distance: number;
  };
}

export interface LogEntry {
  timestamp: number;
  level: "INFO" | "WARN" | "ERROR";
  event_type: string;
  robot_id: string | null;
  message: string;
}
