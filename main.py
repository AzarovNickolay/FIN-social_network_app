from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, ValidationError, Field
from pymongo import MongoClient
from pymongo.results import UpdateResult
from typing import List
from datetime import datetime
import os

app = FastAPI()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = MongoClient(MONGO_URI)

db = client["social_network"]
users_collection = db["users"]
posts_collection = db["posts"]

class User(BaseModel):
    created_on: datetime = Field(default_factory = datetime.now)
    username: str
    fullName: str
    active: bool
    email: str
    friends: List[str] = []
    friends_count: int = 0

class Post(BaseModel):
    username: str
    content: str
    date: datetime = Field(default_factory = datetime.now)
    likes: int = 0
    comment_count: int = 0

# Добавить пользователя
@app.post('/users')
def add_user(user: User):
    existing = users_collection.find_one({'username': user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь с таким username уже существует")
    
    # user_data = User(created_on=datetime.now(),
    #                  username=user.username,
    #                  fullName=user.fullName,
    #                  active=user.active,
    #                  email=user.email,
    #                  friends=[],
    #                  friends_count=0)
    
    users_collection.insert_one(user.model_dump())

    return {"message": "Пользователь успешно добавлен"}

# Добавить пост
@app.post('/posts')
def add_post(post: Post):
    existing = users_collection.find_one({'username': post.username})
    if not existing:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    
    # post_data = Post(date = datetime.now(),
    #                  username = post.username,
    #                  content = post.content,
    #                  likes = post.likes,
    #                  comment_count = post.comment_count)
    
    posts_collection.insert_one(post.model_dump())

    return {"message": "Запись успешно добавлена"}

# Найти всех пользователей
@app.get("/users", response_model=List[User])
def get_users():
    users = users_collection.find()
    return [User(**user) for user in users]

# Найти пользователея по имени пользователя 
@app.get("/users/{username}", response_model=List[User])
def get_users_by_username(username: str):
    users = users_collection.find({'username': username})
    return [User(**user) for user in users]

# Найти пользователей с более чем 100 друзьями
@app.get("/popusers", response_model=List[User])
def get_popular_users():
    users = users_collection.find({"friends_count": {"gt": 100}})
    return [User(**user) for user in users]

# Подсчитать количество пользователей в сети 
@app.get("/online_users_count")
def get_online_users_count():
    online_users_count = users_collection.count_documents({"active": True})
    return {"online_users_count": online_users_count}

# Найти все посты конкретного пользователя
@app.get("/posts/{username}", response_model=List[Post])
def get_posts_by_username(username: str):
    posts = posts_collection.find({'username': username})
    return [Post(**post) for post in posts]

# Найти посты с более чем 50 лайками
@app.get("/trending", response_model=List[Post])
def get_trending_posts():
    posts = posts_collection.find({"likes": {"$gt": 50}})
    return [Post(**post) for post in posts]

# Обновить email-адрес пользователя по имени пользователя
@app.put("/users/{username}/email")
def update_user_email(username: str, new_email: str):
    try:
        result: UpdateResult = users_collection.update_one(
            {"username": username},
            {"$set": {"email": new_email}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        return {"message": "Email успешно обновлен"}
    
    except ValidationError:
        raise HTTPException(status_code=400, detail="email-адрес не соответствует требуемому формату")

# Добавить нового друга к пользователю
@app.put("/users/{username}/add_friend")
def add_friend(username: str, friend_username: str):
    try:
        user = users_collection.find_one({"username": username})
        friend = users_collection.find_one({"username": friend_username})

        if not user or not friend:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        if friend_username in user.get("friends", []):
            raise HTTPException(status_code=400, detail="Пользователь уже в списке друзей")

        users_collection.update_one(
            {"username": username},
            {"$push": {"friends": friend_username}}
        )

        return {"message": "Друг успешно добавлен"}
    
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

# Удалить пользователя по ID
@app.delete("/users/{username}")
def delete_user(username: str):

    # Находим и удаляем пользователя из БД
    user = users_collection.find_one_and_delete({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    
    # Ищем и вычищаем удаляемого пользователя из списка друзей
    users_collection.update_many(
        {"friends": username},
        {"$pull": {"friends": username}}
    )

    return {"message": f"Пользователь {username} удален успешно"}

# Найти пользователей, зарегистрированных после определенной даты
@app.get("/users/find_by_date")
def find_by_date(date: datetime):
    try:
        users = users_collection.find({"registration_date": {"$gt": date}})
        users_list = [{"username": user["username"],
                       "email": user["email"],
                       "registration_date": user["registration_date"]} 
                    for user in users]
        return {"users": users_list}
    
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    
# Найти посты, содержащие конкретное слово (по заданию - "Встреча")
@app.get("/posts/{keyword}")
def search_posts_by_keyword(keyword: str):
    try:
        posts = posts_collection.find({"content": {"$regex": keyword, "$options": "i"}})
        posts_list = [{"content": post["content"],
                       "username": post["username"],
                       "date": post["date"],
                       "likes": post["likes"],
                       "comment_count": post["comment_count"]} 
                    for post in posts]
        
        return {"posts": posts_list}
    
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    
# Найти пользователей, у которых есть общие друзья с заданным пользователем
@app.get("/users/{username}/mutual_friends")
def fetch_mutual_friends(username: str, current_user: str):
    try:
        # Получаем друзей заданного пользователя
        user = users_collection.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=404, detail='Пользователь не найден')
        user_friends = set(user.get("friends", []))
        
        # Получаем друзей текущего пользователя
        current_user_data = users_collection.find_one({"username": current_user})
        if not current_user_data:
            raise HTTPException(status_code=404, detail='Текущий пользователь не найден')
        current_user_friends = set(current_user_data.get("friends", []))
        
        # Находим общих друзей
        mutual_friends = user_friends.intersection(current_user_friends)
        
        return {"mutual_friends": list(mutual_friends)}
    
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

# Найти посты с определенным количеством лайков и комментариев   
@app.get("/posts/by_likes_comments")
def find_post_by_likes_comments(likes: int = None, comment_count: int = None): 
    try:
        if not likes and not comment_count:
            raise HTTPException(status_code=400, detail="Не переданы аргументы")
        
        query = {}
        if likes is not None:
            query["likes"] = likes
        if comment_count is not None:
            query["comment_count"] = comment_count

        qualified_posts = posts_collection.find(query)

        res = [{"content": post["content"],
                 "username": post["username"],
                 "date": post["date"],
                 "likes": post["likes"],
                 "comment_count": post["comment_count"]} 
                 
                 for post in qualified_posts]

        if not res:
            return {"message": "Не найдено постов, соответствующих условиям поиска", "posts": []}
        
        return {"posts": res}


    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    
# Найти пользователей с определенным доменом электронной почты
@app.get("/users/by_email_domain", response_model=List[User])
def find_users_by_email_domain(domain: str):
    try:
        if not domain:
            raise HTTPException(status_code=400, detail="Домен не передан")
        
        users = users_collection.find({"email": {"$regex": f"@{domain}$"}})
        result = [User(**user) for user in users]
        
        if not result:
            return {"message": "Не найдено пользователей с указанным доменом электронной почты", "users": []}
        
        return result

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    
# Подсчитать количество постов каждого пользователя
@app.get("/users/total_posts")
def count_posts_by_user():
    try:
        agg = [
            {"$group": {"_id": "$username", "total_posts": {"$sum": 1}}}
        ]
        result = posts_collection.aggregate(agg)
        response = [{"username": item["_id"], 
                     "total_posts": item["total_posts"]} for item in result]
        
        if not response:
            return {"message": "Не найдено постов", "users": []}
        
        return {"users": response}
    
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
