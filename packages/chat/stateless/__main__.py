#--kind python:default
#--web true
#TODO:E2.1
#--param OLLAMA_HOST $OLLAMA_HOST
#--param OLLAMA_TOKEN $AUTH
#END TODO

import stateless
def main(args):
  return { "body": stateless.stateless(args) }
