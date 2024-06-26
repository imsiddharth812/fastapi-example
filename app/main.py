from fastapi import FastAPI
from .database import engine
from .routers import post, user, auth, vote

from fastapi.middleware.cors import CORSMiddleware

# We do not require below sqlalchemy engine to create tables in database as we have alembic now to do the same.
#  models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
async def root():
    return {"message": "Hello! Successfully deployed from CI-CD pipeline to ubuntu!!!"}
