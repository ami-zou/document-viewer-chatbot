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
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import base64

app = FastAPI()

# Allow all origins in development. Adjust this in production.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "acl_project"
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

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

# Secret key to sign the JWT token
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
    print("Logging in username ", username)
    user = db.users.find_one({"username": username})
    if user is None or password != user["password"]:
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

# Function to validate JWT token (replace with proper validation logic)
def validate_token(token: str):
    print("validate token ", token)
    try:
        # Verify the token using the secret key
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return False
    except jwt.DecodeError:
        print("Invalid token: decode error")
        return False
    except jwt.InvalidTokenError:
        print("Invalid token")
        return False
    except JWTError:
        print("jwt error")
        return False

# Dependency to extract the token from the Authorization header
def extract_token(authorization: str = Depends(oauth2_scheme)):
    print("extracting token from authorization", authorization)
    if not authorization: # or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    # token = authorization.split("Bearer ")[1]
    return authorization

# Route to get user profile by ID
@app.get("/dashboard", response_model=dict)
async def get_user_dashboard(token: str = Depends(extract_token)):
    print("/dashboard received token ", token)
    # Validate token
    if not validate_token(token):
        raise HTTPException(status_code=401, detail="Invalid token or token has expired")
    
    # Decode token
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

    # Extract values from the decoded token
    username = decoded_token.get("sub")
    scopes = decoded_token.get("scopes", [])
    print(f"Username: {username}")
    print(f"Scopes: {scopes}")
        
    # Fetch user data from database
    user = db.users.find_one({"username": username})
    # if user:
    #     print("found user! ", user, " with user name ", user["username"])
    #     content={"username": user["username"], "user": str(user)}
    #     return content
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    print("user is ", user)
    # Fetch resources and permissions from database
    files = []
    for permission in user["permissions"]:
        file = {}

        resource_id = permission["resource_id"]
        actions = permission["actions"]

        resource = db.resources.find_one({"_id": resource_id})
        resource_name = resource["name"]
        resource_path = resource["path"]
        resource_type = resource["type"]
        resource_content = resource["content"]

        # # Convert base64 encoded PDF data to binary
        # pdf_binary_data = base64.b64decode(resource_content)

        file["file_name"] = resource_name
        file["file_path"] = resource_path
        file["file_content"] = resource_content
        file["file_type"] = resource_type
        file["file_permissions"] = actions

        files.append(file)

    return {"files": files}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)