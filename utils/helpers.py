import re

def hex_to_rgba(hex_color):
    """
    Convert a hex color code to RGBA.
    """
    hex_color = hex_color.lstrip('#')  # Remove the hash (#) if it's present
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    a = 1.0  # Set alpha to 1 (opaque)
    return (r, g, b, a)


def preprocess_text(text):
    """
    Preprocess text by converting it to lowercase and removing special characters.
    """
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation and special characters
    return text


def detect_language(text):
    """
    Detect the language of the given text.
    - English is identified by alphabets.
    - Urdu is identified by Urdu-specific characters.
    """
    if any(char in text for char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        return 'english'
    elif any(char in text for char in 'ا ب پ ت ٹ ث ج چ ح خ د ڈ ذ ر ڑ ز ژ س ش ص ض ط ظ ع غ ف ق ک گ ل م ن و ہ ھ ی ے'):
        return 'urdu'
    else:
        return 'unknown'
