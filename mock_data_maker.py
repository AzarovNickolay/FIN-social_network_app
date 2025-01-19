from random import choice, randint
from main import User, Post
from datetime import datetime
from tqdm import tqdm

import lorem
import requests

names = ['Jack', 'Mike', 'Michael', 'Aiden', 'Derrek', 'Amanda', 'Dina', 'Barry', 'Leon', 'Brock', 'Darren', 'Thomas', 'Tom', 'Guy', 'Borja', 'Ito', 'Morris', 'Benjamin', 'Ben', 'Adam', 'Samuel', 'Sam', 'Terry', 'Mark', 'Kirk', 'Synthia', 'Ashley', 'Lia', 'Maria', 'Diana', 'Helga', 'Beatrice', 'Mary', 'Connie']
surnames = ['Downes', 'Marques', 'Johnson', 'Alba', 'Davies', 'Morris', 'Bradley', 'Angelo', 'Cox', 'Dawn', 'Cruz', 'Schmidt', 'Casey', 'Lesnar', 'Orton', 'Hamilton', 'Jefferson', 'Peterson', 'Thompson', 'Marques', 'Sparrow', 'Beau', 'Coman', 'Rashford', 'Rutherford', 'Buxton', 'Ruiz', 'Draper', 'Cole', 'Palmer', 'Terrnece']

def fill_friends(users: list[User]) -> None:
    for user in users:
        user1 = user.username
        to_befriend = [choice(list(item.username for item in users if item.username != user1 and item.username not in user.friends)) for _ in range(5)]
        user.friends.extend(to_befriend)
        user.friends_count += 5
        for username in to_befriend:
            new_friend = [item for item in users if item.username == username][0]
            new_friend.friends.append(user1)
            new_friend.friends_count += 1
            

def create_mock_users(names: list[str], surnames: list[str]) -> list[User]:
    user_list: list[User] = []
    for _ in range(100):

        # Генерируем рандомное имя для нового пользователя
        user_name = choice(names)
        user_surname = choice(surnames)
        
        # Генерируем уникальный username для пользователя на основании имени
        username = f'{user_name}{user_surname}'
        if list(item.username for item in user_list if username in item.username):
           username = f'{username}{len(list(item.username for item in user_list if username in item.username))}' 
        
        # Добавляем в список новый объект класса User, определяем для него обязательные параметры
        user_list.append(User(fullName = f'{user_name} {user_surname}',
                              username = username,
                              active = choice([True, False]),
                              email = f'{username}@example.com',
                              created_on = datetime(randint(2018,2025), randint(1,12), randint(1,28), randint(0,23), randint(0,59), randint(0,59))))
    
    # Осуществляем наполнение списка друзей для каждого юзера
    fill_friends(user_list)

    # Возвращем собранный список пользователей
    return user_list

def generate_mock_posts(user_list: list[User]) -> list[Post]:
    post_list: list[Post] = []
    
    # Генерим посты на каждого юзера
    for user in user_list:
        # Генерим рандомное количество постов на юзера (от 1 до 10)
        for _ in range(randint(1,10)):
            
            post_list.append(Post(username = user.username,
                                  content = lorem.sentence(),
                                  likes = randint(0, 50000),
                                  comment_count = randint(0, 10000),
                                  date = datetime(randint(2018,2025), randint(1,12), randint(1,28), randint(0,23), randint(0,59), randint(0,59))))
            
    # Возвращаем собранный список постов
    return post_list

def upload_to_db(DB_address, 
                 users: list[User] = None, 
                 posts: list[Post] = None) -> str:
    
    with requests.Session() as sess:
        headers = {'content-type': 'application/json'}
        if users:
            for user in tqdm(users, desc = "Adding users:"):
                try:
                    sess.post(url = f'{DB_address}/users',
                              headers = headers,
                              json = {"username": user.username,
                                      "fullName": user.fullName,
                                      "active": user.active,
                                      "email": user.email,
                                      "created_on": user.created_on.isoformat(),
                                      "friends": user.friends,
                                      "friends_count": user.friends_count})
                except:
                    pass

        if posts:
            for post in tqdm(posts, desc = 'Adding posts:'):
                try:
                    sess.post(url = f'{DB_address}/posts',
                              headers = headers,
                              json = {"username": post.username,
                                      "content": post.content,
                                      "likes": post.likes,
                                      "comment_count": post.comment_count,
                                      "date": post.date.isoformat()})
                except:
                    pass

users = create_mock_users(names, surnames)
posts = generate_mock_posts(users)

upload_to_db(DB_address = 'http://localhost:8000', 
             users = users,
             posts = posts)