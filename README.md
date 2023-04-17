# ankikindle
experiment in developing along side gpt. 

original chat 抜粋 with gpt:


Sure, I can provide more specific advice on how to initiate developing this program.
Here are some steps you could follow to get started:
1. Familiarize yourself with the Amazon Kindle API: The first step is to familiarize yourself with the Amazon Kindle API. The Amazon Kindle API is a RESTful API that allows developers to access various features of the Kindle device, including the clippings file. You can use the API to download the clippings file periodically and monitor it for updates.
2. Read and write files using Python: Once you are familiar with the Kindle API, you can start writing Python code to read and write files. You can use Python's built-in open() function to read and write files, and the os module to manipulate files and directories.
3. Parse the clippings file: Once you have downloaded the clippings file, you can use Python's built-in string manipulation functions to parse the file and extract the highlighted text. You can then use this text to create Anki cards.
4. Use AnkiConnect API to create Anki cards: You can use the AnkiConnect API to create Anki cards from your Python code. AnkiConnect is an API that allows developers to interact with Anki using JSON-RPC requests. You can use the API to create a new note with the highlighted text and any other relevant information.
5. Set up a periodic task: To monitor the clippings file for updates, you can set up a periodic task using Python's built-in schedule module or a third-party library like schedule. The periodic task can download the clippings file at regular intervals and check it for updates.
Overall, you can use Python's built-in modules and third-party libraries to implement the functionality you need for this program. Once you have a working prototype, you can start thinking about how to make it more scalable and secure.

explanation of the current code
Python script that reads Kindle clippings from the user's Kindle account and then adds them as notes to the Anki app using the Anki Connect API.

Here's a brief summary of the steps involved in the script:

1. sends a GET request to the Kindle server to retrieve clippings from the user's account. It parses the JSON response to extract the relevant data.

2. loops over each clipping (highlight) and converts it into an Anki note format.

3. checks if the note already exists in Anki by searching for it using the Anki Connect API findNotes action. If it exists, it updates the note with more example sentences. Otherwise, it adds a new note to the specified deck and model (model is dumb, need ot figure out how to make it work for a specific card type i design later).

4. assigns tags to the note based on the number of times the same word appears in the user's clippings (this is to be able to mark the word if its seen too many times, then will be sent to a new deck of higher study priority).


JSON stuff:

potential JSON responses from the Kindle clippings (highlights) file (completely made up):
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
                "word": "自分”
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

example JSON request (or response?) for the word "自分" and the sentences it has been found in.

```json
{
    "deckName": "words from kindle",
    "modelName": "aedict",
    "fields": {
        "Furigana": "自分[じぶん]",
        "Expression": "こうやって机に向かって仕事をしている自分がいる"
        "Sentence": [ "こうやって机に向かって仕事をしている自分がいる", "分の能力を信じて、夢に向かって努力しましょう"]
    }
    "tags": [2]
}
```

Stupid : notes and cards (anki) and highlights and clippings (kindle) are pretty much the same thing... but the apis decided to make it complicated for some reaosn

