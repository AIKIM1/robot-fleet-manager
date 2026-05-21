import { Canvas } from "@react-three/fiber";
import { OrbitControls, Text } from "@react-three/drei";
import type { RobotData } from "../types/robot";

interface Props {
  robots: RobotData[];
  selectedRobotId: string | null;
  onSelectRobot: (id: string) => void;
}

export default function RobotViewer3D({ robots, selectedRobotId, onSelectRobot }: Props) {
  return (
    <Canvas camera={{ position: [8, 8, 8], fov: 45 }} style={{ background: "#0a0c14" }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 10, 5]} intensity={1} />
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[16, 12]} />
        <meshStandardMaterial color="#1f2937" />
      </mesh>
      {robots.map((robot, index) => (
        <group key={robot.id} position={[robot.position[0], 0.25, robot.position[1]]} onClick={() => onSelectRobot(robot.id)}>
          <mesh>
            <boxGeometry args={[0.5, 0.3, 0.5]} />
            <meshStandardMaterial color={robot.id === selectedRobotId ? "#facc15" : ["#3b82f6", "#22c55e", "#ef4444", "#a855f7"][index % 4]} />
          </mesh>
          <Text position={[0, 0.55, 0]} fontSize={0.16} color="white" anchorX="center">
            {robot.name}
          </Text>
        </group>
      ))}
      <OrbitControls target={[0, 0, 0]} />
    </Canvas>
  );
}
