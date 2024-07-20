from app.models.book_info import BookInfo

class BookInfoDTO:
    @staticmethod
    def to_dict(book_info: BookInfo) -> dict:
        return {
            'id': book_info.id,
            'title': book_info.title,
            'authors': book_info.authors
        }

    @staticmethod
    def from_dict(data: dict) -> BookInfo:
        return BookInfo(
            id=data.get('id'),
            title=data.get('title'),
            authors=data.get('authors')
        )
