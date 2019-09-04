"""PDF Renamer user interface."""

import os
import sys
import shutil

from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import (askdirectory,
                                askopenfilenames,
                                asksaveasfilename)
from tkinter.messagebox import showerror, showwarning

from configparser import RawConfigParser

import userpaths
from tkdocviewer import DocViewer

from . import config, icons, util
from .about_dialog import AboutDialog


__all__ = ["PDFRenamer"]


class PDFRenamer(Tk):
    """PDF Renamer user interface."""

    def __init__(self):
        """Return a new PDF Renamer application window."""

        Tk.__init__(self)
        self.title(None)            # Note we've overridden this function

        # List of currently displayed files
        self._files = []

        # Index of the currently selected file in self._files
        self._selected_index = 0

        # Absolute path of the currently selected file
        # This is a StringVar so it can double as a variable for the
        # radio buttons in the Go menu.
        self._selected_file = StringVar()

        # Basename of the current file, minus the extension
        self._new_name = StringVar()

        # Last used directory for the Browse dialog
        self._browse_dir = userpaths.get_my_documents()

        # Last used directory for the "Rename and Move" feature
        self._rename_and_move_dir = userpaths.get_my_documents()

        # Frame for the rename controls
        f = Frame(self)
        f.pack(side="top", fill="x")

        # Icons
        self._icon_back = PhotoImage(data=icons.action_back_gif)
        self._icon_forward = PhotoImage(data=icons.action_forward_gif)
        self._icon_wand = PhotoImage(data=icons.icon_wand_gif)

        # Left-hand command buttons
        b = Toolbutton(f,
                       width=4,
                       text="Prev",
                       image=self._icon_back,
                       compound="left",
                       command=self.go_previous)
        b.pack(side="left", ipadx=4, fill="y")

        b = Toolbutton(f,
                       width=4,
                       text="Next",
                       image=self._icon_forward,
                       compound="left",
                       command=self.go_next)
        b.pack(side="left", ipadx=4, fill="y")

        # Right-hand command buttons
        b = Toolbutton(f,
                       width=6,
                       text="Rename",
                       image=self._icon_wand,
                       compound="left",
                       command=self.rename_and_go_next)
        b.pack(side="right", ipadx=6, fill="y")

        # Text entry for the new filename
        e = self.filename_entry = Entry(f,
                                        textvariable=self._new_name)
        e.pack(side="left", expand=1, fill="both", padx=1)

        # Key bindings for the entry box
        e.bind("<Return>", self.rename_and_go_next)
        e.bind("<Shift-Return>", self.rename)
        e.bind("<Control-z>", self.reset_new_name)

        # Separator between the command frame and viewer widget
        sep = Separator(self)
        sep.pack(fill="x")

        # Document viewer widget
        v = self.viewer = DocViewer(self,
                                    borderwidth=0,
                                    use_ttk=True)

        # This fits most of a letter-size page on a modern widescreen display
        v.fit_page(8.5, 11.0 * 3/5)

        # Allow mouse scrolling when the focus is on the entry box
        v.bind_scroll_wheel(e)

        # Pack the viewer widget
        v.pack(side="top", expand=1, fill="both")

        # Add a size grip for good measure
        sg = Sizegrip(v)
        sg.grid(row=1, column=1, sticky="se")

        # Menu bar
        top = self.winfo_toplevel()
        m = top["menu"] = Menu(top)

        # File menu
        m_file = Menu(m, tearoff=0)
        m_file.add_command(label="Open Files...",
                           accelerator="Ctrl+O",
                           underline=0,
                           command=self.browse)
        m_file.add_command(label="Open Folder...",
                           underline=5,
                           command=self.browse_for_dir)
        m_file.add_separator()
        m_file.add_command(label="Open in Default Viewer...",
                           underline=16,
                           accelerator="Ctrl+R",
                           command=self.open_in_default_viewer)
        m_file.add_command(label="Rename and Move...",
                           underline=11,
                           accelerator="Ctrl+M",
                           command=self.rename_and_move)
        m_file.add_separator()
        m_file.add_command(label="Close",
                           underline=0,
                           accelerator="Ctrl+W",
                           command=self.close_file)
        m_file.add_command(label="Exit",
                           underline=1,
                           accelerator="Ctrl+Q",
                           command=self.close_window)
        m.add_cascade(label="File", underline=0, menu=m_file)

        # Go menu
        m_go = self.m_go = Menu(m, tearoff=0)
        m_go.add_command(label="Previous",
                         underline=0,
                         accelerator="Page Up",
                         command=self.go_previous)
        m_go.add_command(label="Next",
                         underline=0,
                         accelerator="Page Down",
                         command=self.go_next)
        m_go.add_separator()
        # The rest of the menu will be filled with the names of open files
        m.add_cascade(label="Go", underline=0, menu=m_go)

        # Options menu
        m_options = self.m_options = Menu(m, tearoff=0)
        m_options.add_checkbutton(label="Enable PDF Downscaling",
                                  underline=11,
                                  variable=v.enable_downscaling,
                                  command=self.reload)
        m.add_cascade(label="Options", underline=0, menu=m_options)

        # Help menu
        m_help = self.m_help = Menu(m, tearoff=0)
        m_help.add_command(label="About...",
                           underline=0,
                           command=self.about_dialog)
        m.add_cascade(label="Help", underline=0, menu=m_help)

        # Key bindings
        self.bind("<F5>", self.reload)
        self.bind("<Prior>", self.go_previous)              # page up
        self.bind("<Next>", self.go_next)                   # page down
        self.bind("<Control-l>", self.focus_filename_entry)
        self.bind("<Control-m>", self.rename_and_move)
        self.bind("<Control-o>", self.browse)
        self.bind("<Control-q>", self.close_window)
        self.bind("<Control-r>", self.open_in_default_viewer)
        self.bind("<Control-w>", self.close_file)

        # Cancel PDF rendering when Esc is pressed
        self.bind("<Escape>", v.cancel_rendering)

        # Call close_window() when the window is X'd
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # Load configuration options
        self._load_config()

    # ------------------------------------------------------------------------

    def about_dialog(self, event=None):
        """Show the About dialog."""

        # Debugging information
        debug_info = []

        # Python version
        debug_info += "Python version: {0}".format(sys.version).splitlines()
        debug_info.append("Tk version: {0}".format(TkVersion))
        debug_info.append("")

        # Ghostscript version
        gs_version = DocViewer.gs_version()
        if gs_version:
            debug_info.append("Ghostscript version: {0}"
                              .format(gs_version))
            debug_info.append("Ghostscript executable: {0}"
                              .format(DocViewer.gs_executable()))
            debug_info.append("Ghostscript search path: {0}"
                              .format(", ".join(DocViewer.gs_search_path())))
        else:
            debug_info.append("Ghostscript not installed")
        debug_info.append("")

        # Command line
        args = []
        for arg in sys.argv:
            if " " in arg:
                args.append('"{0}"'.format(arg))
            else:
                args.append(arg)
        debug_info.append("Command line: {0}".format(" ".join(args)))

        ad = AboutDialog(self, config.NAME,
                         version=config.VERSION,
                         copyright=config.COPYRIGHT,
                         license=config.LICENSE)

        ad.add_tab("Debug Info", "\n".join(debug_info))

        ad.focus_set()
        self.wait_window(ad)

    def browse(self, event=None):
        """Browse for files to process."""

        # Start in the directory containing the current file, or the
        # current working directory if no files are currently open
        if self._files:
            initialdir = os.path.dirname(self._selected_file.get())
        else:
            initialdir = self._browse_dir

        doc_extensions = "*.pdf"
        image_extensions = " ".join("*{0}".format(ext)
                                    for ext in DocViewer.image_extensions)
        text_extensions = " ".join("*{0}".format(ext)
                                   for ext in DocViewer.text_extensions)

        all_extensions = " ".join((doc_extensions,
                                   image_extensions,
                                   text_extensions))

        filetypes = (
            ("All Supported File Types", all_extensions),
            ("Documents", doc_extensions),
            ("Image Files", image_extensions),
            ("Plain-Text Files", text_extensions),
            ("All Files", "*.*"),
        )

        new_files = askopenfilenames(parent=self,
                                     title="Select Files to Rename",
                                     initialdir=initialdir,
                                     filetypes=filetypes)

        if new_files:
            # Note that self.open() will normalize the pathnames
            self.open(*new_files)

        elif not self._files:
            # Close the application if no files were previously open
            self.close_window()

    def browse_for_dir(self, event=None):
        """Browse for an entire directory to process."""

        # Start in the directory containing the current file, or the
        # current working directory if no files are currently open
        if self._files:
            initialdir = os.path.dirname(self._selected_file.get())
        else:
            initialdir = self._browse_dir

        new_dir = askdirectory(parent=self,
                               title="Select Folder",
                               initialdir=initialdir)

        if new_dir:
            # Note that self.open_dir() will normalize the pathname
            self.open_dir(new_dir)

        elif not self._files:
            # Close the application if no files were previously open
            self.close_window()

    def close_file(self, event=None):
        """Close the current file and display the next."""

        self.viewer.cancel_rendering()
        self.viewer.erase()

        i = self._selected_index
        del self._files[i]

        if self._files:
            self._update_go_menu()

            # Display the next file on the list
            self._preview(i if i < len(self._files) - 1 else 0)

        else:
            # We're out of files; close the program
            self.close_window()

    def close_window(self, event=None):
        """Close the application window."""

        try:
            self._save_config()

        except (Exception) as err:
            showerror("Could Not Save Configuration",
                      err,
                      parent=self)

        self.destroy()

    def focus_filename_entry(self, event=None):
        """Set the focus on the filename entry widget and select all text."""

        self.filename_entry.focus_set()
        self.filename_entry.icursor("end")
        self.filename_entry.selection_range(0, "end")

    def go_next(self, event=None):
        """Display the next file to process."""

        p = self._files
        i = self._selected_index

        self._preview(i + 1 if i < len(p) - 1 else 0)

    def go_previous(self, event=None):
        """Display the previous file to process."""

        p = self._files
        i = self._selected_index

        self._preview(i - 1 if i > 0 else len(p) - 1)

    def open(self, *paths):
        """Open each of the specified files."""

        if paths:
            self.viewer.cancel_rendering()
            self.viewer.erase()

            # Close all open files
            del self._files[:]
            self._selected_index = 0

            for path in paths:
                if os.path.isfile(path):
                    # Save the absolute path to this file
                    self._files.append(os.path.abspath(path))

            self._update_go_menu()
            self._preview(0)

        else:
            showwarning("No Files",
                        "Could not find any of the specified files.",
                        parent=self)

            if not self._files:
                # Close the application if no files were previously open
                self.close_window()

    def open_dir(self, path):
        """Open all files in the specified directory."""

        # Normalize the pathname
        # Having this here cleans weirdness from both Tk dialogs and sys.argv
        path = os.path.normpath(path)

        # Identify files in this folder
        items = map(lambda item: os.path.join(path, item),
                    sorted(os.listdir(path)))

        # Filter out items we can't display
        items = filter(self.viewer.can_display, items)

        # On Python 3, map and filter are distinct types
        items = list(items)

        if items:
            self._files = items
            self._selected_index = 0
            self._preview(0)
            self._update_go_menu()

        else:
            showwarning("No Files",
                        "Could not process any files in the folder:\n"
                        "{0}"
                        .format(path),
                        parent=self)

            if not self._files:
                # Close the application if no files were previously open
                self.close_window()

    def open_in_default_viewer(self, event=None):
        """Open the current document in the user's default viewer."""

        try:
            util.startfile(self._selected_file.get())

        except (Exception):
            showwarning("Not Implemented",
                        "This feature is not available on your system.",
                        parent=self)

    def reload(self, event=None):
        """Reload the displayed document from disk."""

        # Note: Binding directly to self.viewer.reload() won't work if
        # we renamed the document before reloading, so we have to do this.
        if self._files:
            self._preview(self._selected_index)

    def rename(self, event=None):
        """Rename the current file.

        Returns True if the file was successfully renamed, False otherwise.
        """

        # Sanity check: Make sure the viewer is done rendering before
        # we do anything to the file
        rendering = self.viewer.rendering
        if rendering.get():
            self.viewer.cancel_rendering()
            self.wait_variable(rendering)

        try:
            self._process_rename()
            return True

        except (RenamerError) as err:
            showerror("Error",
                      err,
                      parent=self)
            return False

    def rename_and_go_next(self, event=None):
        """Rename the current file and move on to the next one."""

        # Only display the next file if renaming this one was successful
        if self.rename(event):
            self.go_next(event)

    def rename_and_move(self, event=None):
        """Rename this file and move it to another folder."""

        # Sanity check: Make sure the viewer is done rendering before
        # we do anything to the file.
        rendering = self.viewer.rendering
        if rendering.get():
            self.viewer.cancel_rendering()
            self.wait_variable(rendering)

        # Get the extension of the displayed file
        src_base, ext = os.path.splitext(self._selected_file.get())

        # Prompt for a destination filename
        dst_path = asksaveasfilename(parent=self,
                                     title="Rename and Move",
                                     initialdir=self._rename_and_move_dir,
                                     initialfile=self._new_name.get() + ext,
                                     defaultextension=ext)

        # Sanity check: Make sure the user entered a filename
        if not dst_path:
            return

        # Normalize and split the path
        dst_path = os.path.normpath(dst_path)
        dst_dir, dst_base = os.path.split(dst_path)

        # Save the new name for this file
        dst_base, ext = os.path.splitext(dst_base)
        self._new_name.set(dst_base)

        # Save the last-used destination folder
        self._rename_and_move_dir = dst_dir

        try:
            self._process_rename(dst_dir)
            self.go_next()

        except (RenamerError) as err:
            showerror("Error",
                      err,
                      parent=self)

    def reset_new_name(self, event=None):
        """Reset the new name of the displayed file."""

        selected_file = self._selected_file.get()
        base, ext = os.path.splitext(os.path.basename(selected_file))

        # Reset the displayed basename
        self._new_name.set(base)

        # Set the focus on the filename entry box and select all text
        self.focus_filename_entry()

    def title(self, string=None):
        """Set the title of this window."""

        if string:
            Tk.title(self, "{0} - {1}".format(config.NAME, string))
        else:
            Tk.title(self, config.NAME)

    # ------------------------------------------------------------------------

    def _load_config(self):
        """Load configuration options."""

        cfg = RawConfigParser()
        cfg.read([config.config_path])

        if cfg.has_option("ui", "browse_dir"):
            self._browse_dir = cfg.get("ui", "browse_dir")

        if cfg.has_option("ui", "enable_downscaling"):
            enable_downscaling = cfg.getboolean("ui", "enable_downscaling")
            self.viewer.enable_downscaling.set(enable_downscaling)

        if cfg.has_option("ui", "rename_and_move_dir"):
            self._rename_and_move_dir = cfg.get("ui", "rename_and_move_dir")

    def _preview(self, index=0):
        """Preview the selected file."""

        # Sanity check: Make sure we actually have files to process.
        if not self._files:
            # FIXME: When would this method be called with no files open?
            showerror("Error",
                      "Cannot display a preview because no files are open.",
                      parent=self)
            return

        self._selected_index = index
        selected_file = self._files[index]
        self._selected_file.set(selected_file)

        # Open the next Browse dialog in the directory containing this file
        self._browse_dir = os.path.dirname(selected_file)

        # Sanity check: Make sure the file still exists. If it doesn't,
        # remove it silently from the list and display the next one.
        if not os.path.isfile(selected_file):
            return self.close_file()

        # Display the file
        self.viewer.display_file(selected_file)

        # Update the title bar to show where we are in the list
        self.title("{0} of {1}".format(index + 1, len(self._files)))

        # Reset the new name of the displayed file
        self.reset_new_name()

    def _process_rename(self, dst_dir=None):
        """Rename and optionally move the displayed file.

        If dst_dir is specified, the renamed file will be moved to that
        location. Otherwise, it will be renamed in-place.
        """

        # Identify the new name the user has entered
        dst_base = self._new_name.get()
        if not dst_base:
            raise RenamerError("Please enter a new name for this file.")

        # Identify the displayed file
        src_path = self._selected_file.get()

        # Separate the dirname and basename
        src_dir, src_base = os.path.split(src_path)

        # Separate the basename and extension
        src_base, ext = os.path.splitext(src_base)

        # Identify the destination directory
        if not dst_dir:
            dst_dir = src_dir

        # Reconstruct the filename using the new basename
        dst_path = os.path.join(dst_dir, dst_base + ext)

        # Sanity check: Make sure there's no existing file with this name
        if src_path != dst_path and os.path.exists(dst_path):
            raise RenamerError("File already exists:\n"
                               "{0}"
                               .format(dst_path))

        try:
            # Rename the file
            shutil.move(src_path, dst_path)

            # Update the list of available files
            self._files[self._selected_index] = dst_path
            self._selected_file.set(dst_path)

            # Update the Go menu
            self._update_go_menu()

        except (Exception) as err:
            # IOError, OSError, and maybe shutil.Error are the most likely
            # exceptions, but we may as well catch them all so this will fail
            # gracefully if someone ever finds a weird corner case.
            raise RenamerError("Could not rename:\n"
                               "{0}\n"
                               "\n"
                               "{1}"
                               .format(src_path, err))

    def _save_config(self):
        """Save configuration options."""

        cfg = RawConfigParser()
        cfg.read([config.config_path])

        if not cfg.has_section("ui"):
            cfg.add_section("ui")

        cfg.set("ui", "browse_dir", self._browse_dir)
        cfg.set("ui", "enable_downscaling",
                str(self.viewer.enable_downscaling.get()))
        cfg.set("ui", "rename_and_move_dir", self._rename_and_move_dir)

        try:
            # Make a folder for the configuration file if needed
            config_dir = os.path.dirname(config.config_path)
            if not os.path.isdir(config_dir):
                os.makedirs(config_dir)

            # Save the configuration file
            with open(config.config_path, "w") as config_file:
                cfg.write(config_file)

        except (Exception):
            # The worst case here is we can't save the configuration file
            pass

    def _update_go_menu(self):
        """Update the navigation menu."""

        m_go = self.m_go
        m_go.delete(3, "end")

        for i, path in enumerate(self._files):
            # Command to display this file
            go_command = lambda event=None, i=i: self._preview(i)

            # Add this file to the menu
            m_go.add_radiobutton(label=os.path.basename(path),
                                 variable=self._selected_file,
                                 value=path,
                                 command=go_command)


class Toolbutton(Button):
    """A flat toolbar button that raises on mouseover."""

    def __init__(self, master, **kw):
        """Return a new Toolbutton widget."""

        Button.__init__(self, master, **kw)

        self.configure(takefocus=0,
                       style="ToolbarFlat.TButton")

        # Tk widgets have the overrelief property to achieve this effect,
        # but the widget reverts to its default relief after being clicked.
        # Binding to Enter / Leave makes the mouseover relief persistent.
        self.bind("<Enter>", self._handle_enter)
        self.bind("<Leave>", self._handle_leave)

    def _handle_enter(self, event):
        self.configure(style="ToolbarRaised.TButton")

    def _handle_leave(self, event):
        self.configure(style="ToolbarFlat.TButton")


class RenamerError(Exception):
    """Exception representing an error message during a rename operation."""

    pass
