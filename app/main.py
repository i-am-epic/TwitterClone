from ast import Str
from multiprocessing import synchronize
from tkinter import E
from typing import List, Optional
from fastapi import FastAPI,Response,status,HTTPException, Depends, APIRouter
import psycopg2 
from psycopg2.extras import RealDictCursor
import time

from sqlalchemy import String
from .database import engine, get_db
from . import models, schemas, utils, oauth2
from .routers import auth
from sqlalchemy.orm import session
from passlib.context import CryptContext
from .config import settings
from fastapi.middleware.cors import CORSMiddleware
origins = [
    "http://localhost:3000",
    "http://localhost:8000"
]



app = FastAPI()

models.Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

while(True):

    try:
        connection = psycopg2.connect(host=settings.database_hostname,database = settings.database_name,user=settings.database_username,password = settings.database_password,cursor_factory=RealDictCursor)#The password is password of your db
        cursor = connection.cursor()
        print("Connection was succesfull")
        break
    except Exception as error:
        print("Connection Failed ERROR:",error)
        time.sleep(8)

pwd_contex = CryptContext(schemes=["bcrypt"],deprecated = "auto")

def hash(password:str):
    return pwd_contex.hash(password)
    
@app.get("/")
async def root():
    return {"GREETINGS": "HELLO ALL","DBMS":"MINI PROJECT","NAME":"PROJECT_TWEET","USING":"HTML+CSS+REACT+PYTHON+FASTAPI+POSTGRES","AS":"API BASED SOCIAL MEDIA PLATFORM","BY":"NIKHIL & PRATHEEK"}


router = APIRouter()


app.include_router(auth.router)


#gets all the post available which is posted latest
@app.get("/posts")
async def get_posts(limit:int = 12,skip:int=0,search:Optional[str]=""):
    cursor.execute("""SELECT posts.*,user_name,COUNT(votes.post_id) as votes 
    FROM 
    posts LEFT JOIN votes ON posts.postid = votes.post_id 
    LEFT JOIN users ON posts.owner_id = users.id
    WHERE 
    content LIKE %s OR title LIKE %s OR user_name LIKE %s OR cat_name LIKE %s
    group by posts.postid,users.user_name 
    ORDER BY created_at DESC LIMIT %s OFFSET %s""",(str("%"+search+"%"),str("%"+search+"%"),str("%"+search+"%"),str("%"+search+"%"),limit,skip,))
    posts = cursor.fetchall()
    return posts


'''@app.get("/psts",response_model=schemas.PostOut)
async def get_psts(db:session = Depends(get_db)):
    posts = db.query(models.Post).all()

    return{"all_posts":posts}
'''



#ccreating post which include the schema of posts which is defined above
@app.post("/posts",status_code=status.HTTP_201_CREATED)
async def create_posts(post:schemas.Post,current_user:int = Depends(oauth2.get_current_user)):
    try:
        cursor.execute("""INSERT INTO posts (title , content, published,owner_id,cat_name) VALUES(%s,%s,%s,%s,%s) RETURNING * """,(post.title,post.content,post.published,current_user.id,post.cat_name))
        new_post = cursor.fetchone()
        connection.commit()
        #print(current_user.email)
        return{"status":"created succesfully","post":new_post}
    except :
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,detail=f"ERROR: CHECK FOR VALID CATEGORY")



#gets the latest post by the id
@app.get("/posts/latest")
async def get_latest_post():
    cursor.execute("""SELECT posts.*,user_name,COUNT(votes.post_id) as votes 
    FROM 
    posts LEFT JOIN votes ON posts.postid = votes.post_id 
    LEFT JOIN users ON posts.owner_id = users.id
    WHERE postid =(SELECT max(postid) FROM posts)
    group by posts.postid,users.user_name 
    """)
    latest=cursor.fetchone()
    return latest



