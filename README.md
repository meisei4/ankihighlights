# ankikindle
experiment in developing along side gpt. 

original chat 抜粋 with gpt:

4shi死]

This will be an app that listens to a users kindle clippings(highlight) file and upon any update to that file parses the update and generates an anki card(note) from it and adds it to that users anki app. This will be used to allow for better studying of encountered words during reading in a foreign language.

explanation of the current code：
Python script that reads Kindle clippings from the user's Kindle account and then adds them as notes to the Anki app using the Anki Connect API.

Here's a brief summary of the steps involved in the script:

1. sends a GET request to the Kindle server to retrieve clippings from the user's account. It parses the JSON response to extract the relevant data.

2. loops over each clipping (highlight) and converts it into an Anki note format.

3. checks if the note already exists in Anki by searching for it using the Anki Connect API findNotes action. If it exists, it updates the note with more example sentences. Otherwise, it adds a new note to the specified deck and model (model is dumb, need ot figure out how to make it work for a specific card type i design later).

4. assigns tags to the note based on the number of times the same word appears in the user's clippings (this is to be able to mark the word if its seen too many times, then will be sent to a new deck of higher study priority).


JSON stuff:

potential JSON responses from the amazon Kindle clippings (highlights) file (completely made up):
```json
[
    {
        "asin": "B08KPXKVRV",
        "authors": "Haruki Murakami",
        "title": "1Q84 BOOK1",
        "lastUpdatedDate": "2022-04-15T05:26:11.000Z",
        "highlights": [
            {
                "text": "君は、この世で会った全ての女性の中で、その顔を覚えている女性は何人くらいいるだろうか。",
                "location": {
                    "page": 191
                },
                "timestamp": "2022-04-15T05:27:12.027Z",
                "note": "Highlight"
            },
            {
                "word": "自分",
                "text": "どんな仕事をしていようと、いつだって、こうやって机に向かって仕事をしている自分がいる。",
                "location": {
                    "page": 498
                },
                "timestamp": "2022-04-15T05:29:12.027Z",
                "note": "VocabWord"
            }
        ]
    }
]
```

example anki based JSON request (or response? note_id blah, card_id blah figure it the heck out) for the word "自分" and the sentences it was orignally highlight in.

```json
{
    "deckName": "words from kindle",
    "modelName": "aedict",
    "fields": {
        "Furigana": "自分[じぶん]",
        "Expression": "こうやって机に向かって仕事をしている自分がいる",
        "Sentence": [ "こうやって机に向かって仕事をしている自分がいる", "分の能力を信じて、夢に向かって努力しましょう"]
    },
    "tags": ['2']
}
```

Stupid : notes and cards (anki) and highlights and clippings (kindle) are pretty much the same thing... but the apis decided to make it complicated for some reaosn

