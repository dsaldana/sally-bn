#!/usr/bin/env python


import sys
from lib_sallybn import SallyApp

# MAIN
if __name__ == "__main__":
    app = SallyApp.SallyApp()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
