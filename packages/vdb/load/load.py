import vdb
import base64
import pdfplumber
import io
import re
import requests as req
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

DIMENSION=800
REG_EXP_TOKENIZER = r"\b\w+\b|[^\w\s]"

USAGE = f"""Welcome to the Vector DB Loader.
Write text to insert in the DB.
Start with * to do a vector search in the DB.
Start with ! to remove text with a substring.
"""

FORM = [
  {
    "label": "Load pdf",
    "name": "pdf",
    "required": "true",
    "type": "file"
  },
]

def load(args):
  
  collection = args.get("COLLECTION", "default")
  out = f"{USAGE}Current collection is {collection}"
  inp = args.get('input', "")
  db = vdb.VectorDB(args)
  res = {}

  print('>>>>> load 1')
  
  if type(inp) is dict and "form" in inp:
    print('>>>>> load 2')
    pdfFile = inp.get("form", {}).get("pdf", "")
    print(f"uploaded size {len(pdfFile)}")

    # Read the file content into memory
    pdf_bytes = base64.b64decode(pdfFile)
    
    # Create a file-like object from the bytes
    pdf_stream = io.BytesIO(pdf_bytes)
    
    # Extract text using pdfplumber
    text_content = ""
    with pdfplumber.open(pdf_stream) as pdf:
      for page in pdf.pages:
          page_text = page.extract_text()
          if page_text:
              text_content += page_text + "\n"
    chunks = split_text_into_chunks(text_content)
    for chunk in chunks:
      db.insert(chunk)
  elif inp == "file":
     res['form'] = FORM
  elif inp.startswith("https://"):
    try:
      resHttps = req.get(inp)
      if resHttps.status_code == 200:
        soup = BeautifulSoup(resHttps.text, 'html.parser')
        for img_tag in soup.find_all('img'):
            img_tag.decompose()
        for script_tag in soup.find_all('script'):
            script_tag.decompose()
        for style_tag in soup.find_all('style'):
            style_tag.decompose()

        clean_text = soup.get_text(separator=' ', strip=True)

        # chunks = smart_split(clean_text)
        # chunks = tokenize(clean_text)
        chunks = split_text_into_chunks(clean_text)
        for chunk in chunks:
          # print(f"Inserting chunk {index} of {len(chunks)}")
          # print(len(chunk))
          # if(len(chunk) > 1000):
          #    print(chunk)
          db.insert(chunk)
      else:
        out ="URL not valid or not accessible"
    except RequestException as e:
      out ="URL not valid or not accessible " + str(e)
  elif inp == "clean":
    print('>>>>> clean')
    db.setup(True)
  elif inp.startswith("*"):
    print('>>>>> load 3')
    if len(inp) == 1:
      out ="please specify a search string"
    else:
      resSearch = db.vector_search(inp[1:])
      if len(resSearch) > 0:
        out = f"Found:\n"
        for i in resSearch:
          out += f"({i[0]:.2f}) {i[1]}\n"
      else:
        out = "Not found"
  elif inp.startswith("!"):
    print('>>>>> load 4')
    count = db.remove_by_substring(inp[1:])
    out = f"Deleted {count} records."
  elif inp != '':
    print('>>>>> load 5')
    resInsert = db.insert(inp)
    out = "Inserted " 
    out += " ".join([str(x) for x in resInsert.get("ids", [])])

  #return {'form': FORM, 'output': out}
  #return {'output': out}

  res['output'] = out

  return res

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