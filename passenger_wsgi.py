import sys, os
INTERP = os.path.join(os.getcwd(), 'osfvenv', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, os.getcwd() + "/pkg/")
import osfflask
application = osfflask.create_app()
