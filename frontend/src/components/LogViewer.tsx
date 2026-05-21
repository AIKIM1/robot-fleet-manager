import type { LogEntry } from "../types/robot";

export default function LogViewer({ logs = [] }: { logs?: LogEntry[] }) {
  return (
    <section>
      {logs.map((log) => (
        <div key={`${log.timestamp}-${log.message}`}>{log.message}</div>
      ))}
    </section>
  );
}
