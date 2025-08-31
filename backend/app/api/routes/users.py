from fastapi import APIRouter, status, HTTPException, Response
from pydantic import BaseModel
from typing import List
from app.core.db import user_collection
from app.models.user import NewUser, User
from app.schemas.user_schema import list_users, seralize_user_schema
from bson import ObjectId

router = APIRouter(prefix="/users")

class UserListData(BaseModel):
    users: List[User]
    skip: int
    limit: int
    total: int
    hasPrevious: bool
    hasNext: bool

class UserListResponse(BaseModel):
    status: int
    message: str
    data: UserListData


@router.get("/", response_model=UserListResponse)
async def get_users(skip: int = 0, limit: int = 10):
    users_cursor = user_collection.find().skip(skip).limit(limit)
    users_data = list_users(await users_cursor.to_list(length=limit))
    total = await user_collection.count_documents({})
    hasPrevious = skip > 0
    hasNext = (skip + limit) < total
    
    data = UserListData(
        users=users_data,
        skip=skip,
        limit=limit,
        total=total,
        hasPrevious=hasPrevious,
        hasNext=hasNext
    )
    
    return UserListResponse(
        status=status.HTTP_200_OK,
        message="Users retrieved successfully",
        data=data
    )
    

@router.post("/",  response_class=Response)
async def create_user(user: NewUser):
    try:
        result = await user_collection.insert_one({
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "gender": user.gender.value
        })
        
        if result.inserted_id:
            # Return the created user data
            return Response(status_code=status.HTTP_201_CREATED)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Error creating user"
        )


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return seralize_user_schema(user)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


@router.delete("/{user_id}", response_class=Response)
async def delete_user(user_id: str):
    result = await user_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user: User):
    result = await user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "gnder": user.gender.value
        }}
    )
    if result.modified_count == 1:
        updated_user = await user_collection.find_one({"_id": ObjectId(user_id)})
        if updated_user:
            return seralize_user_schema(updated_user)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found or no changes made"
    )
