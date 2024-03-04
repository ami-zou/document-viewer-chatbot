from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List
# from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from bson import ObjectId
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sample_data import insert_sample_data
from utils import extract_text_from_base64_pdf
from haystack.utils import print_answers
from haystack import Document
from haystack.document_stores import InMemoryDocumentStore
import os
from haystack.pipelines.standard_pipelines import TextIndexingPipeline
from haystack.nodes import BM25Retriever
from haystack.nodes import FARMReader
from haystack.pipelines import ExtractiveQAPipeline
from haystack.utils import print_answers
from pprint import pprint
import os
from dotenv.main import load_dotenv


load_dotenv()

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
# MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "acl_project"
client = MongoClient(os.getenv('MONGO_URI'))
db = client[DATABASE_NAME]


# Initialize sample data in MongoDB at startup (if not already exists)
# Alice with read and write access to 3 climate related articles
# Bob with read only access to 2 LLM research papers
insert_sample_data(db)

# AI pre-process data
document_store = InMemoryDocumentStore(use_bm25=True)

# Index documents
resources = db.resources.find()

indexing_pipeline = TextIndexingPipeline(document_store)
# indexing_pipeline.run_batch(file_paths=files_to_index)

# documents = [
#     Document({
#         "text": str(extract_text_from_base64_pdf(str(resource["content"]))),
#         "meta": {
#             "name": resource["name"],
#             "id": str(resource["_id"])
#         }
#     }) for resource in resources
# ]

documents = []
for resource in resources:
    content = resource["content"]
    text = extract_text_from_base64_pdf(content)
    # print(text)

    # doc = Document(
    #     "content": text
    #     "meta": {
    #         "name": resource["name"],
    #         "id": str(resource["_id"])
    #     }
    # ) 

    document = Document(
      content=text,
      meta={"name": resource["name"],
            "id": str(resource["_id"])}
  	)
    documents.append(document)

# clean_wiki_text

document_store.write_documents(documents)
print(f"Write {len(documents)} documents to haystack in-memory db")
# write_documents_to_db(documents, db, index="documents")

# Initialize retriever
retriever = BM25Retriever(document_store=document_store)

# Initialize Finder
# reader = FARMReader(model_name_or_path="bert-base-uncased-reader", use_gpu=False)
# finder = Finder(reader, db)
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)

# retriever = InMemoryBM25Retriever(db)

pipe = ExtractiveQAPipeline(reader, retriever)

# Secret key to sign the JWT token
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Function to create JWT token
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta

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
    print("Logging in username ", username)
    # Check if the user exists in MongoDB
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


def print_json_structure(data, indent=2):
    if isinstance(data, dict):
        for key, value in data.items():
            print(" " * indent + str(key))
            print_json_structure(value, indent + 2)
    elif isinstance(data, list):
        for item in data:
            print_json_structure(item, indent)
    else:
        print(" " * indent + str(data))

@app.post("/chatbot")
def chatbot(data: dict):
    query = data["query"]
    username = data["username"]
    print(f"user {username} query received {query}")
    user = db.users.find_one({"username": username})
    resource_ids = []
    if user is not None:
        for permission in user["permissions"]:
            resource_id = permission["resource_id"]
            actions = permission["actions"]
            if "read" in actions:
                resource_ids.append(resource_id)
    print("user is allowed to access resources: ", resource_ids)

    # Retrieve relevant passages and filter based on user permissions
    # results = finder.get_answers(
    #     question=query,
    #     top_k_retriever=10,
    #     top_k_reader=5,
    #     filters={"meta": {"id": {"$in": resource_ids}}},
    # )

    prediction = pipe.run(
        query=query, 
        params={
            "Retriever": {"top_k": 10}, 
            "Reader": {"top_k": 5}
        }
    )

    # print("printing prediction: ")
    # pprint(prediction)

    print("printing answers: ")
    print_answers(prediction, details="minimum")

    # print("prediction structure")
    # print_json_structure(prediction)

    # Assuming `predictions` is the list of predictions from Haystack
    sorted_answers = sorted(prediction['answers'], key=lambda x: x.score, reverse=True)
    best_answer = sorted_answers[0].answer
    print(f"best answer with score {sorted_answers[0].score} is {best_answer}")

    return {"response": best_answer}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)