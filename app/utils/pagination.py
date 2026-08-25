from math import ceil
from sqlalchemy.orm import Query


def paginate(query: Query, page: int = 1, size: int = 10) -> dict:
    total_items = query.count()
    total_pages = ceil(total_items / size) if size > 0 else 0

    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()

    return {
        "items": items,
        "total": total_items,
        "page": page,
        "size": size,
        "total_pages": total_pages
    }
