import logging
from app import db
from app.models.anki_card import AnkiCard
from app.models.vocab_highlight import VocabHighlight
from app.services.ankiconnect_service import AnkiService

logger = logging.getLogger(__name__)

class VocabHighlightService:
    @staticmethod
    def process_highlights():
        highlights = VocabHighlight.query.all()
        for highlight in highlights:
            if not highlight.anki_card_id:
                note_id = AnkiService.add_anki_note(
                    deck_name="YourDeckName",
                    model_name="Basic",
                    front=highlight.word,
                    back=highlight.usage,
                    tags=["vocab"]
                )
                if note_id:
                    new_card = AnkiCard(note_id=note_id, front=highlight.word, back=highlight.usage)
                    db.session.add(new_card)
                    db.session.commit()
                    highlight.anki_card_id = new_card.id
                    db.session.commit()
                    logger.info(f"Created Anki card for highlight ID {highlight.id}")
                else:
                    logger.error("Failed to create Anki card")
            else:
                # Update logic for existing Anki card can be implemented here
                pass

    # Additional methods related to managing vocab highlights can be added here.
