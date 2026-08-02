"use client";

import { api } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import cytoscape, { type Core } from "cytoscape";
import { useEffect, useRef, useState } from "react";

type GraphData = {
  nodes: cytoscape.ElementDefinition[];
  edges: cytoscape.ElementDefinition[];
  truncated: boolean;
};

export default function GraphPage() {
  const container = useRef<HTMLDivElement>(null);
  const graph = useRef<Core | null>(null);
  const [selected, setSelected] = useState<Record<string, unknown> | null>(null);
  const query = useQuery({ queryKey: ["citation-graph"], queryFn: () => api<GraphData>("/graphs/citations") });

  useEffect(() => {
    if (!container.current || !query.data) return;
    const instance = cytoscape({
      container: container.current,
      elements: [...query.data.nodes, ...query.data.edges],
      layout: { name: "cose", animate: false },
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            "font-size": 8,
            "text-max-width": 120,
            "text-wrap": "ellipsis",
            width: "mapData(citations, 0, 190000, 22, 72)",
            height: "mapData(citations, 0, 190000, 22, 72)",
            "background-color": "#335cff",
          },
        },
        {
          selector: "edge",
          style: { width: 1, "target-arrow-shape": "triangle", "curve-style": "bezier" },
        },
        { selector: ":selected", style: { "border-width": 3, "border-color": "#172033" } },
      ],
    });
    instance.on("tap", "node", (event) => setSelected(event.target.data()));
    graph.current = instance;
    return () => {
      instance.destroy();
      graph.current = null;
    };
  }, [query.data]);

  return (
    <main className="container">
      <header className="page-header">
        <div>
          <h1>Mạng trích dẫn</h1>
          <p className="muted">Kích thước node dựa trên citation; PageRank được tính ở backend.</p>
        </div>
      </header>
      {query.data?.truncated && <p className="muted">Đồ thị đã được giới hạn node để bảo đảm hiệu năng trình duyệt.</p>}
      {query.error && <p className="error">{query.error.message}</p>}
      <div className="grid two-columns">
        <section className="card"><div ref={container} style={{ height: 620 }} /></section>
        <aside className="card">
          <h2>Node được chọn</h2>
          {selected ? <pre>{JSON.stringify(selected, null, 2)}</pre> : <p className="muted">Bấm một node để xem metadata.</p>}
        </aside>
      </div>
    </main>
  );
}
