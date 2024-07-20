from app.models.word import Word

class WordDTO:
    @staticmethod
    def to_dict(word: Word) -> dict:
        return {
            'id': word.id,
            'word': word.word
        }

    @staticmethod
    def from_dict(data: dict) -> Word:
        return Word(
            id=data.get('id'),
            word=data.get('word')
        )
