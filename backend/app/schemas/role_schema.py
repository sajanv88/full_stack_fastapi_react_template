def serialize_role_schema(role) -> dict:
    """Serialize a role document from MongoDB to a dictionary."""
    return {
        "id": str(role["_id"]),
        "name": role["name"],
        "description": role["description"],
        "permissions": role["permissions"],
        "created_at": str(role["created_at"]) if "created_at" in role else None
    }

def list_roles(roles) -> list:
    """Serialize a list of role documents."""
    return [serialize_role_schema(role) for role in roles]