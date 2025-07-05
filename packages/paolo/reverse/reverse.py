def reverse(args):
  out = "Provide the text to reverse"
  inp = args.get("input", "")
  if inp != "":
    out = inp[::-1]
  return { "output": out }
