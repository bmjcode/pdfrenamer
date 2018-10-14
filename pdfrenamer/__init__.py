#!/usr/bin/env python

"""A simple utility to preview and rename documents."""

try:
    from .ui import PDFRenamer
except (ImportError):
    # This lets main() know to handle the error condition
    PDFRenamer = None

# Export the PDFRenamer widget and our main function
__all__ = ["PDFRenamer", "main"]


def main():
    """Start the PDF Renamer application."""

    import os
    import sys

    from glob import iglob

    try:
        # Python 3
        from tkinter import Tk, TclError
        from tkinter.messagebox import showerror
    except (ImportError):
        # Python 2
        from Tkinter import Tk, TclError
        from tkMessageBox import showerror

    if PDFRenamer:
        # Start the application
        r = PDFRenamer()

        try:
            # Start with the window maximized
            r.wm_state("zoomed")

        except (TclError):
            # ...this isn't available on all platforms
            pass

        # Parse command line arguments
        if len(sys.argv) > 1:
            if os.path.isdir(sys.argv[-1]):
                # If the last command line argument is a folder, then
                # open all files found in that folder
                r.open_dir(os.path.abspath(sys.argv[-1]))

            else:
                # Open each file specified on the command line
                paths = []
                for arg in sys.argv[1:]:
                    for item in iglob(arg):
                        paths.append(os.path.abspath(item))

                r.open(*paths)

        else:
            # Browse for a folder after the main loop has started
            r.after(50, r.browse)

        r.mainloop()

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
