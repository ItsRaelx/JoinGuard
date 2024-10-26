import hashlib
import os


async def hash_data_with_salt(input_data):

    if isinstance(input_data, dict) and 'data' in input_data:
        input_data = input_data['data']

    if not isinstance(input_data, (list, tuple)):
        input_data = [input_data]

    output_data = []

    for string in input_data:
        hash_object = hashlib.sha512()
        hash_object.update(str(string).encode('utf-8'))
        hashed_value = hash_object.hexdigest()
        output_data.append(hashed_value)
    return output_data