import os
import pickle

# Dynamic execution + insecure deserialization (dynamic_exec detector).
def run(blob, cmd):
    os.system("echo starting")
    data = pickle.loads(blob)
    eval(cmd)
    return data
