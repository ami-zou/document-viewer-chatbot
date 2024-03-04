Project overview: a resource management platform allowing users to upload documents, share them with their colleagues, assisted by an AI chat bot

**Tech stack**
1. Front-end: React
2. Back-end: Python FastAPI
3. NLP model: Haystack 
4. DB: MongoDB


**Running the application locally**

1. Run MongoDB locally or using Atlas cloud version: https://www.mongodb.com/docs/manual/installation/
2. Start a Python environment in terminal
3. Create a `.env` file and put mongoDB URl (e.g. if running locally, put `MONGO_URI = "mongodb://localhost:27017"`)
4. Install Python dependencies `pip install -r requirements.txt`
5. Run the FastAPI Application:
    - In the `backend` directory, run the FastAPI application: `uvicorn main:app --reload` This command will start the FastAPI application, and you should see output indicating that the server is running. All the API documentations are in `localhost:8000/docs`, and you should be able to send requests via `curl`
6. Run the front-end web page:
    1. In the `frontend` directory, run `$npm start` , and go to `localhost:3000` which should displays the login feature
    2. Sample users: `alice` and `bob`, both with password `password123`
    

**Technical features**
1. User login and logout
2. Data persistence using MongoDB
3. Web application built using React and FastAPI
4. Different user roles and permissions for the documents 
5. File viewer based on user permission (only displaying `read` access files): list of files + PDF viewer
6. Access control: in the PDF viewer, display additional `edit` button for `write` access files
8. AI chat bot for summary 
    1. Process PDF files 
    2. Chat bot
9. TODO: Enhanced UI with navigation bar and home page
10. TODO: Deployment to production
11. TODO: CRUD for resources 
12. TODO: CRUD for user creation + management
13. TODO: Hierachy display of file structure

**Tech debt**
1. encode password
2. enable HTTPS
3. Docker containerize everything
4. DB objects 
5. PrivateRoute to dashboard
6. Use web-socket for chatbot
7. Hit enter for “send”
8. use a different AI model library 


API documentation: http://127.0.0.1:8000/docs


Data models:
users:
```
{
    _id: ObjectId('65e2c9997126dd95fe82b932'),
    username: 'alice',
    password: 'password123',
    permissions: [
      {
        resource_id: ObjectId('65e2c66c73aa358dd216b0cd'),
        actions: [ 'read', 'write' ]
      },
      {
        resource_id: ObjectId('65e2c66c73aa358dd216b0ce'),
        actions: [ 'read', 'write' ]
      },
      {
        resource_id: ObjectId('65e2c66c73aa358dd216b0cf'),
        actions: [ 'read', 'write' ]
      }
    ]
  },
```

resources:
```
  {
    _id: ObjectId('65e2c9997126dd95fe82b931'),
    name: 'article_z',
    type: 'pdf',
    content: 'bson PDF binary file with base64 encoding',
    path: '/article_z.pdf'
  }
```
```
