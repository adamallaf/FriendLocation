import json

# The keys have to be in JSON format in a file called "keys"
def get_key(key_name):
    with open("keys") as f:
        try:
            keys = json.loads(f.read())
            if key_name in keys.keys():
                return keys[key_name]
        except json.decoder.JSONDecodeError:
            pass
    return ""
