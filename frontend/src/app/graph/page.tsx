"use client";

import { api } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import cytoscape, { type Core } from "cytoscape";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";

type GraphData = {
  nodes: cytoscape.ElementDefinition[];
  edges: cytoscape.ElementDefinition[];
  truncated: boolean;
};

const LAYOUTS = [
  { id: "cose", label: "Lực đẩy (COSE)" },
  { id: "concentric", label: "Đồng tâm (Concentric)" },
  { id: "circle", label: "Vòng tròn (Circle)" },
  { id: "breadthfirst", label: "Cây phân cấp (Hierarchy)" },
];

export default function GraphPage() {
  const container = useRef<HTMLDivElement>(null);
  const graph = useRef<Core | null>(null);
  const [selected, setSelected] = useState<Record<string, unknown> | null>(null);
  const [currentLayout, setCurrentLayout] = useState("cose");
  const query = useQuery({
    queryKey: ["citation-graph"],
    queryFn: () => api<GraphData>("/graphs/citations"),
  });

  useEffect(() => {
    if (!container.current || !query.data) return;
    const instance = cytoscape({
      container: container.current,
      elements: [...query.data.nodes, ...query.data.edges],
      layout: { name: currentLayout } as cytoscape.LayoutOptions,
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            "font-size": 9,
            "text-max-width": "130px",
            "text-wrap": "ellipsis",
            width: "mapData(citations, 0, 190000, 24, 76)",
            height: "mapData(citations, 0, 190000, 24, 76)",
            "background-color": "#2563eb",
            color: "#0f172a",
            "font-weight": 600,
          },
        },
        {
          selector: "edge",
          style: {
            width: 1.5,
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            "line-color": "#94a3b8",
            "target-arrow-color": "#94a3b8",
            opacity: 0.7,
          },
        },
        {
          selector: ":selected",
          style: {
            "border-width": 3,
            "border-color": "#f59e0b",
            "background-color": "#1d4ed8",
          },
        },
      ],
    });

    instance.on("tap", "node", (event) => setSelected(event.target.data()));
    graph.current = instance;
    return () => {
      instance.destroy();
      graph.current = null;
    };
  }, [query.data, currentLayout]);

  function changeLayout(layoutName: string) {
    setCurrentLayout(layoutName);
    if (graph.current) {
      graph.current.layout({ name: layoutName } as cytoscape.LayoutOptions).run();
    }
  }

  function zoomIn() {
    graph.current?.zoom(graph.current.zoom() * 1.25);
  }

  function zoomOut() {
    graph.current?.zoom(graph.current.zoom() * 0.8);
  }

  function fitView() {
    graph.current?.fit(undefined, 30);
  }

  return (
    <main className="container">
      <header className="page-header">
        <div>
          <h1>Mạng lưới Đồ thị Trích dẫn (Citation Network)</h1>
          <p className="muted">
            Kích thước node biểu diễn số lượng citation; liên kết mũi tên biểu thị quan hệ trích dẫn chéo.
          </p>
        </div>

        {/* Graph Controls Toolbar */}
        <div className="row wrap gap-2 items-center">
          <div className="graph-layout-selector">
            {LAYOUTS.map((layout) => (
              <button
                key={layout.id}
                className={`graph-toolbar-btn ${currentLayout === layout.id ? "graph-toolbar-btn-active" : ""}`}
                onClick={() => changeLayout(layout.id)}
                type="button"
              >
                {layout.label}
              </button>
            ))}
          </div>

          <div className="row gap-1">
            <button aria-label="Phóng to" className="graph-icon-btn" onClick={zoomIn} type="button">
              +
            </button>
            <button aria-label="Thu nhỏ" className="graph-icon-btn" onClick={zoomOut} type="button">
              −
            </button>
            <button aria-label="Căn chỉnh toàn màn hình" className="graph-icon-btn" onClick={fitView} type="button">
              ⛶
            </button>
          </div>
        </div>
      </header>

      {query.data?.truncated && (
        <div className="card text-xs muted mb-3">
          💡 Đồ thị đã được giới hạn node để bảo đảm hiệu năng hiển thị trên trình duyệt.
        </div>
      )}
      {query.error && <p className="error">{query.error.message}</p>}

      <div className="grid two-columns">
        <section className="card graph-canvas-card">
          <div ref={container} style={{ height: 600, width: "100%" }} />
        </section>

        <aside className="card stack graph-inspector-card">
          <h2>Thông tin Node Đang Chọn</h2>
          {selected ? (
            <div className="stack gap-3">
              <div>
                <h3 className="text-base font-semibold text-primary">
                  {String(selected.label || selected.id || "Bài báo")}
                </h3>
                <div className="row wrap gap-2 mt-2">
                  <span className="badge">
                    {selected.citations ? `${Number(selected.citations).toLocaleString()} citations` : "0 citations"}
                  </span>
                  {selected.year ? <span className="badge badge-neutral">Năm {String(selected.year)}</span> : null}
                </div>
              </div>

              {Boolean(selected.id) && (
                <div className="row wrap gap-2 mt-4 pt-3 border-t">
                  <Link className="button text-xs" href={`/search?query=${encodeURIComponent(String(selected.label || ""))}`}>
                    Tìm bài liên quan
                  </Link>
                </div>
              )}

              <details className="mt-2 text-xs text-muted">
                <summary className="cursor-pointer font-semibold">Xem chi tiết JSON</summary>
                <pre className="mt-2 p-2 bg-slate-50 rounded overflow-x-auto">
                  {JSON.stringify(selected, null, 2)}
                </pre>
              </details>
            </div>
          ) : (
            <div className="text-center py-12 muted">
              <p className="text-3xl mb-2">👆</p>
              <p className="text-sm">Nhấp vào bất kỳ node bài báo nào trên đồ thị để xem thông tin chi tiết.</p>
            </div>
          )}
        </aside>
      </div>
    </main>
  );
}
