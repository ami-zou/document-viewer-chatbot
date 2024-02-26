from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List
# from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from bson import ObjectId
import uvicorn
from pdf_conversion import convert

app = FastAPI()

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "acl_project"
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Secret key to sign the JWT token
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize sample data in MongoDB at startup (if not already exists)
article_a = db.resources.find_one({"path": "/article_a"})
article_a_id = None
if article_a is None:
    article_a_base64_content=convert("./article_a.pdf")

    db.resources.insert_one({
        "name": "article_a",
        "type": "pdf",
        "content": article_a_base64_content,
        "path": "/article_a"
    })
    print("Article A added to MongoDB.")
    article_a = db.resources.find_one({"path": "/article_a"})
else:
    print("Resource article already exist in MongoDB.")

article_a_id = article_a["_id"]


# Initialize sample user Alice in MongoDB at startup (if not already exists)
alice = db.users.find_one({"username": "alice"})

if alice is None:
    db.users.insert_one({
        "username": "alice",
        "password": "password123",  # Note: In a real application, use secure password hashing
        "permissions": [
            {"resource_id": article_a_id, "actions": ["read", "write"]}
            # {"resource_id": ObjectId("article_b"), "actions": ["read"]},
        ],
    })
    print("User Alice added to MongoDB.")
else: 
    print("User Alice already exist in MongoDB.")

# Function to create JWT token
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta

    # Print the to_encode dictionary
    print("to_encode:", to_encode)

    # Extract permissions and concatenate resource_id:action for each permission
    scopes = []
    for permission in to_encode.get("scopes", []):
        resource_id = permission.get("resource_id", "")
        actions = permission.get("actions", [])
        for action in actions:
            scope = f"{resource_id}:{action}"
            scopes.append(scope)

    to_encode.update({"exp": expire, "scopes": scopes})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# OAuth2PasswordBearer is a helper class to get the token from the request headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Function to get user information from the token
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return payload

# Route to create a token for login
@app.post("/login")
async def login_for_access_token(username: str, password: str):
    # user = next((user for user in USERS if user["username"] == username), None)
        # Check if the user exists in MongoDB
    user = db.users.find_one({"username": username})
    if user is None or password != user["password"]:
        print("user is ", user)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create a token with user information
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "scopes": user["permissions"]},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Route to simulate user logout (token invalidation)
@app.post("/logout")
async def logout():
    # In a real application, you might want to maintain a list of revoked tokens
    # and check if the token being used for logout is in that list.
    return {"message": "Logout successful"}

# Route to get user profile by ID
@app.get("/profiles/{id}", response_model=dict)
async def read_user_profile(id: str, current_user: dict = Depends(get_current_user)):
    user = next((user for user in USERS if user["id"] == id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)