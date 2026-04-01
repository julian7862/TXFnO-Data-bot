from urllib.parse import urljoin


def resolve_link(base_url: str, href: str) -> str:
    if not href:
        raise ValueError("href cannot be empty")
    return urljoin(base_url, href)
