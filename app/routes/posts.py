from fastapi import APIRouter, HTTPException, status
from app.database import db
from app.schemas import PostCreate, PostResponse, PostUpdate
from app.models import Post

router = APIRouter(prefix="/api/posts", tags=["posts"])

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post_data: PostCreate, authorId: int):
    user = db.get_user(authorId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    post_id = db.get_next_post_id()
    post = Post(
        id=post_id,
        authorId=authorId,
        title=post_data.title,
        content=post_data.content
    )
    
    db.save_post(post)
    return post

@router.get("/", response_model=list[PostResponse])
async def get_all_posts():
    return db.get_all_posts()

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int):
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_data: PostUpdate):
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    updated_post = db.update_post(post_id, **post_data.model_dump(exclude_unset=True))
    return updated_post

@router.delete("/{post_id}")
async def delete_post(post_id: int):
    if not db.delete_post(post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}

@router.post("/{post_id}/like/{user_id}")
async def like_post(post_id: int, user_id: int):
    if not db.get_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    if db.like_post(post_id, user_id):
        return {"message": "Post liked successfully"}
    raise HTTPException(status_code=400, detail="Unable to like post")

@router.post("/{post_id}/unlike/{user_id}")
async def unlike_post(post_id: int, user_id: int):
    if db.unlike_post(post_id, user_id):
        return {"message": "Post unliked successfully"}
    raise HTTPException(status_code=400, detail="Unable to unlike post")