export default function AboutPage() {
  return (
    <main className="container">
      <h1>Phương pháp và giới hạn</h1>
      <section className="card stack">
        <p>
          OpenResearch Graph kết hợp metadata nghiên cứu, full-text/semantic search,
          graph algorithms, PDF retrieval và recommendation.
        </p>
        <p className="muted">
          Citation, recommendation và RAG là công cụ hỗ trợ khám phá, không thay thế
          đánh giá học thuật hoặc việc đọc nguồn gốc. Demo local dùng seed/mock khi
          chưa cấu hình dịch vụ ngoài.
        </p>
      </section>
    </main>
  );
}
