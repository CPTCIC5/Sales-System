from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from utils.auth import SECRET_KEY,router as utils_router
from routers import users, contacts, organizations, products
from ai.app import router
from wp import webhook
from db.models import engine, Base

app = FastAPI()

# Add SessionMiddleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="session_cookie",
    max_age=1800000000000  # 30 minutes in seconds
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
app.include_router(router)
app.include_router(webhook.router)
app.include_router(utils_router)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)