"""A simple utility to preview and rename documents."""

import os
import sys

from glob import iglob

from tkinter import TclError, ttk

from .ui import PDFRenamer


# Export the PDFRenamer widget and our main function
__all__ = ["PDFRenamer", "main"]


def main():
    """Start the PDF Renamer application."""

    # Start the application
    r = PDFRenamer()

    # Configure toolbar button styles
    s = ttk.Style()
    s.configure("ToolbarFlat.TButton", borderwidth=1, relief="flat")
    s.configure("ToolbarRaised.TButton", borderwidth=1, relief="raised")

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
