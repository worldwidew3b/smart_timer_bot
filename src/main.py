from fastapi import FastAPI
from .api.endpoints import tasks, tags, timer, statistics
from .core.config import settings


def create_app():
    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        debug=settings.debug
    )
    
    # Include routers
    app.include_router(tasks.router)
    app.include_router(tags.router)
    app.include_router(timer.router)
    app.include_router(statistics.router)
    
    @app.get("/")
    async def root():
        return {"message": "Smart Timer Bot API", "version": settings.app_version}
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)