import sys, os
INTERP = os.path.join(os.environ['HOME'], 'pythonenv', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd() + "/pkg/")
import osfflask
application = osfflask.create_app()
