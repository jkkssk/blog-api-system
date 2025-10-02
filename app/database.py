import json
import os
from datetime import datetime
from typing import Dict, List

class Database:
    def __init__(self, storage_file: str = "data.json"):
        self.storage_file = storage_file
        self.users: Dict[int, object] = {}
        self.posts: Dict[int, object] = {}
        self._next_user_id = 1
        self._next_post_id = 1
        self.load_from_file()

    def get_next_user_id(self) -> int:
        user_id = self._next_user_id
        self._next_user_id += 1
        return user_id

    def get_next_post_id(self) -> int:
        post_id = self._next_post_id
        self._next_post_id += 1
        return post_id

    def save_user(self, user) -> object:
        self.users[user.id] = user
        self.save_to_file()
        return user

    def get_user(self, user_id: int):
        return self.users.get(user_id)

    def get_all_users(self) -> List[object]:
        return list(self.users.values())

    def update_user(self, user_id: int, **kwargs):
        user = self.users.get(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)
            user.updatedAt = datetime.now()
            self.save_to_file()
        return user

    def delete_user(self, user_id: int) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            post_ids_to_delete = [post_id for post_id, post in self.posts.items() if post.authorId == user_id]
            for post_id in post_ids_to_delete:
                del self.posts[post_id]
            self.save_to_file()
            return True
        return False

    def save_post(self, post) -> object:
        self.posts[post.id] = post
        self.save_to_file()
        return post

    def get_post(self, post_id: int):
        post = self.posts.get(post_id)
        if post:
            post.views += 1
        return post

    def get_all_posts(self) -> List[object]:
        return list(self.posts.values())

    def update_post(self, post_id: int, **kwargs):
        post = self.posts.get(post_id)
        if post:
            for key, value in kwargs.items():
                if hasattr(post, key) and value is not None:
                    setattr(post, key, value)
            post.updatedAt = datetime.now()
            self.save_to_file()
        return post

    def delete_post(self, post_id: int) -> bool:
        if post_id in self.posts:
            del self.posts[post_id]
            self.save_to_file()
            return True
        return False

    def like_post(self, post_id: int, user_id: int) -> bool:
        post = self.posts.get(post_id)
        if post and user_id not in post.likes:
            post.likes.append(user_id)
            self.save_to_file()
            return True
        return False

    def unlike_post(self, post_id: int, user_id: int) -> bool:
        post = self.posts.get(post_id)
        if post and user_id in post.likes:
            post.likes.remove(user_id)
            self.save_to_file()
            return True
        return False

    def save_to_file(self):
        data = {
            'users': {},
            'posts': {},
            'next_user_id': self._next_user_id,
            'next_post_id': self._next_post_id
        }
        
        for user_id, user in self.users.items():
            data['users'][user_id] = {
                'id': user.id,
                'email': user.email,
                'login': user.login,
                'password': user.password,
                'createdAt': user.createdAt.isoformat(),
                'updatedAt': user.updatedAt.isoformat(),
                'following': user.following,
                'followers': user.followers
            }
        
        for post_id, post in self.posts.items():
            data['posts'][post_id] = {
                'id': post.id,
                'authorId': post.authorId,
                'title': post.title,
                'content': post.content,
                'createdAt': post.createdAt.isoformat(),
                'updatedAt': post.updatedAt.isoformat(),
                'likes': post.likes,
                'views': post.views
            }
        
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)

    def load_from_file(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                
                self._next_user_id = data.get('next_user_id', 1)
                self._next_post_id = data.get('next_post_id', 1)
                
                from app.models import User, Post
                
                for user_id, user_data in data.get('users', {}).items():
                    user = User(
                        id=user_data['id'],
                        email=user_data['email'],
                        login=user_data['login'],
                        password=user_data['password']
                    )
                    user.createdAt = datetime.fromisoformat(user_data['createdAt'])
                    user.updatedAt = datetime.fromisoformat(user_data['updatedAt'])
                    user.following = user_data.get('following', [])
                    user.followers = user_data.get('followers', [])
                    self.users[user.id] = user
                
                for post_id, post_data in data.get('posts', {}).items():
                    post = Post(
                        id=post_data['id'],
                        authorId=post_data['authorId'],
                        title=post_data['title'],
                        content=post_data['content']
                    )
                    post.createdAt = datetime.fromisoformat(post_data['createdAt'])
                    post.updatedAt = datetime.fromisoformat(post_data['updatedAt'])
                    post.likes = post_data.get('likes', [])
                    post.views = post_data.get('views', 0)
                    self.posts[post.id] = post
                    
            except Exception as e:
                print(f"Error loading data: {e}")

db = Database()