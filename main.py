from fastapi import FastAPI
from routers import users, contacts, organizations
from db.models import engine, Base

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(users.router)
app.include_router(contacts.router)
app.include_router(organizations.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)