import sys
sys.path.append("packages/vdb/load")
import re
import requests as req
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

DIMENSION=800
REG_EXP_TOKENIZER = r"\b\w+\b|[^\w\s]"
HTTP_URL = 'https://en.wikipedia.org/wiki/Lorem_ipsum'

def test_tokenizer():
    out = ""
    resHttps = req.get(HTTP_URL)
    if resHttps.status_code == 200:
        soup = BeautifulSoup(resHttps.text, 'html.parser')
        for img_tag in soup.find_all('img'):
            img_tag.decompose()
        for script_tag in soup.find_all('script'):
            script_tag.decompose()
        for style_tag in soup.find_all('style'):
            style_tag.decompose()

        clean_text = soup.get_text(separator=' ', strip=True)
        chunks = split_text_into_chunks(clean_text)

        out = 'OK'
        for chunk in chunks:
        #   print(f"Inserting chunk {index} of {len(chunks)}")
          print(len(chunk))
          if(len(chunk) > 1025):
            print(chunk)
            out = 'KO'
    else:
        out ="URL not valid or not accessible"

    assert out == 'OK'


def split_text_into_chunks(text, max_chunk_size=DIMENSION):
    """
    Split a text into chunks with maximum size, using spaces and punctuation as separators.
    
    Args:
        text (str): The input text to be tokenized
        max_chunk_size (int): Maximum size of each chunk
    
    Returns:
        list: List of text chunks, each with length <= max_chunk_size
    """
    if not text or max_chunk_size <= 0:
        return []
    
    # Split text into tokens using spaces and punctuation as separators
    # This regex matches words followed by optional spaces and punctuation
    tokens = re.findall(r'[^\s\W]+[\s\W]*|[^\s\w]+[\s]*', text)
    
    # If regex doesn't capture everything, fall back to simpler approach
    if not tokens or ''.join(tokens) != text:
        # Alternative: split on whitespace and punctuation, keeping separators
        tokens = re.split(r'(\s+|[^\w\s])', text)
        tokens = [token for token in tokens if token]  # Remove empty strings
    
    chunks = []
    current_chunk = ""
    
    for token in tokens:
        # If adding this token would exceed max_chunk_size
        if len(current_chunk) + len(token) > max_chunk_size:
            # If current_chunk is not empty, add it to chunks
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            # If single token is larger than max_chunk_size, split it
            if len(token) > max_chunk_size:
                # Split the oversized token into smaller pieces
                for i in range(0, len(token), max_chunk_size):
                    chunk_piece = token[i:i + max_chunk_size]
                    chunks.append(chunk_piece)
            else:
                current_chunk = token
        else:
            current_chunk += token
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks