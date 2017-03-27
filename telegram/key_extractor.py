import json

# The keys have to be in JSON format in a file called "keys"
def getKey(keyName):
    with open("keys") as f:
        try:
            keys = json.loads(f.read())
            if keyName in keys.keys():
                return keys[keyName]
        except json.decoder.JSONDecodeError:
            pass
    return ""
