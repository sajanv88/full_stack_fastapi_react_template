

def seralize_user_schema(user) -> dict:
    return {
        "id": str(user["_id"]),
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "gender": user["gender"],
    }

def list_users(users) -> list:
    return [seralize_user_schema(user) for user in users]