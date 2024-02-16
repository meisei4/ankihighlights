import logging
from app.services.anki_service import AnkiService
from app import db
from app.models.models import Lookup

logger = logging.getLogger(__name__)

class VocabHighlightService:

    @staticmethod
    def process_new_vocab_highlights(deck_name="DefaultDeck", model_name="Basic"):
        highlights = Lookup.query.filter(Lookup.anki_card_id.is_(None)).all()
        for highlight in highlights:
            VocabHighlightService.process_highlight(highlight, deck_name, model_name)

    @staticmethod
    def process_highlight(highlight, deck_name, model_name):
        query = f"deck:{deck_name} front:{highlight.word.word}"  # Adjust based on your model's attributes
        existing_note_ids = AnkiService.find_notes(query)

        if not existing_note_ids:
            note_id = AnkiService.add_anki_note(
                deck_name=deck_name,
                model_name=model_name,
                front=highlight.word.word,  # Use word attribute from Word model
                back=highlight.usage,  # Use usage attribute from Lookup model
                tags=["vocab"]
            )
        else:
            note_id = existing_note_ids[0]  # Assuming updating isn't required if the note already exists

        if note_id:
            highlight.anki_card_id = note_id  # Update your model accordingly
            db.session.commit()
            logger.info(f"Processed highlight for word '{highlight.word.word}' with Anki note ID {note_id}")
        else:
            logger.error(f"Failed to process highlight for word '{highlight.word.word}'")

