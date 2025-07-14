import re, os, requests as req
#MODEL = "llama3.1:8b"
MODEL = "phi4:14b"

SETTINGS_MESSAGE = "Choose your puzzle settings"
FORM = [
  {
    "name": "queen",
    "label": "With a queen",
    "type": "checkbox",
    "required": "false"
  },
  {
    "name": "rook",
    "label": "With a rook",
    "type": "checkbox",
    "required": "false"
  },
  {
    "name": "knight",
    "label": "With a knight",
    "type": "checkbox",
    "required": "false"
  },
  {
    "name": "bishop",
    "label": "With a bishop",
    "type": "checkbox",
    "required": "false"
  }
]

def chat(args, inp):
  host = args.get("OLLAMA_HOST", os.getenv("OLLAMA_HOST"))
  auth = args.get("AUTH", os.getenv("AUTH"))
  url = f"https://{auth}@{host}/api/generate"
  msg = { "model": MODEL, "prompt": inp, "stream": False}
  res = req.post(url, json=msg).json()
  out = res.get("response", "error")
  return  out
 
def extract_fen(out):
  pattern = r"([rnbqkpRNBQKP1-8]+\/){7}[rnbqkpRNBQKP1-8]+"
  fen = None
  m = re.search(pattern, out, re.MULTILINE)
  if m:
    fen = m.group(0)
  return fen

def puzzle(args):
  out = "To see a random chess puzzle, type 'puzzle'<br>To display a fen position, type 'fen <fen string>'<br>To choose the puzzle settings type 'settings'"
  inp = args.get("input", "")
  res = {}
  if inp == "puzzle":
    inp = "generate a chess puzzle in FEN format"
    out = chat(args, inp)
    fen = extract_fen(out)
    if fen:
       print(fen)
       res['chess'] = fen
    else:
      out = "Bad FEN position."
  elif inp == "settings":
    out = SETTINGS_MESSAGE
    res['form'] = FORM
  elif type(inp) is dict and "form" in inp:
      data = inp["form"]
      for field in data.keys():
        print(f"""{field} = {data[field]}""")

      queenSetting = ''
      rookSetting = ''
      knightSetting = ''
      bishopSetting = ''
      if data['queen']:
        queenSetting = 'with a queen.'
      if data['rook']:
        rookSetting = 'with a rook.'
      if data['knight']:
        knightSetting = 'with a knight.'
      if data['bishop']:
        bishopSetting = 'with a bishop.'
      inp = f"""Generate a valid fen position {queenSetting} {rookSetting} {knightSetting} {bishopSetting}. It must be a legal position. Include the white king and the black king."""
      out = chat(args, inp)
      fen = extract_fen(out)
      if fen:
        out = f"[{inp}]\n{out}"
        res['chess'] = fen
  elif inp.startswith("fen"):
    fen = extract_fen(inp)
    if fen:
       out = "Here you go."
       res['chess'] = fen
  elif inp != "":
    out = chat(args, inp)
    fen = extract_fen(out)
    print(out, fen)
    if fen:
      res['chess'] = fen

  res["output"] = out
  return res
