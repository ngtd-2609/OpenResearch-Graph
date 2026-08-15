"use client";

import type { Paper } from "@/types/api";
import Link from "next/link";

export type ComparisonFeature = {
  id: string;
  title: string;
  year?: number | null;
  citations: number;
  openAccess: boolean;
  topic?: string;
  pros?: string;
  cons?: string;
  highlight?: string;
};

interface PaperComparisonMatrixProps {
  papers: Paper[];
  onRemove?: (paperId: string) => void;
  onClear?: () => void;
}

export default function PaperComparisonMatrix({
  papers,
  onRemove,
  onClear,
}: PaperComparisonMatrixProps) {
  if (!papers || papers.length === 0) return null;

  return (
    <section className="card comparison-matrix-card" aria-label="Bảng so sánh bài báo">
      <div className="comparison-header">
        <div>
          <h2 className="comparison-title">
            Bảng So sánh Nghiên cứu Đối chiếu ({papers.length} bài báo)
          </h2>
          <p className="muted text-sm">
            So sánh trực tiếp các công trình theo chỉ số ảnh hưởng, quyền truy cập và tóm tắt cốt lõi.
          </p>
        </div>
        {onClear && (
          <button className="secondary-button text-sm" onClick={onClear} type="button">
            Xóa danh sách so sánh
          </button>
        )}
      </div>

      <div className="comparison-table-wrapper">
        <table className="comparison-table">
          <thead>
            <tr>
              <th scope="col" style={{ width: "200px" }}>Tiêu chí</th>
              {papers.map((paper) => (
                <th key={paper.id} scope="col">
                  <div className="comparison-th-content">
                    <Link className="comparison-paper-link" href={`/papers/${paper.id}`}>
                      {paper.title}
                    </Link>
                    {onRemove && (
                      <button
                        aria-label={`Bỏ bài ${paper.title}`}
                        className="comparison-remove-btn"
                        onClick={() => onRemove(paper.id)}
                        type="button"
                      >
                        ×
                      </button>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row">Năm xuất bản</th>
              {papers.map((paper) => (
                <td key={paper.id}>
                  <span className="badge">{paper.publication_year ?? "N/A"}</span>
                </td>
              ))}
            </tr>
            <tr>
              <th scope="row">Trích dẫn (Citations)</th>
              {papers.map((paper) => (
                <td key={paper.id}>
                  <strong className="citation-count">{paper.cited_by_count.toLocaleString()}</strong> lượt
                </td>
              ))}
            </tr>
            <tr>
              <th scope="row">Quyền truy cập</th>
              {papers.map((paper) => (
                <td key={paper.id}>
                  {paper.is_open_access ? (
                    <span className="badge badge-success">Open Access (Miễn phí)</span>
                  ) : (
                    <span className="badge badge-neutral">Restricted</span>
                  )}
                </td>
              ))}
            </tr>
            <tr>
              <th scope="row">Nguồn xuất bản</th>
              {papers.map((paper) => (
                <td key={paper.id}>
                  <span className="muted">{paper.source_name || "Nguồn học thuật"}</span>
                </td>
              ))}
            </tr>
            <tr>
              <th scope="row">Tóm lược cốt lõi</th>
              {papers.map((paper) => (
                <td key={paper.id} className="comparison-abstract">
                  {paper.abstract ? (
                    <p className="line-clamp-4 text-sm">{paper.abstract}</p>
                  ) : (
                    <span className="muted text-sm italic">Chưa có abstract chi tiết</span>
                  )}
                </td>
              ))}
            </tr>
            <tr>
              <th scope="row">Thao tác nhanh</th>
              {papers.map((paper) => (
                <td key={paper.id}>
                  <div className="row wrap gap-2">
                    <Link className="button text-xs" href={`/papers/${paper.id}`}>
                      Xem chi tiết
                    </Link>
                    {paper.open_access_url && (
                      <a
                        className="secondary-button text-xs"
                        href={paper.open_access_url}
                        rel="noreferrer"
                        target="_blank"
                      >
                        Đọc PDF gốc
                      </a>
                    )}
                  </div>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}
