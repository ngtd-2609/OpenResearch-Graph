"""Check existing data in Neon database."""
import asyncio
import asyncpg


async def main():
    dsn = (
        "postgresql://neondb_owner:npg_rvh83OAqkLyp"
        "@ep-flat-rain-azk2olvk-pooler.c-3.ap-southeast-1.aws.neon.tech"
        "/neondb?sslmode=require"
    )
    conn = await asyncpg.connect(dsn)
    try:
        # Count records in key tables
        tables = [
            "users", "papers", "authors", "institutions", "topics",
            "citations", "user_paper_interactions", "library_items",
            "uploaded_documents", "document_chunks", "chat_sessions",
            "chat_messages", "search_history", "recommendation_logs",
            "subscriptions", "refresh_tokens",
        ]
        print("=== Data Overview ===")
        for table in tables:
            try:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                if count > 0:
                    print(f"  {table}: {count} records")
                else:
                    print(f"  {table}: (empty)")
            except Exception as e:
                print(f"  {table}: ERROR - {e}")

        # Check subscription plans
        plans = await conn.fetch("SELECT id, name, price_cents FROM subscriptions")
        if plans:
            print(f"\n=== Subscription Plans ===")
            for p in plans:
                print(f"  {p['name']}: ${p['price_cents']/100:.2f}")

        # Sample papers
        papers = await conn.fetch(
            "SELECT id, title, publication_date FROM papers LIMIT 5"
        )
        if papers:
            print(f"\n=== Sample Papers ===")
            for p in papers:
                print(f"  [{p['id']}] {p['title'][:80]} ({p['publication_date']})")
        else:
            print("\n[INFO] No papers in database yet")

        # Check if embeddings exist
        has_embeddings = await conn.fetchval(
            "SELECT COUNT(*) FROM papers WHERE embedding IS NOT NULL"
        )
        print(f"\n=== Embeddings ===")
        print(f"  Papers with embeddings: {has_embeddings}")

        # Check alembic version
        version = await conn.fetchval("SELECT version_num FROM alembic_version")
        print(f"\n=== Alembic Version: {version} ===")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
