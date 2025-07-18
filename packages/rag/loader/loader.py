import vdb, bucket, uuid, vision2 as vision, base64
from vdb import RAG_IMAGES_COLLECTION

USAGE = f"""Welcome to the Vector DB Loader.
Type > to upload an image for RAG images.

Write text to insert in the DB. 
Use `@[<coll>]` to select/create a collection and show the collections.
Use `*<string>` to vector search the <string>  in the DB.
Use `#<limit>`  to change the limit of searches.
Use `!<substr>` to remove text with `<substr>` in collection.
Use `!![<collection>]` to remove `<collection>` (default current) and switch to default.
"""

FORM = [
  {
    "label": "Load an image",
    "name": "image",
    "required": "true",
    "type": "file"
  },
]

def loader(args):
  #print(args)
  # get state: <collection>[:<limit>]
  ret = {}
  collection = "default"
  limit = 30
  sp = args.get("state", "").split(":")
  if len(sp) > 0 and len(sp[0]) > 0:
    collection = sp[0]
  if len(sp) > 1:
    try:
      limit = int(sp[1])
    except: pass
  print(collection, limit)

  out = f"{USAGE}Current collection is {collection} with limit {limit}"
  db = vdb.VectorDB(args, collection)
  inp = args.get('input', "")

  #form to upload image
  if inp == ">":
    if collection != RAG_IMAGES_COLLECTION:
      out = f"Switch to {RAG_IMAGES_COLLECTION} collection before loading an image for RAG"
    else:
      ret['form'] = FORM
  #load image
  elif type(inp) is dict and "form" in inp:
    image = inp.get("form", {}).get("image", "")
    resp = loadImage(args, image, db)
    if resp == -1:
      out = "Error on loading the image"
  # select collection
  elif inp.startswith("@"):
    out = ""
    if len(inp) > 1:
       collection = inp[1:]
       out = f"Switched to {collection}.\n"
    out += db.setup(collection)
  # set size of search
  elif inp.startswith("#"):
    try: 
       limit = int(inp[1:])
    except: pass
    out = f"Search limit is now {limit}.\n"
  # run a query
  elif inp.startswith("*"):
    search = inp[1:]
    if search == "":
      search = " "
    res = db.vector_search(search, limit=limit)
    if len(res) > 0:
      out = f"Found:\n"
      for i in res:
        out += f"({i[0]:.2f}) {i[1]}\n"
    else:
      out = "Not found"
  # remove a collection
  elif inp.startswith("!!"):
    if len(inp) > 2:
      collection = inp[2:].strip()
    out = db.destroy(collection)
    collection = "default"
  # remove content
  elif inp.startswith("!"):
    count = db.remove_by_substring(inp[1:])
    out = f"Deleted {count} records."    
  elif inp != '':
    out = "Inserted "
    lines = [inp]
    if args.get("options","") == "splitlines":
      lines = inp.split("\n")
    for line in lines:
      if line == '': continue
      res = db.insert(line)
      out += "\n".join([str(x) for x in res.get("ids", [])])
      out += "\n"

  ret['output'] = out
  ret['state'] = f"{collection}:{limit}"
  return ret

def loadImage(args, image, db):
  print(f"uploaded size {len(image)}")

  #load to S3
  buc = bucket.Bucket(args)
  s3Key = str(uuid.uuid4())
  if buc.write(s3Key, base64.b64decode(image)) == 1:
    #generate image description
    vis = vision.Vision(args)
    visResp = vis.decode(image)
    if visResp == -1:
      print("Error on Vision decode")
    else:
      #load into Vector DB
      res = db.insertImgRef(visResp, s3Key)
  else:
    print("Error on S3 write")
    return -1