@app.get("/posts/user/{id}")
async def get_user_posts(id:int,current_user:int = Depends(oauth2.get_current_user),search:Optional[str]=""):
    if (True):
        cursor.execute("""SELECT posts.*,user_name,COUNT(votes.post_id) as votes 
        FROM 
        posts LEFT JOIN votes ON posts.postid = votes.post_id 
        LEFT JOIN users ON posts.owner_id = users.id
        WHERE owner_id =%s 
        group by posts.postid,users.user_name 
        ORDER BY created_at DESC """,(str(id),))
        user_posts=cursor.fetchall()
        return user_posts
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Not authorised to do this action")



@app.get("/posts/user")
async def get_user_posts(current_user:int = Depends(oauth2.get_current_user),search:Optional[str]=""):
    print(id)
    cursor.execute("""SELECT posts.*,user_name,COUNT(votes.post_id) as votes 
    FROM 
    posts LEFT JOIN votes ON posts.postid = votes.post_id 
    LEFT JOIN users ON posts.owner_id = users.id
    WHERE owner_id =%s 
    group by posts.postid,users.user_name 
    ORDER BY created_at DESC""",(str(current_user.id),))
    user_posts=cursor.fetchall()
    return user_posts




#get the post by postid
@app.get("/post/{id}")
async def get_posts(id:int,current_user:int = Depends(oauth2.get_current_user)):
    cursor.execute("""SELECT posts.*,user_name,COUNT(votes.post_id) as votes 
        FROM 
        posts LEFT JOIN votes ON posts.postid = votes.post_id 
        LEFT JOIN users ON posts.owner_id = users.id
        WHERE postid = %s 
        group by posts.postid,users.user_name""",(str(id),) )
    post = cursor.fetchone()
    if (post == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"ERROR post of id:{id} not found")
    connection.commit()
    return post


#deleting the post by postid
@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id:int,db:session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
    if(current_user.admin):
        cursor.execute("""DELETE FROM posts WHERE postid  = %s  RETURNING *""",(str(id),))
        deleted_post = cursor.fetchone()
        if deleted_post==None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"ERROR post of id:{id} not found")
        connection.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    post_query = db.query(models.Post).filter(models.Post.postid == id)
    post = post_query.first()
    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"ERROR post of id:{id} not found")

    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Not authorised to do this action")

    post_query.delete(synchronize_session = False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


#updating a post by PUT  method it requires to add all the values not just updating values
@app.put("/postid/{id}",response_model=schemas.Post)
async def update_post(id:int,updated_post:schemas.PostCreate,db:session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user)):
    if (current_user.admin):

        cursor.execute("""UPDATE posts SET title = %s, content= %s, cat_name =%s WHERE postid = %s RETURNING *""",(updated_post.title,updated_post.content,updated_post.cat_name,str(id)))
        updated_post = cursor.fetchone()
        if updated_post==None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} not available")
        
        connection.commit()
        return  {"updated post":updated_post}
    
    post_query = db.query(models.Post).filter(models.Post.postid == id)
    post = post_query.first()

    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"ERROR post of id:{id} not found")

    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Not authorised to do this action")
   
    post_query.update(updated_post.dict(),synchronize_session = False)
    db.commit()
    return post

@app.get("/posts/category/{name}")
async def get_user_posts(name:str,current_user:int = Depends(oauth2.get_current_user),search:Optional[str]=""):
    
    cursor.execute("""SELECT posts.*,user_name,COUNT(votes.post_id) as votes 
        FROM 
        posts LEFT JOIN votes ON posts.postid = votes.post_id 
        LEFT JOIN users ON posts.owner_id = users.id
        WHERE cat_name =%s 
        group by posts.postid,users.user_name
        ORDER BY created_at DESC """,(str(name),))
    cat_posts=cursor.fetchall()
    return cat_posts



@app.post("/users",status_code=status.HTTP_201_CREATED)
async def create_user(user:schemas.NewUser):
    hashed_passwd = utils.hash(user.password)
    user.password = hashed_passwd
    try:
        cursor.execute("""INSERT INTO users (user_name , email, password,admin,description) VALUES(%s,%s,%s,%s,%s) RETURNING * """,(user.username,user.email,user.password,user.admin,user.description))
        new_user = cursor.fetchone()
        connection.commit()
        return{"STATUS":"created succesfully","user":new_user}
    except:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"ERROR user with that email already exist, try login")

