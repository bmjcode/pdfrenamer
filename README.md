**PDF Renamer** is a simple utility to preview and rename documents. The name's a bit misleading, since it can display other file formats now, too. But renaming PDFs was its original purpose, and I haven't yet thought of anything more clever to call it.


## Quick Start

First things first: You'll need [Ghostscript](https://ghostscript.com/) installed to display PDF files. Support for other formats is built into PDF Renamer itself.

If you're running Windows, you can download a ready-to-run `PDF Renamer.exe` from GitHub. If you're running Linux, Unix, or macOS, see the instructions under "Installing from Source" below.

Using PDF Renamer is pretty straightforward:

1. Select the folder containing the files you want to rename. (You can also drag and drop files onto the PDF Renamer icon, or pass their names on the command line, to bypass this prompt.) PDF Renamer will display the first file it finds.
2. Enter a new name for this file in the box at the top. (You don't need to include the extension; PDF Renamer will automatically keep the current one.)
3. Press Enter to rename this file and move on to the next.

When you have finished renaming all your files, PDF Renamer will loop back around to the first file. At this point you're good to go -- you can either close the application, or browse for another folder and keep renaming stuff.


## Installing from Source

PDF Renamer requires Python, Tkinter, [tkDocViewer](https://github.com/bmjcode/tkDocViewer), and [userpaths](https://github.com/bmjcode/userpaths). Both Python 2 and 3 are currently supported, though Python 3 is recommended. (Python 2 support may be phased out in a future release.)

More likely than not, you'll also want [Ghostscript](https://ghostscript.com/) for PDF support, and [Pillow](https://python-pillow.org/) for PNG, GIF, and JPEG support. PDF Renamer will technically run without them, but file format support will be extremely limited. Many Linux and Unix systems come with Ghostscript already installed; try running `gs --version` to check.

If `pip` is available on your system, you can install the needed Python modules by running:
```
python3 -m pip install tkDocViewer userpaths pillow
```

You can then start PDF Renamer from the source directory by running:
```
./run.py
```

You can also install it system-wide by running:
```
python3 setup.py install
```

After installing PDF Renamer, you can start it by running `pdfrenamer`.
