from uuid import UUID

import networkx as nx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Citation, Paper


class GraphService:
    async def citation_graph(self, db: AsyncSession, limit: int = 80) -> dict:
        papers = list((await db.scalars(select(Paper).order_by(Paper.cited_by_count.desc()).limit(limit))).all())
        ids = {paper.id for paper in papers}
        edges = list((await db.execute(select(Citation.citing_paper_id, Citation.cited_paper_id))).all())
        graph = nx.DiGraph()
        for paper in papers:
            graph.add_node(str(paper.id))
        for source, target in edges:
            if source in ids and target in ids:
                graph.add_edge(str(source), str(target))
        pagerank = nx.pagerank(graph) if graph.number_of_nodes() else {}
        return {
            "nodes": [
                {
                    "data": {
                        "id": str(paper.id),
                        "label": paper.title,
                        "year": paper.publication_year,
                        "citations": paper.cited_by_count,
                        "pagerank": round(pagerank.get(str(paper.id), 0), 6),
                    }
                }
                for paper in papers
            ],
            "edges": [
                {"data": {"id": f"{source}-{target}", "source": str(source), "target": str(target)}}
                for source, target in edges
                if source in ids and target in ids
            ],
            "truncated": len(papers) == limit,
        }
