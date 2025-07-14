import os, requests as req, base64
import vision2 as vision
import bucket

USAGE = "Please upload a picture and I will tell you what I see"
FORM = [
  {
    "label": "Load Image",
    "name": "pic",
    "required": "true",
    "type": "file"
  },
]

def form(args):
  res = {}
  out = USAGE
  inp = args.get("input", "")

  #print(args)

  print('>>>>> load 1')
  print(type(inp))
  print("form" in inp)

  if type(inp) is dict and "form" in inp:
    img = inp.get("form", {}).get("pic", "")
    print(f"uploaded size {len(img)}")

    vis = vision.Vision(args)
    picName = vis.nameIt(img)

    buc = bucket.Bucket(args)
    print(buc.write(picName, base64.b64decode(img)))

    out = vis.decode(img)
    exturl = buc.exturl(picName, 3600)
    res['html'] = f'<img src="{exturl}">'
    
  res['form'] = FORM
  res['output'] = out
  
  return res
