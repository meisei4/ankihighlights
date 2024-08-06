def remove_value_order_from_dict(result: list[dict]) -> list[dict]:
    updated_result = result
    for i in range(len(result)):
        fields_keys = result[i]["fields"].keys()
        for field_key in fields_keys:
            updated_result[i]["fields"][field_key] = result[i]["fields"][field_key]["value"]
    return updated_result
