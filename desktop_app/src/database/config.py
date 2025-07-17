from pydantic import BaseModel



class DataBasePaths(BaseModel):
    # paths
    faces: str = "src/database/faces"
    users: str = "src/database/users"
    check_users: str = "src/database/users"
