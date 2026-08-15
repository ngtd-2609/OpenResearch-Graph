"""Benchmark script to measure exact latency in ms across endpoints."""
import asyncio
import time
import httpx


async def main():
    base_url = "http://localhost:8000"
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        # 1. Health check latency
        t0 = time.perf_counter()
        resp = await client.get("/health")
        t_health = (time.perf_counter() - t0) * 1000.0
        print(f"1. GET /health: {t_health:.2f}ms (Status: {resp.status_code}, X-Process-Time: {resp.headers.get('X-Process-Time')})")

        # 2. Login latency
        t0 = time.perf_counter()
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@openresearch.dev", "password": "Student123!"},
        )
        t_login = (time.perf_counter() - t0) * 1000.0
        token = resp.json()["access_token"]
        print(f"2. POST /api/v1/auth/login: {t_login:.2f}ms (Status: {resp.status_code}, X-Process-Time: {resp.headers.get('X-Process-Time')})")

        headers = {"Authorization": f"Bearer {token}"}

        # 3. Search latency (First query)
        t0 = time.perf_counter()
        resp = await client.get("/api/v1/search/papers?query=transformer&page=1&per_page=10", headers=headers)
        t_search1 = (time.perf_counter() - t0) * 1000.0
        total_found = resp.json().get("total", 0)
        print(f"3. GET /api/v1/search/papers (First): {t_search1:.2f}ms (Found: {total_found}, X-Process-Time: {resp.headers.get('X-Process-Time')})")

        # 4. Search latency (Cached query)
        t0 = time.perf_counter()
        resp = await client.get("/api/v1/search/papers?query=transformer&page=1&per_page=10", headers=headers)
        t_search2 = (time.perf_counter() - t0) * 1000.0
        print(f"4. GET /api/v1/search/papers (Repeat): {t_search2:.2f}ms (X-Process-Time: {resp.headers.get('X-Process-Time')})")

        # 5. Citation Graph latency
        t0 = time.perf_counter()
        resp = await client.get("/api/v1/graphs/citations", headers=headers)
        t_graph = (time.perf_counter() - t0) * 1000.0
        print(f"5. GET /api/v1/graphs/citations: {t_graph:.2f}ms (Nodes: {len(resp.json().get('nodes', []))}, X-Process-Time: {resp.headers.get('X-Process-Time')})")

        # 6. Recommendations latency
        t0 = time.perf_counter()
        resp = await client.get("/api/v1/recommendations", headers=headers)
        t_rec = (time.perf_counter() - t0) * 1000.0
        print(f"6. GET /api/v1/recommendations: {t_rec:.2f}ms (Items: {len(resp.json())}, X-Process-Time: {resp.headers.get('X-Process-Time')})")

        # 7. Trends analytics latency
        t0 = time.perf_counter()
        resp = await client.get("/api/v1/analytics/trends", headers=headers)
        t_trends = (time.perf_counter() - t0) * 1000.0
        print(f"7. GET /api/v1/analytics/trends: {t_trends:.2f}ms (X-Process-Time: {resp.headers.get('X-Process-Time')})")


if __name__ == "__main__":
    asyncio.run(main())
