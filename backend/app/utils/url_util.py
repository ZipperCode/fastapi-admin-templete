def to_relative_url(url: str | None, upload_prefix='/upload') -> str:
    """
    转相对路径
    转前: https://127.0.0.1/uploads/11.png
    转后: /uploads/11.png
    :param url:
    :param upload_prefix:
    :return:
    """
    if not url or not url.startswith('http'):
        return url
    return url[url.index(upload_prefix):]
