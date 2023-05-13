def sanitize_url(url: str) -> str:
    return url.replace("http", "hxxp").replace(".", "[.]")
