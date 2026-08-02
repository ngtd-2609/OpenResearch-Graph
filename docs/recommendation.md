# Hệ thống khuyến nghị

Ranker development là hệ thống hybrid, không chỉ sắp xếp theo citation.

## Tín hiệu

- Content profile: embedding của các paper người dùng đã save/like/read.
- Collaborative co-occurrence: hành vi implicit giữa người dùng và paper.
- Graph: Personalized PageRank trên citation graph.
- Popularity: citation đã log-normalize.
- Recency: decay theo publication year.
- Open access: boost nhỏ, có cấu hình.
- Negative feedback: dislike/dismiss làm giảm điểm.

## Công thức

Các thành phần được normalize và kết hợp bằng trọng số trong `Settings`. API trả component scores và explanation để dễ debug.

## Cold start

Người dùng mới nhận paper phổ biến/gần đây nhưng có MMR diversity. Khi có tương tác, content profile và collaborative signal dần có trọng số.

## Diversity

MMR tránh trả nhiều paper gần như giống nhau. Diversity không nên làm mất hoàn toàn relevance; cần tuning `lambda` trên tập validation.

## Evaluation

Các metrics trong `app/ml/evaluation` gồm Precision@K, Recall@K, nDCG@K, coverage/diversity có thể bổ sung theo dataset. Evaluation tối thiểu phải so với popularity baseline.

## Giới hạn

Seed interactions chỉ chứng minh code path, không chứng minh chất lượng recommendation. Trước khi trình bày với nhà tuyển dụng, hãy chạy notebook `03_recommendation_baseline.ipynb`, lưu metrics và mô tả dataset rõ ràng.

## Tránh leakage

Chia tương tác theo thời gian: train bằng hành vi cũ, test bằng hành vi mới hơn. Không random split toàn bộ interaction vì dễ để tương lai rò vào train.
