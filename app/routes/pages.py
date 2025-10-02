from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.database import db
from app.models import Post

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def read_root(request: Request):
    posts = db.get_all_posts()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

@router.get("/posts/create")
async def create_post_form(request: Request):
    return templates.TemplateResponse("create_post.html", {"request": request})

@router.post("/posts/create")
async def create_post(authorId: int = Form(...), title: str = Form(...), content: str = Form(...)):
    user = db.get_user(authorId)
    if not user:
        return RedirectResponse("/posts/create?error=user_not_found", status_code=302)
    
    post_id = db.get_next_post_id()
    post = Post(id=post_id, authorId=authorId, title=title, content=content)
    db.save_post(post)
    return RedirectResponse(f"/posts/{post_id}", status_code=303)

@router.get("/posts/{post_id}")
async def read_post(request: Request, post_id: int):
    post = db.get_post(post_id)
    if not post:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return templates.TemplateResponse("post.html", {"request": request, "post": post})

@router.get("/posts/{post_id}/edit")
async def edit_post_form(request: Request, post_id: int):
    post = db.get_post(post_id)
    if not post:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return templates.TemplateResponse("edit_post.html", {"request": request, "post": post})

@router.post("/posts/{post_id}/edit")
async def edit_post(post_id: int, title: str = Form(...), content: str = Form(...)):
    post = db.get_post(post_id)
    if not post:
        return RedirectResponse("/", status_code=302)
    
    db.update_post(post_id, title=title, content=content)
    return RedirectResponse(f"/posts/{post_id}", status_code=303)