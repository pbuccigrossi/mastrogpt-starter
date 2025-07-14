import chat, history

def stateful(args):
  
  inp = args.get("input", "")
  out = f"Hello from {chat.MODEL}"
  res = {}
  hi = history.History(args)
  res['state'] = hi.id() #non funziona in caso di streaming
  
  if inp != "":
    # load the history in the chat
    
    ch = chat.Chat(args)
    #TODO:E4.2 load the history
    hi.load(ch)
    #END TODO
    # add a message and save it 
    msg = f"user:{inp}"
    ch.add(msg)
    hi.save(msg)

    #print(ch.messages)
    out = ch.complete()

    # complete, save the assistant and return the id
    #TODO:E4.2 save the message and the state
    hi.save(f"assistant:{out}")
    # return the id as state field in the response
    
    #END TODO

    print('>>>>>>>' + hi.id())
    hi.print()

  res['output'] = out
  res['streaming'] = True
  return res
