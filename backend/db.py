from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['your-database-name']
users_collection = db['users']
resources_collection = db['resources']

# Sample Queries:

# 1. Find User by Username:
user = users_collection.find_one({"username": "alice"})

# 2. Find Users with a Specific Role:
users_with_role = users_collection.find({"roles.role_name": "Company_A_Employee"})

# 3. Find Users with Specific Permission on a Resource:
users_with_permission = users_collection.find({
    "permissions.resource_id": ObjectId("folder_A_id"),
    "permissions.actions": "read"
})

# 4. Add a New Role to a User:
users_collection.update_one(
    {"username": "alice"},
    {
        "$push": {
            "roles": {
                "role_name": "Manager",
                "permissions": [
                    {"resource_id": ObjectId("folder_A_id"), "actions": ["read"]}
                ]
            }
        }
    }
)

# 5. Remove a Role from a User:
users_collection.update_one(
    {"username": "alice"},
    {"$pull": {"roles": {"role_name": "Company_A_Employee"}}}
)

# 6. Update Permissions for a User on a Specific Resource:
users_collection.update_one(
    {"username": "alice", "roles.permissions.resource_id": ObjectId("folder_A_id")},
    {"$set": {"roles.$.permissions.$.actions": ["read", "write", "share"]}}
)

# 7. Querying All Documents in a Folder and Its Subfolders:
documents_in_folder = resources_collection.find({"path": {"$regex": "^/folder_A"}})

# 8. Querying Subfolders of a Folder:
subfolders_of_folder = resources_collection.find({"parent": ObjectId("folder_A_id"), "type": "folder"})

# 9. Querying Parent Folder of a Resource:
parent_folder = resources_collection.find_one({"_id": ObjectId("subfolder_X_id")})["parent"]

# 10. Moving a Folder to a Different Parent:
old_parent_id = ObjectId("folder_A_id")
new_parent_id = ObjectId("folder_B_id")
folder_name = "subfolder_X"

# Update the parent reference for the folder
resources_collection.update_one(
    {"_id": ObjectId("subfolder_X_id")},
    {"$set": {"parent": new_parent_id}}
)

# Update the path of the folder and its descendants
resources_collection.update_many(
    {"parent": old_parent_id, "name": folder_name},
    {"$set": {"path": {"$concat": ["/folder_B/", folder_name, {"$substr": ["$path", {"$strLenCP": len(old_parent_id.toHexString()) + len(folder_name) + 2}] }]}}}
)

# 11. Renaming a Folder:
folder_id = ObjectId("subfolder_X_id")
new_folder_name = "new_subfolder_X"

# Update the name of the folder
resources_collection.update_one(
    {"_id": folder_id},
    {"$set": {"name": new_folder_name}}
)

# Update the path of the folder and its descendants
resources_collection.update_many(
    {"path": {"$regex": "^/folder_A/subfolder_X"}},
    {"$set": {"path": {"$concat": ["/folder_A/", new_folder_name, {"$substr": ["$path", {"$strLenCP": len("/folder_A/subfolder_X") + len(new_folder_name) + 2}] }]}}}
)
