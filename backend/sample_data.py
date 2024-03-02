from pymongo import MongoClient
from bson import ObjectId
from utils import convert

# Initialize sample data in MongoDB at startup (if not already exists)

def insert_article(db, path) -> ObjectId:
    article = db.resources.find_one({"path": path})
    article_id = None
    if article is None:
        article_base64_content=convert("./" + path)

        db.resources.insert_one({
            "name": path.split('/')[-1].split('.')[0],
            "type": "pdf",
            "content": article_base64_content,
            "path": path
        })
        print(f"Article {path} added to MongoDB.")
        article = db.resources.find_one({"path": path})
    else:
        print(f"Resource {path} already exist in MongoDB.")

    article_id = article["_id"]
    return article_id


# Initialize sample user Alice in MongoDB at startup (if not already exists)
    
def insert_user_alice(db, article_ids):
    alice = db.users.find_one({"username": "alice"})

    if alice is None:
        permissions = [{"resource_id": article_id, "actions": ["read", "write"]} for article_id in article_ids]
        db.users.insert_one({
            "username": "alice",
            "password": "password123",  # Note: In a real application, use secure password hashing
            "permissions": permissions,
            # {"resource_id": ObjectId("article_b"), "actions": ["read"]},
        })
        print("User Alice added to MongoDB.")
    else: 
        print("User Alice already exists in MongoDB.")

def insert_user_bob(db, article_ids):
    alice = db.users.find_one({"username": "bob"})

    if alice is None:
        permissions = [{"resource_id": article_id, "actions": ["read"]} for article_id in article_ids]
        db.users.insert_one({
            "username": "bob",
            "password": "password123",  # Note: In a real application, use secure password hashing
            "permissions": permissions,
            # {"resource_id": ObjectId("article_b"), "actions": ["read"]},
        })
        print("User Bob added to MongoDB.")
    else: 
        print("User Bob already exists in MongoDB.")

def insert_sample_data(db):
    article_a_id = insert_article(db, "/article_a.pdf")
    article_b_id = insert_article(db, "/article_b.pdf")
    article_c_id = insert_article(db, "/article_c.pdf")
    # article_g_id = insert_article(db, "/article_g.pdf")
    article_e_id = insert_article(db, "/article_e.pdf")
    article_z_id = insert_article(db, "/article_z.pdf")
    insert_user_alice(db, [article_a_id, article_b_id, article_c_id])
    insert_user_bob(db, [article_e_id, article_z_id])