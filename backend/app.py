from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from jose import JWTError, jwt
from typing import List, Optional
from bson import ObjectId

app = FastAPI()

# Configure CORS
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
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

# Security Configuration
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# User Model
class User(BaseModel):
    username: str
    password: str
    roles: List[str] = ["read"]


# Token Model
class Token(BaseModel):
    access_token: str
    token_type: str


# Resource Model
class Resource(BaseModel):
    title: str

# Dependency to get the current user from the token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await users_collection.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user


# Dependency to get the current user's roles
async def get_current_user_roles(current_user: User = Depends(get_current_user)):
    return current_user["roles"]

# Token endpoint for user authentication
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: User):
    user = await users_collection.find_one({"username": form_data.username})
    if user and form_data.password == user["password"]:
        return {
            "access_token": jwt.encode({"sub": form_data.username}, SECRET_KEY, algorithm=ALGORITHM),
            "token_type": "bearer",
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

# MongoDB Collection for Resources
resources_collection = db.resources

# CRUD Endpoints for Resources
@app.get("/resources", response_model=List[Resource])
async def get_resources(current_user_roles: List[str] = Depends(get_current_user_roles)):
    if "read" in current_user_roles:
        resources = await resources_collection.find().to_list(None)
        return resources
    raise HTTPException(status_code=403, detail="Unauthorized access")


@app.post("/resources", response_model=JSONResponse)
async def create_resource(resource: Resource, current_user_roles: List[str] = Depends(get_current_user_roles)):
    if "write" in current_user_roles:
        # Assume the resource is a PDF document
        resource_data = {"title": resource.title, "type": "pdf"}
        await resources_collection.insert_one(resource_data)
        return JSONResponse(content={"message": "Resource added successfully"}, status_code=201)
    raise HTTPException(status_code=403, detail="Unauthorized access")

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
