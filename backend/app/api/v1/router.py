from fastapi import APIRouter

from app.api.v1 import admin, analytics, auth, chat, documents, graphs, library, papers, recommendations, search, subscriptions, users

api_router = APIRouter(prefix="/api/v1")
for router in [auth.router, users.router, search.router, papers.router, analytics.router, graphs.router, library.router, documents.router, chat.router, recommendations.router, subscriptions.router, admin.router]:
    api_router.include_router(router)
