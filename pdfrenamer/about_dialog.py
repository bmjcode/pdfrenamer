"""About dialog."""

from tkinter import *
from tkinter.ttk import *


class AboutDialog(Toplevel):
    """About dialog.

    Valid keyword arguments are "version", "copyright", and "license",
    the purpose of which should be self-explanatory.
    """

    def __init__(self, master, program_name, **kw):
        """Return a new About dialog."""

        Toplevel.__init__(self, master)
        self.title("About {0}".format(program_name))
        self.resizable(0, 0)
        self.transient(master)

        if "version" in kw:
            version_text = kw["version"]
        else:
            version_text = None

        if "copyright" in kw:
            copyright_text = kw["copyright"]
        else:
            copyright_text = None

        top_frame = Frame(self)
        top_frame.pack(side="top", fill="x", padx=8, pady=(8, 0))

        name_label = Label(top_frame,
                           text=program_name,
                           anchor="center",
                           justify="center",
                           font=("Times", 14, "bold"))
        name_label.pack(side="top", fill="x")

        if version_text:
            version_label = Label(top_frame,
                                  text="Version {0}".format(version_text),
                                  anchor="center",
                                  justify="center")
            version_label.pack(side="top", fill="x")

        if copyright_text:
            copyright_label = Label(top_frame,
                                    text=copyright_text,
                                    anchor="center",
                                    justify="center")
            copyright_label.pack(side="top", fill="x", pady=(4, 0))

        # Container to hold a space for self.tabs
        tab_container = Frame(self)
        tab_container.pack(side="top", expand=1, fill="both",
                           padx=8, pady=(8, 0))

        # Tabs for additional information (license, etc.)
        # This will be packed the first time add_tab() is called
        self.tabs = Notebook(tab_container)
        self.show_tabs = False

        # License tab
        if "license" in kw:
            self.add_tab("License", kw["license"])

        # Command buttons
        command_frame = Frame(self)
        command_frame.pack(side="top", fill="x", padx=8, pady=8)

        close_button = Button(command_frame,
                              text="Close",
                              default="active",
                              command=self.close_window)
        close_button.pack(side="right")

        for seq in "<Return>", "<Escape>":
            self.bind(seq, self.close_window)

        close_button.focus_set()

    # ------------------------------------------------------------------------

    def add_tab(self, label, contents):
        """Add a tab with the specified label and text contents."""

        container = Frame(self.tabs,
                          borderwidth=1,
                          relief="sunken")
        self.tabs.add(container, text=label, padding=8)

        sb = Scrollbar(container,
                       orient="vertical")
        sb.pack(side="right", fill="y")

        text = Text(container,
                    width=80,
                    height=11,
                    font=("Courier", 8),
                    wrap="word",
                    borderwidth=0,
                    relief="flat")
        text.pack(side="left", expand=1, fill="both")

        text.insert("end", contents)
        text.configure(state="disabled", yscrollcommand=sb.set)
        sb.configure(command=text.yview)

        # Show the tab bar if it's not already visible
        if not self.show_tabs:
            self.tabs.pack(side="top", expand=1, fill="both")
            self.show_tabs = True

    def close_window(self, event=None):
        """Close the dialog."""

        self.destroy()
