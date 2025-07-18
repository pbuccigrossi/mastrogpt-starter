import os, json, requests as req, time

MODEL = "llava:7b"

def collect(lines):
  out = ""
  for line in lines:
    #line = next(lines)
    chunk = json.loads(line.decode("UTF-8"))
    out +=  chunk.get("response", "")
  return out

class Vision:
  def __init__(self, args):
    host = args.get("OLLAMA_HOST", os.getenv("OLLAMA_HOST"))
    auth = args.get("OLLAMA_TOKEN", os.getenv("OLLAMA_TOKEN"))
    self.url = f"https://{auth}@{host}/api/generate"

  def decode(self, img):
    msg = {
      "model": MODEL,
      "prompt": "describe the image",
      "images": [img]
    }

    resp = req.post(self.url, json=msg, stream=True)
    if resp.status_code == 200:
      lines = resp.iter_lines()
      return collect(lines)
    else:
      return -1

  def nameIt(self, img):
    msg = {
      "model": MODEL,
      "prompt": "generate a single word to give a name to the image",
      "images": [img]
    }
    lines = req.post(self.url, json=msg, stream=True).iter_lines()
    out = collect(lines).replace(" ", "")
    print(out)
    return f"upload/{time.time()}/{out}"