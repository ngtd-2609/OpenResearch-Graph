import Link from "next/link";

const features = [
  ["Hybrid Search", "Full-text, embedding, citation score, recency và cross-encoder reranking."],
  ["Citation Analytics", "Phân tích xu hướng, tác giả, tổ chức và mạng ảnh hưởng."],
  ["PDF RAG", "Truy xuất đoạn liên quan, chống prompt injection và citation theo trang."],
  ["Recommendations", "Content, collaborative filtering, Personalized PageRank và diversity."],
  ["OpenAlex Pipeline", "Batch ingestion, checkpoint, resume, retry và dead-letter records."],
  ["Secure Accounts", "Argon2, JWT ngắn hạn, refresh rotation và phân quyền."],
];

export default function HomePage() {
  return (
    <main className="container">
      <section className="hero">
        <span className="badge">Development mode · Seed data · Mock billing</span>
        <h1>Khám phá tri thức khoa học bằng tìm kiếm, đồ thị trích dẫn và RAG.</h1>
        <p className="muted">
          Một hệ thống portfolio end-to-end cho AI, Data Science, NLP, recommendation và web engineering.
        </p>
        <div className="row wrap">
          <Link className="button" href="/search">Bắt đầu tìm paper</Link>
          <Link className="secondary-button" href="/chat">Chat với PDF</Link>
        </div>
      </section>
      <section className="grid" aria-label="Tính năng chính">
        {features.map(([title, description]) => (
          <article className="card" key={title}>
            <h2>{title}</h2>
            <p className="muted">{description}</p>
          </article>
        ))}
      </section>
    </main>
  );
}
