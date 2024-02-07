import logging

from app import db
from app.models.anki_card import AnkiCard
from app.models.vocab_highlight import VocabHighlight
from app.services.ankiconnect_service import AnkiService

logger = logging.getLogger(__name__)


class VocabHighlightService:
    @staticmethod
    def process_new_vocab_highlights():
        # Assuming we're fetching highlights that have not yet been processed
        highlights = VocabHighlight.query.filter_by(anki_card_id=None).all()

        for highlight in highlights:
            # Check if a corresponding Anki note already exists
            query = f'"deck:YourDeckName" "front:{highlight.word}"'
            existing_note_ids = AnkiService.find_notes(query)

            if existing_note_ids:
                note_id = existing_note_ids[0]  # Assuming the first note ID is the one we want to update
                # Optionally update note fields here using AnkiService.update_note_fields
            else:
                # Create a new Anki note if it doesn't exist
                note_id = AnkiService.add_anki_note(
                    deck_name="YourDeckName",
                    model_name="Basic",
                    front=highlight.word,
                    back=highlight.usage,
                    tags=["vocab"]
                )

            if note_id:
                # Create or update the AnkiCard model
                anki_card = AnkiCard.query.filter_by(note_id=note_id).first()
                if not anki_card:
                    anki_card = AnkiCard(note_id=note_id)
                    db.session.add(anki_card)
                highlight.anki_card = anki_card
                db.session.commit()
                logger.info(f"Processed Anki card for highlight ID {highlight.id} with note ID {note_id}")
            else:
                logger.error(f"Failed to process Anki card for highlight ID {highlight.id}")

    @staticmethod
    def update_anki_card(highlight_id, updated_usage):
        """Update an existing Anki card with new usage/examples."""
        highlight = VocabHighlight.query.get(highlight_id)
        if highlight and highlight.anki_card:
            note_id = highlight.anki_card.note_id
            fields = {"Back": updated_usage}  # Assuming 'Back' field is used for usage/examples
            AnkiService.update_note_fields(note_id, fields)
            logger.info(f"Updated Anki card for highlight ID {highlight.id} with note ID {note_id}")
        else:
            logger.error(f"Highlight ID {highlight_id} not found or does not have an associated Anki card.")

