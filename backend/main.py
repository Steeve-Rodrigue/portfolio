from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dto.userDto import UserDTO
from typing import List

app = FastAPI()

# 🔐 CORS (important pour Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod → mettre ton domaine
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 Mock database
users_db = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"},
]

# 🧠 Endpoint
@app.get("/users", response_model=List[UserDTO])
def get_users():
    return users_db