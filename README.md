**PDF Renamer** is a simple utility to preview and rename documents. It actually supports a number of document and image formats, but renaming PDFs was its original purpose, and I haven't yet thought of anything more clever to call it. (Feel free to get in touch if you have any suggestions.)


## Running on Windows

**Windows installers are available on the [releases page on GitHub](https://github.com/bmjcode/pdfrenamer/releases).**

PDF Renamer runs on Windows 7 and newer versions. The installer includes Ghostscript and all the other goodies you need for full file format support.

If you're reading this on GitHub, note this README is from the latest development sources. The installers are built from stable releases, which are safer for day-to-day use, but may not include all the features described in this document.


## Installing from Source

PDF Renamer should run on any recent Windows, Linux, or Unix system that meets the requirements below. It probably also runs on macOS, but this has not yet been tested.

To run PDF Renamer, you need Python, Tkinter, [tkDocViewer](https://github.com/bmjcode/tkDocViewer) (version 2.0.0 or greater), and [userpaths](https://github.com/bmjcode/userpaths). [Pillow](https://python-pillow.org/) is optional, but highly recommended for image format support. Python 3 is preferred; Python 2 support may be phased out in a future release.

If `pip` is available on your system, you can install the needed Python modules by running:
```
python3 -m pip install tkDocViewer userpaths pillow
```

tkDocViewer has a number of runtime dependencies; see its README for the complete list. Make sure you've installed what you need for the formats you want to view. In particular, you'll need [Ghostscript](https://ghostscript.com/) to display PDF and Postscript files. (Most Linux distributions include Ghostscript as part of their print system. If you're on Linux, try running `gs --version` to see if it's installed.)

Once you have everything you need installed, you can start PDF Renamer from the source directory by running:
```
./run.py
```

You can also install it system-wide by running:
```
./setup.py install
```
after which you can start it anywhere by running `pdfrenamer`.


## How to Use PDF Renamer

Using PDF Renamer is pretty straightforward:

1. Select the files you want to rename. The first file will be displayed.
2. Enter a new name for the file. You don't have to include the extension; PDF Renamer will automatically keep its current extension.
3. Press Enter to rename this file. The next file will be displayed.
4. Repeat steps 2 and 3 for each remaining file.

After you rename your last file, PDF Renamer will loop back to your first file. Congratulations, you are done. You can either close the application, or browse for more files to rename.