@app.get('/users/{id}')
async def get_user(id:int,current_user:int = Depends(oauth2.get_current_user),search:Optional[str]=""):
    cursor.execute("""SELECT * FROM users WHERE id = %s """,(str(id),) )
    user = cursor.fetchone()
    if (user == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"ERROR user of id:{id} not found")
    connection.commit()
    return{"user_details":user}

@app.get('/user/{name}')
async def get_user_name(name:str,current_user:int = Depends(oauth2.get_current_user),search:Optional[str]=""):
    cursor.execute("""SELECT * FROM users WHERE user_name = %s OR email= %s """,(str(name),str(name)))
    user = cursor.fetchone()
    if (user == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"ERROR user of id:{id} not found")
    connection.commit()
    return{"user_details":user}

@app.get("/users")
async def get_users(current_user:int = Depends(oauth2.get_current_user),search:Optional[str]=""):
    print(current_user.admin)
    if (current_user.admin):
        cursor.execute("""SELECT * FROM users
        WHERE 
        user_name LIKE %s OR email LIKE %s
        ORDER BY id""",(str("%"+search+"%"),str("%"+search+"%")))
        users = cursor.fetchall()
        return{"all_users":users}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"ERROR user is not admin")

        
    
@app.delete("/categories/{name}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_cat(name:str,db:session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):

    if(current_user.admin):
        cursor.execute("""DELETE FROM categories WHERE cat_name  = %s  RETURNING *""",(str(name),))
        deleted_cat = cursor.fetchone()
        if deleted_cat==None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"ERROR post of name:{name} not found")
        connection.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    cat_query = db.query(models.Categories).filter(models.Categories.cat_name == name)
    cat = cat_query.first()

    if cat==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"ERROR post of name:{name} not found")
    print(str(cat.cat_name)+" deleted")
    
    if cat.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Not authorised to do this action")

    cat_query.delete(synchronize_session = False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/categories/{name}",response_model=schemas.CatOut)
async def update_cat(name:str,updated_cat:schemas.NewCat,db:session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user),search:Optional[str]=""):
    if (current_user.admin):

        cursor.execute("""UPDATE categories SET cat_name = %s, description= %s WHERE cat_name = %s RETURNING *""",(updated_cat.cat_name,updated_cat.description,str(name)))
        updated_cat = cursor.fetchone()
        if updated_cat==None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"category with name {name} not available")
        
        connection.commit()
        return  {"updated category":updated_cat}
    
    post_query = db.query(models.Categories).filter(models.Categories.cat_name == name)
    post = post_query.first()

    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"ERROR category of name: {name} not found")

    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Not authorised to do this action")
   
    post_query.update(updated_cat.dict(),synchronize_session = False)
    db.commit()
    return post

@app.post("/categories",status_code=status.HTTP_201_CREATED)
async def create_categorie(cat:schemas.NewCat,current_user:int = Depends(oauth2.get_current_user)):
    try:
        cursor.execute("""INSERT INTO categories (cat_name,description,owner_id) VALUES(%s,%s,%s) RETURNING * """,(cat.cat_name,cat.description,current_user.id,))
        new_cat = cursor.fetchone()
        connection.commit()
        return{"STATUS":"created succesfully","user":new_cat}
    
    except:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"ERROR category already exist, try new name")

@app.get('/categories/{name}')
async def get_categorie(name:str,current_user:int = Depends(oauth2.get_current_user),search:Optional[str]=""):
    cursor.execute("""SELECT * FROM categories WHERE cat_name = %s """,(str(name),) )
    cat = cursor.fetchone()
    if (cat == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"ERROR user of name:{name} not found")
    connection.commit()
    return{"cat_details":cat}

@app.get("/categories")
async def get_categories():
    cursor.execute("""SELECT * FROM categories ORDER BY created_at DESC""")
    posts = cursor.fetchall()
    return{"all_posts":posts}

