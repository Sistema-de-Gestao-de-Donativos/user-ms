from fastapi import FastAPI
from .db import models, engine
from .routes.user_routes import router as user_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
