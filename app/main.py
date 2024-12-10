from fastapi import FastAPI
from app.routers import librarian, user

app = FastAPI()

# Include routes
app.include_router(librarian.router, prefix="/librarian", tags=["Librarian"])
app.include_router(user.router, prefix="/user", tags=["User"])
