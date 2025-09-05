

def seralize_user_schema(user) -> dict:
    return {
        "id": str(user["_id"]),
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "gender": user["gender"],
        "role_id": str(user["role_id"]) if "role_id" in user and user["role_id"] else None,
        "is_active": user["is_active"],
        "activated_at": str(user["activated_at"]) if "activated_at" in user else None,
        "created_at": str(user["created_at"]) if "created_at" in user else None
    }

def list_users(users) -> list:
    return [seralize_user_schema(user) for user in users]