from typing import Optional
from fastapi import status, Response, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from .. import models, schemas, oauth2
from ..schemas import PostBase


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=list[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 20,
    skip: int = 0,
    search: Optional[str] = "",
):

    results = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    """TypeError('cannot convert dictionary update sequence element #0 to a sequence')
try to add this line of code before returning results:
results = list ( map (lambda x : x._mapping, results) )
When querying the db with two arguments in the .query method, sqlalchemy returns a list of sqlalchemy.engine.row.Row objects. As far as I have acknowledged from the documentation:
"Changed in version 1.4:
Renamed RowProxy to .Row. .Row is no longer a "proxy" object in that it contains the final form of data within it, and now acts mostly like a named tuple. Mapping-like functionality is moved to the .Row._mapping attribute, but will remain available in SQLAlchemy 1.x ... "
So, in my understanding, we are not allowed to retrieve the jsonized data directly from the query anymore; the ._mapping method takes care of building the dict structure with "Post" and "votes" keys, and using map does this for each .Row element in the list; we then convert map to a list to be able to return it. 
Please feel free to correct me if I'm wrong, or if you have any better workaround."""
    posts = list(map(lambda x: x._mapping, results))

    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    new_post = models.Post(owner_id=current_user.id, **post.model_dump())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.post("/multiple", response_model=list[schemas.Post])
def create_multiple_posts(
    posts: list[schemas.PostCreate],
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    new_posts = []
    for post in posts:
        # print(str(post))
        # print(repr(post))
        new_post = models.Post(owner_id=current_user.id, **post.model_dump())
        db.add(new_post)
        new_posts.append(new_post)
    db.commit()  # Commit all new posts at once after adding them

    # Optionally refresh each new post to load any database-generated values
    for post in new_posts:
        db.refresh(post)

    return new_posts


@router.get("/{post_id}", response_model=schemas.PostOut)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == post_id)
        .first()
    )
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id : {post_id} does not exist.",
        )
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id : {post_id} Not Found",
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised to perform requested action",
        )

    # return {"message": f"Post with id : {post_id} deleted successfully"}
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{post_id}", response_model=schemas.Post)
def update_post(
    post_id: int,
    updated_post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    updated_post_query = db.query(models.Post).filter(models.Post.id == post_id)

    post = updated_post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id : {post_id} Not Found",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised to perform requested action",
        )
    updated_post_query.update(updated_post.model_dump())
    db.commit()
    return updated_post_query.first()
