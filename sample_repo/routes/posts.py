from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.post import Post
from models.user import User

router = APIRouter()

@router.get("/")
async def list_posts(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    posts = db.query(Post).offset(skip).limit(limit).all()
    return [post.to_dict() for post in posts]

@router.get("/{post_id}")
async def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post.to_dict()

@router.post("/")
async def create_post(title: str, content: str, author_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == author_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Author not found")

    new_post = Post(title=title, content=content, author_id=author_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post.to_dict()

@router.put("/{post_id}")
async def update_post(post_id: int, title: str = None, content: str = None, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if title:
        post.title = title
    if content:
        post.content = content

    db.commit()
    db.refresh(post)
    return post.to_dict()

@router.delete("/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}

@router.get("/{post_id}/author")
async def get_post_author(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post.author.to_dict()
