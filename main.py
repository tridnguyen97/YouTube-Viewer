import sys
from application import Application

if __name__ == '__main__':
    app = Application()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
