import os,sys,re
import pdb,traceback,warnings

import argparse
from pprint import pprint


sys.path.append('.')
import osf

def run_program():
    with open('cfg/test.cfg') as fh:
        token = fh.read().strip()
    print(token)
    stuff = osf.session(token)
    usrinfo = stuff.get_user()
    pprint(usrinfo)

try:
    run_program()
except:
    errtype,errvalue,errtb = sys.exc_info()
    traceback.print_exc()
    pdb.post_mortem(errtb)
