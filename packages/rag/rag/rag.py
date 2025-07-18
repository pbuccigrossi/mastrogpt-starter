import bucket
import os, re, requests as req
import json, socket, traceback, time, uuid
import vdb
from vdb import RAG_IMAGES_COLLECTION

MODELS = {
  "P": "phi4:14b",
  "L": "llama3.1:8b",
  "M": "mistral:latest"
}

USAGE = f"""
Start with `@[LPM][<size>][<collection>]` to select the model then add `<size>` sentences from the `<collection>` to the context.
Models: L=llama P=phi4 M=mistral.
You can shorten collection names, it will use the first one starting with the name.
Your query is then passed to the LLM with the sentences for an answer.

To find images by description switch to the {RAG_IMAGES_COLLECTION} collection.
"""

# Pattern: @<model><size><collection> <optional content>
PATTERN = re.compile(r'^@([LPDM]?)(\d*)(\w*)(\s*.*)$')

def parse_query(content):
    res = {
        "model": MODELS["L"],
        "size": 30,
        "collection": "default",
        "content": content
    }

    match = PATTERN.match(content.strip())
    if not match:
        return res
    
    model_key, size_str, collection, content = match.groups()
    
    if model_key in MODELS:
      res["model"] = MODELS[model_key]
    
    try: 
      size = int(size_str)
      res["size"] = size
    except: pass

    if collection != "":
      res["collection"]  = collection.strip()

    res["content"] = content.strip()
    return res

def streamlines(args, lines):
  sock = args.get("STREAM_HOST")
  port = int(args.get("STREAM_PORT") or "0")
  out = ""
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    if sock:
      s.connect((sock, port))
    try:
      for line in lines:
        time.sleep(0.1)
        msg = {"output": line }
        out += line
        if sock:
          s.sendall(json.dumps(msg).encode("utf-8"))
    except Exception as e:
      traceback.print_exc(e)
      out = str(e)
    if sock:
      s.close()
  return out

def stream(args, lines):
  sock = args.get("STREAM_HOST")
  port = int(args.get("STREAM_PORT") or "0")
  out = ""
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    if sock:
      s.connect((sock, port))
    try:
      for line in lines:
        dec = json.loads(line.decode("utf-8")).get("response")
        msg = {"output": dec }
        out += dec
        if sock:
          s.sendall(json.dumps(msg).encode("utf-8"))
    except Exception as e:
      traceback.print_exc(e)
      out = str(e)
    if sock:
      s.close()
  return out

def llm(args, model, prompt):
  host = args.get("OLLAMA_HOST", os.getenv("OLLAMA_HOST"))
  auth = args.get("AUTH", os.getenv("AUTH"))
  url = f"https://{auth}@{host}/api/generate"

  msg = {
    "model": model,
    "prompt": prompt,
    "stream": True
  }

  lines = req.post(url, json=msg, stream=True).iter_lines()
  return stream(args, lines)

def rag(args):
  inp = str(args.get('input', ""))
  ret = {"output": USAGE}
  if inp != "":
    opt = parse_query(inp)
    if opt['content'] == '':
      db = vdb.VectorDB(args, opt["collection"], shorten=True)
      lines = [f"model={opt['model']}\n", f"size={opt['size']}\n",f"collection={db.collection}\n",f"({",".join(db.collections)})"]
      ret = {"output": streamlines(args, lines)}
    else:
      db = vdb.VectorDB(args, opt["collection"], shorten=True)
      res = db.vector_search(opt['content'], limit=opt['size'])
      
      if opt["collection"] == RAG_IMAGES_COLLECTION:
        llmRet = llmRagImages(res, opt, args)
        #print(llmRet)
        #print('isValid?', is_valid_uuid4(llmRet))

        if(is_valid_uuid4(llmRet)):
          #get image from S3 and sent to FE for visualization
          url = getImageUrl(args, llmRet)
          ret = {"output": "Got it!", "html": f"<img src='{url}'>"}
        else:
          ret = {"output": "Sorry, cannot find any image."}
      else:
        ret = {"output": llmRagText(res, opt, args)}

  return ret

def llmRagText(res, opt, args):
  prompt = ""
  if len(res) > 0:
    prompt += "Consider the following text:\n"

    for (w, txt) in res:
      prompt += f"{txt}\n"
    prompt += "Answer to the following prompt:\n"
  prompt += f"{opt['content']}"

  #print(prompt)
  return llm(args, opt['model'], prompt)

def llmRagImages(res, opt, args):
  prompt = ""
  if len(res) > 0:
    prompt += "Consider the following text:\n"
    for (w, txt, s3Key) in res:
      prompt += f"{s3Key} is the code for this image description:{txt}\n"
    prompt += f"Reply with the code for this image description: {opt['content']}.\n"
  prompt += "Your response must only contain the code, no other words."

  #print(prompt)
  return llm(args, opt['model'], prompt)

def is_valid_uuid4(uuid_string: str) -> bool:
  try:
    val = uuid.UUID(uuid_string, version=4)
    return str(val) == uuid_string
  except ValueError:
    return False
  
def getImageUrl(args, key):
  buc = bucket.Bucket(args)
  return buc.exturl(key, 3600)