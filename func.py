import os
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, './functions')
modules = os.listdir('./functions')
for mod in modules:
    if mod.endswith(".py"):
        string = f'from {mod[:-3]} import *'
        try:
            exec (string)
        except:
            pass