'''
@app.post('/retweet/{id}',status_code=status.HTTP_201_CREATED)
async def retweet(id:int,retweet:schemas.Retweet,current_user:int = Depends(oauth2.get_current_user),):
    cursor.execute("""INSERT INTO retweet (user_id , post_id) VALUES(%s,%s) RETURNING * """,(current_user.id,retweet.post_id))
    new_post = cursor.fetchone()
    connection.commit()
    return{"retweet":"retweeted succesfully","post":new_post}

import requests

def test_function(request: Request, path_parameter: path_param):

    request_example = {"test" : "in"}
    host = request.client.host
    data_source_id = path_parameter.id

    get_test_url= f"http://{host}/test/{id}/"
    get_inp_url = f"http://{host}/test/{id}/inp"

    test_get_response = requests.get(get_test_url)
    inp_post_response = requests.post(get_inp_url , json=request_example)
    if inp_post_response .status_code == 200:
        print(json.loads(test_get_response.content.decode('utf-8')))'''

@app.post("/vote",status_code=status.HTTP_201_CREATED)
async def vote(vote:schemas.Vote,db:session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.postid == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post does not exist")

    vote_query = db.query(models.Vote).filter(models.Vote.post_id ==vote.post_id,models.Vote.user_id==current_user.id)
    found_vote = vote_query.first()
    if (vote.dir == 1):
        if (found_vote):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"USER {current_user.id} ALREADY VOTED ON THIS POST {vote.post_id}")
        new_vote = models.Vote(post_id=vote.post_id,user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"status":"succesfully voted"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"vote not exist")

        vote_query.delete(synchronize_session=False)
        db.commit()

        return {"status":"successfully removed vote"}


@app.post("/retweet",status_code=status.HTTP_201_CREATED)
async def retweet(retweet:schemas.Retweet,db:session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.postid == retweet.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post does not exist")

    re_query = db.query(models.Retweet).filter(models.Retweet.post_id ==retweet.post_id,models.Retweet.user_id==current_user.id)
    found_re = re_query.first()
    get_new_post = await get_latest_post()
    new_post_id = get_new_post["postid"]
    print(new_post_id)
    if (retweet.dir == 1):
        if (found_re):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"USER {current_user.id} ALREADY RETWEETED THIS POST {retweet.post_id}")
        new_tweet = models.Retweet(post_id=retweet.post_id,user_id=current_user.id)
        db.add(new_tweet)
        db.commit()
        new_post = await get_posts(retweet.post_id) 
        title,content,cat_name = new_post["post_details"]["title"],new_post["post_details"]["content"],new_post["post_details"]["cat_name"]
        keys = ['title', 'content', 'cat_name']
        post_req = {x:dict(new_post)[x] for x in keys}
        post_req["published"]=True
        cursor.execute("""INSERT INTO posts (title , content, published,owner_id,cat_name) VALUES(%s,%s,%s,%s,%s) RETURNING * """,(post_req["title"],post_req["content"],post_req["published"],current_user.id,post_req["cat_name"]))
        #created_post =await create_posts(post_req)
        #print(dict(created_post["post"]))
        new_posts = cursor.fetchone()
        connection.commit()
        new_post_id=dict(new_posts)["postid"]

        #print(current_user.email)
        return{"status":"retweeted succesfully","post":new_post}

        #return {"status":"succesfully retweeted"}


    else:
        if not found_re:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"tweet not exist")
        print(new_post_id)
        print("del")

        if new_post_id!=0:
            cursor.execute("""DELETE FROM posts WHERE postid  = %s  RETURNING *""",(str(new_post_id),))
            deleted_post = cursor.fetchone()
            if deleted_post==None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"ERROR post of id:{new_post_id} not found")
            connection.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)

            '''deleted_post = await delete_post(new_post_id)
            print(str(delete_post)+"deleted")
            re_query.delete(synchronize_session=False)
            db.commit()
            return {"status":"successfully removed tweet"}'''
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post does not exist")

