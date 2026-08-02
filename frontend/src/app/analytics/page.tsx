"use client";

import { api } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import * as echarts from "echarts";
import { useEffect, useRef } from "react";

type Trends = { series: { year: number; papers: number; citations: number }[] };

export default function AnalyticsPage() {
  const chartContainer = useRef<HTMLDivElement>(null);
  const query = useQuery({ queryKey: ["trends"], queryFn: () => api<Trends>("/analytics/trends") });

  useEffect(() => {
    if (!chartContainer.current || !query.data) return;
    const chart = echarts.init(chartContainer.current);
    chart.setOption({
      tooltip: { trigger: "axis" },
      legend: { data: ["Papers", "Citations"] },
      xAxis: { type: "category", data: query.data.series.map((item) => item.year) },
      yAxis: { type: "value" },
      series: [
        { name: "Papers", type: "bar", data: query.data.series.map((item) => item.papers) },
        { name: "Citations", type: "line", data: query.data.series.map((item) => item.citations) },
      ],
    });
    const resize = () => chart.resize();
    window.addEventListener("resize", resize);
    return () => {
      window.removeEventListener("resize", resize);
      chart.dispose();
    };
  }, [query.data]);

  return (
    <main className="container">
      <h1>Xu hướng nghiên cứu</h1>
      {query.error && <p className="error">{query.error.message}</p>}
      <section className="card">
        <div ref={chartContainer} style={{ height: 460 }} aria-label="Biểu đồ xu hướng xuất bản và citation" />
      </section>
    </main>
  );
}
