#!/usr/bin/env python3

"""A simple utility to preview and rename documents."""

import os
import sys

from tkinter import Tk
from tkinter.messagebox import showerror

try:
    from pdfrenamer import main
except (ImportError):
    # Indicate we need to handle the error condition
    main = None


if __name__ == "__main__":
    if main:
        main()

    else:
        # Check for missing dependencies not in the standard library
        missing_deps = []

        # Dependency: tkDocViewer
        try: import tkdocviewer
        except (ImportError): missing_deps.append("tkDocViewer")

        # Dependency: userpaths
        try: import userpaths
        except (ImportError): missing_deps.append("userpaths")

        # If pip is present, we'll suggest how to install the needed modules
        try: import pip
        except (ImportError): pip = None

        if missing_deps:
            # Format the error message
            bulleted_deps = ["    * {0}".format(dep)
                             for dep in missing_deps]
            message = ("Your system is missing the following Python "
                       "module(s) required to run this program:\n"
                       "\n"
                       "{0}"
                      ).format("\n".join(bulleted_deps))

            if pip:
                # Always suggest the command-line version of Python
                python_exe = sys.executable.replace("pythonw", "python")

                message += ("\n"
                            "\n"
                            "To install them, try running:\n"
                            "{0} -m pip install {1}"
                           ).format(python_exe, " ".join(missing_deps))

            # Hide the root window when calling showerror()
            root = Tk()
            root.withdraw()

            # Display an error message
            showerror("Missing Dependencies", message, parent=root)

            # Exit with an error
            sys.exit(1)
