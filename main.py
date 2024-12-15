from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from utils.auth import SECRET_KEY
from routers import users, contacts, organizations, products
from db.models import engine, Base

app = FastAPI()

# Add SessionMiddleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="session_cookie",
    max_age=1800  # 30 minutes in seconds
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(users.router)
app.include_router(contacts.router)
app.include_router(organizations.router)
app.include_router(products.router)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)