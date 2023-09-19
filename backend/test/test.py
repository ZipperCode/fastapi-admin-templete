from app.schemas.system import SystemUserCreateIn

if __name__ == '__main__':
    body = {
        "ids": [
            0
        ],
        "roleIds": [
            0
        ],
        "deptIds": [
            0
        ],
        "postIds": [
            0
        ],
        "username": "string",
        "nickname": "string",
        "password": "string",
        "avatar": "string",
        "sort": 0,
        "isDisable": 0
    }
    create = SystemUserCreateIn(**body)
    print()
