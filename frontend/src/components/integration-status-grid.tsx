import StatusBadge from "@/components/status-badge";

export type IntegrationStatus = {
  name: string;
  configured: boolean;
  status: string;
  message: string;
  latency_ms?: number;
  checked_at: string;
};

function tone(status: string): "neutral" | "success" | "warning" | "error" {
  if (status === "healthy") return "success";
  if (status === "error") return "error";
  if (["mock", "seed-mode", "console"].includes(status)) return "warning";
  return "neutral";
}

export default function IntegrationStatusGrid({ items }: { items: IntegrationStatus[] }) {
  return (
    <div className="grid">
      {items.map((integration) => (
        <article className="card stack" key={integration.name}>
          <div className="row wrap">
            <h2>{integration.name}</h2>
            <StatusBadge tone={tone(integration.status)}>{integration.status}</StatusBadge>
          </div>
          <p>{integration.message}</p>
          <dl className="integration-meta">
            <div><dt>Configured</dt><dd>{integration.configured ? "Có" : "Không"}</dd></div>
            {integration.latency_ms !== undefined && <div><dt>Latency</dt><dd>{integration.latency_ms} ms</dd></div>}
            <div><dt>Checked</dt><dd>{new Date(integration.checked_at).toLocaleString("vi-VN")}</dd></div>
          </dl>
        </article>
      ))}
    </div>
  );
}
