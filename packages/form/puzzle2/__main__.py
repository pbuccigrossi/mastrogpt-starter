#--kind python:default
#--web true
#--param OLLAMA_HOST $OLLAMA_HOST
#--param AUTH $AUTH

import puzzle2
def main(args):
  return { "body": puzzle2.puzzle(args) }
