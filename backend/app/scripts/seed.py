import asyncio
from datetime import date

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.entities import (
    Author,
    Citation,
    Institution,
    LibraryItem,
    Paper,
    PaperAuthor,
    PaperInstitution,
    PaperTopic,
    Plan,
    Subscription,
    Topic,
    User,
    UserPaperInteraction,
    UserRole,
)
from app.services.embedding_service import get_embedding_service

PAPERS = [
    ("Attention Is All You Need", 2017, 130000, "Transformers replace recurrence with self-attention for sequence modeling.", True, "NLP"),
    ("BERT: Pre-training of Deep Bidirectional Transformers", 2018, 90000, "Bidirectional transformer pretraining for language understanding.", True, "NLP"),
    ("Retrieval-Augmented Generation for Knowledge-Intensive NLP", 2020, 18000, "Combines parametric generation with non-parametric retrieval.", True, "IR"),
    ("Sentence-BERT", 2019, 20000, "Siamese BERT networks for sentence embeddings and semantic similarity.", True, "IR"),
    ("Graph Neural Networks: A Review", 2021, 6000, "A review of graph representation learning methods.", False, "GRAPH"),
    ("Deep Learning", 2015, 70000, "A broad review of deep learning methods and applications.", True, "ML"),
    ("Adam: A Method for Stochastic Optimization", 2014, 190000, "Adaptive estimates of lower-order moments for stochastic optimization.", True, "ML"),
    ("Learning to Rank for Information Retrieval", 2010, 9000, "Ranking models and evaluation methods for information retrieval.", False, "IR"),
    ("Collaborative Filtering for Implicit Feedback Datasets", 2008, 12000, "Matrix factorization for implicit user feedback.", True, "REC"),
    ("PageRank Citation Ranking", 1998, 30000, "Graph ranking based on recursive link importance.", True, "GRAPH"),
    ("Efficient Estimation of Word Representations in Vector Space", 2013, 65000, "Efficient neural word embeddings.", True, "NLP"),
    ("A Survey on Explainable Artificial Intelligence", 2022, 4500, "Methods, evaluation and limitations of explainable AI.", True, "XAI"),
]


async def main() -> None:
    async with AsyncSessionLocal() as db:
        if await db.scalar(select(User.id).limit(1)):
            print("Seed skipped: database already contains users")
            return

        users = [
            User(
                email="admin@openresearch.dev",
                username="admin",
                full_name="Admin Demo",
                password_hash=hash_password("Admin123!"),
                role=UserRole.ADMIN,
                is_verified=True,
            ),
            User(
                email="user@openresearch.dev",
                username="student",
                full_name="Student Demo",
                password_hash=hash_password("Student123!"),
                role=UserRole.USER,
                is_verified=True,
            ),
            User(
                email="premium@openresearch.dev",
                username="premium",
                full_name="Premium Demo",
                password_hash=hash_password("Premium123!"),
                role=UserRole.PREMIUM,
                is_verified=True,
            ),
        ]
        db.add_all(users)
        await db.flush()
        db.add_all(
            [
                Subscription(
                    user_id=user.id,
                    plan=Plan.PREMIUM if user.role == UserRole.PREMIUM else Plan.FREE,
                )
                for user in users
            ]
        )

        paper_texts = [f"{title} {abstract}" for title, _, _, abstract, _, _ in PAPERS]
        embeddings = get_embedding_service().encode(paper_texts)
        papers = [
            Paper(
                openalex_id=f"seed:{index}",
                title=title,
                publication_year=year,
                publication_date=date(year, 1, 1),
                cited_by_count=citations,
                abstract=abstract,
                is_open_access=open_access,
                source_name="Seed Research Corpus",
                language="en",
                type="article",
                metadata_json={"seed": True, "topic_code": topic_code},
                embedding=embedding,
            )
            for index, ((title, year, citations, abstract, open_access, topic_code), embedding) in enumerate(
                zip(PAPERS, embeddings, strict=True),
                1,
            )
        ]
        db.add_all(papers)
        await db.flush()

        citation_pairs = [
            (1, 0), (2, 0), (2, 1), (3, 1), (3, 2), (4, 9), (7, 8),
            (8, 7), (9, 0), (10, 0), (10, 1), (11, 5), (11, 6),
        ]
        db.add_all(
            [
                Citation(citing_paper_id=papers[source].id, cited_paper_id=papers[target].id)
                for source, target in citation_pairs
            ]
        )

        topics = {
            "NLP": Topic(name="Natural Language Processing"),
            "IR": Topic(name="Information Retrieval"),
            "GRAPH": Topic(name="Graph Learning"),
            "ML": Topic(name="Machine Learning"),
            "REC": Topic(name="Recommender Systems"),
            "XAI": Topic(name="Explainable AI"),
        }
        db.add_all(topics.values())
        authors = [
            Author(openalex_id="seed-author:1", name="A. Researcher"),
            Author(openalex_id="seed-author:2", name="B. Scientist"),
            Author(openalex_id="seed-author:3", name="C. Engineer"),
        ]
        institution = Institution(
            openalex_id="seed-inst:1",
            name="OpenResearch University",
            country_code="VN",
            institution_type="education",
        )
        db.add_all([*authors, institution])
        await db.flush()
        for index, paper in enumerate(papers):
            topic_code = str(paper.metadata_json["topic_code"])
            db.add(PaperTopic(paper_id=paper.id, topic_id=topics[topic_code].id, score=0.95))
            db.add(PaperAuthor(paper_id=paper.id, author_id=authors[index % len(authors)].id))
            db.add(PaperInstitution(paper_id=paper.id, institution_id=institution.id))

        student = users[1]
        premium = users[2]
        db.add_all(
            [
                LibraryItem(user_id=student.id, paper_id=papers[2].id, collection_name="RAG"),
                LibraryItem(user_id=student.id, paper_id=papers[3].id, collection_name="RAG"),
                LibraryItem(user_id=premium.id, paper_id=papers[0].id, collection_name="NLP"),
                LibraryItem(user_id=premium.id, paper_id=papers[2].id, collection_name="NLP"),
            ]
        )
        db.add_all(
            [
                UserPaperInteraction(user_id=student.id, paper_id=papers[2].id, interaction_type="save", interaction_value=1),
                UserPaperInteraction(user_id=student.id, paper_id=papers[3].id, interaction_type="like", interaction_value=1),
                UserPaperInteraction(user_id=premium.id, paper_id=papers[0].id, interaction_type="save", interaction_value=1),
                UserPaperInteraction(user_id=premium.id, paper_id=papers[2].id, interaction_type="like", interaction_value=1),
                UserPaperInteraction(user_id=premium.id, paper_id=papers[7].id, interaction_type="download", interaction_value=1),
            ]
        )
        await db.commit()
        print("Seed completed")
        print("admin@openresearch.dev / Admin123!")
        print("user@openresearch.dev / Student123!")
        print("premium@openresearch.dev / Premium123!")


if __name__ == "__main__":
    asyncio.run(main())

