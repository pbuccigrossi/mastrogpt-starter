import os
import openai

MODEL = "phi4:14b"

ROLE = "system:You are an helpful assistant."

import json, socket, traceback
def stream(args, lines):
  if not args.get("STREAM_HOST") or not args.get("STREAM_PORT"):
    print("No streaming host or port provided, returning full response.")
    out = ''
    for line in lines:
        out += line.choices[0].delta.content
    return out
  sock = args.get("STREAM_HOST") ; port = int(args.get("STREAM_PORT"))
  out = ""
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((sock, port))
    try:
      for m in lines: 
        msg = {"output": m.choices[0].delta.content}
        s.sendall(json.dumps(msg).encode("utf-8"))
        out += str(m.choices[0].delta.content) #; print(m.choices[0].delta.content, end='')
    except Exception as e:
      traceback.print_exc(e)
      out = str(e)
  return out

class Chat:
    def __init__(self, args):
        
        host = args.get("OLLAMA_HOST", os.getenv("OLLAMA_HOST"))
        api_key = args.get("AUTH", os.getenv("AUTH"))
        base_url = f"https://{api_key}@{host}/v1"
        
        self.client = openai.OpenAI(
            base_url = base_url,
            api_key = api_key,
        )
        
        self.messages = []
        self.add(ROLE)
        self.args = args
        
    def add(self, msg):
        [role, content] = msg.split(":", maxsplit=1)
        self.messages.append({
                "role": role,
                "content": content,
        })
        return msg
    
    def complete(self):
        res = self.client.chat.completions.create(
            model=MODEL,
            messages=self.messages,
            stream = True
        )

        # out = "error"
        # if len(res.choices) >0:
        #     out = res.choices[0].message.content
        #     self.add(f"assistant:{out}")
        # return out
        try:
            out = stream(self.args, res)
        except:
            out =  "error"
        return out