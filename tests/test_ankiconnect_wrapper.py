import ankiconnect_wrapper


def test_remove_value_order_from_dict():
    input_result = [
        {
            "cardId": 1593143468571,
            "fields": {
                "Expression": {
                    "value": "再現性",
                    "order": 0
                },
                "Meaning": {
                    "value": "reproducibility, repeatability, duplicability",
                    "order": 1
                },
                "Furigana": {
                    "value": "再現性[さいげんせい]",
                    "order": 2
                },
                "Sentence": {
                    "value": "",
                    "order": 3
                },
                "Pronunciation": {
                    "value": "",
                    "order": 4
                }
            },
            "fieldOrder": 0,
            "question": ""
        }
    ]

    removed_value_order_dict = ankiconnect_wrapper.remove_value_order_from_dict(input_result)
    expected_result = [
        {
            "cardId": 1593143468571,
            "fields": {
                "Expression": "再現性",
                "Meaning": "reproducibility, repeatability, duplicability",
                "Furigana": "再現性[さいげんせい]",
                "Sentence": "",
                "Pronunciation": ""
            },
            "fieldOrder": 0,
            "question": ""
        }
    ]
    assert removed_value_order_dict == expected_result

