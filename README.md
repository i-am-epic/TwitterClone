# Twitter_CLONE

Simple Twitter clone API  using Fastapi

This is a basic api which has major features of a twitter(social media app) using jwt token as authentication.

## Features

Basic CRUD operation on posts,users,votes,category,retweet.

1.CREATE
2.READ
3.UPDATE
4.DELETE

### Some of the defined api calls are listed:
```Root_url: http://127.0.0.1:8000/ = {{URL}}```

```login: {{URL}}login, body:form_type:key username:... ,password:....```

```signup: {{URL}}users, body:{ "username":"admin1","email":"admin1@gmail.com","password":"password","admin":"True","description":"i am admin"}```

```get_all post:{{URL}}posts?skip=0&limit=10&search=input.```

.
.
.
.


## Libraries imported/installed

Fastapi
psycopg2  drivers //newer version is available 
pydantic
uvicorn
others are listed in  /required.txt



## To Run the API server
run using uvicorn:
```bash
uvicorn app.main:app --reload
```
Default location/url http://127.0.0.1:8000/ [Localhost]

 
```bash
USE POSTMAN FOR API HANDELING.
```


