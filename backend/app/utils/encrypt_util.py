import hashlib


def make_md5(data: str) -> str:
    """制作MD5"""
    hl_md5 = hashlib.md5()
    hl_md5.update(data.encode('utf-8'))
    return hl_md5.hexdigest()
