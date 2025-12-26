import base64
import json
import urllib.parse


def decode_embed(url):
    """Decode a base64 encoded string back to its original form."""
    data_str = url.split("data=")[-1]
    decoded_url = urllib.parse.unquote(data_str)
    decoded_bytes = base64.b64decode(decoded_url)
    decoded_json = json.loads(decoded_bytes.decode("utf-8"))
    return decoded_json
