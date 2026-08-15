"""Quick test: verify Neon PostgreSQL connectivity and pgvector extension."""
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
        version = await conn.fetchval("SELECT version()")
        print(f"[OK] Connected: {version[:60]}")

        exts = await conn.fetch("SELECT extname FROM pg_extension")
        ext_names = [r["extname"] for r in exts]
        print(f"[OK] Extensions: {ext_names}")

        if "vector" not in ext_names:
            print("[INFO] pgvector not yet installed, creating...")
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            print("[OK] pgvector extension created")

        # Check for uuid-ossp
        if "uuid-ossp" not in ext_names:
            print("[INFO] uuid-ossp not yet installed, creating...")
            await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
            print("[OK] uuid-ossp extension created")

        # Check for pg_trgm
        if "pg_trgm" not in ext_names:
            print("[INFO] pg_trgm not yet installed, creating...")
            await conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
            print("[OK] pg_trgm extension created")

        # List tables
        tables = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )
        table_names = [r["tablename"] for r in tables]
        print(f"[OK] Tables ({len(table_names)}): {table_names}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
