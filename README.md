# Twitter_CLONE

Simple Twitter clone API  using Fastapi

This is a basic api which has major features of a twitter(social media app) using jwt token as authentication.

## Features

Basic CRUD operation on posts,users,votes,category,retweet.

1.CREATE<br />
2.READ<br />
3.UPDATE<br />
4.DELETE<br />


## Libraries imported/installed

Fastapi<br />
psycopg2  drivers //newer version is available <br />
pydantic<br />
uvicorn<br />
others are listed in  /required.txt<br />



## To Run the API server
run using uvicorn:
```bash
uvicorn app.main:app --reload
```
Default location/url http://127.0.0.1:8000/ [Localhost]

 
```bash
USE POSTMAN FOR API HANDELING.
```
### Some of the defined api calls are listed:
## Functions available
![alt text](https://github.com/i-am-epic/TwitterClone/blob/main/api%20functions.png)


