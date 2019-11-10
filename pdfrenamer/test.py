"""Test cases for PDF Renamer."""

import os
import shutil
import tempfile
import unittest

try:
    # Python 3
    import tkinter as tk
except (ImportError):
    # Python 2
    import Tkinter as tk

from . import PDFRenamer


# Absolute path to this file
TEST_PY_PATH = os.path.realpath(__file__)


class PDFRenamerTest(unittest.TestCase):
    """Test case for PDF Renamer."""

    def setUp(self):
        """Set up the test case."""

        # Temporary directories for PDF Renamer files
        self.src_dir = tempfile.mkdtemp()
        self.dst_dir = tempfile.mkdtemp()

        # Initial basename (minus extension) for our test file
        self.src_base = "test"

        # Basename (minus extension) for the renamed test file
        self.dst_base = "renamed"

        # Full initial path to the source file
        self.src_path = os.path.join(self.src_dir,
                                     "{0}.txt".format(self.src_base))

        # Full path to the test file after renaming in same dir
        self.dst_path_renamed = os.path.join(self.src_dir,
                                             "{0}.txt".format(self.dst_base))

        # Full path to the test file after renaming and moving
        self.dst_path_moved = os.path.join(self.dst_dir,
                                           "{0}.txt".format(self.dst_base))

        # Make sure all our file paths are unique
        self.assertNotEqual(self.src_path, self.dst_path_renamed)
        self.assertNotEqual(self.src_path, self.dst_path_moved)
        self.assertNotEqual(self.dst_path_renamed, self.dst_path_moved)

        # Create a test file by copying this file's contents
        shutil.copy(TEST_PY_PATH, self.src_path)

        # Make sure only the expected file exists
        self.assertTrue(os.path.isfile(self.src_path))
        self.assertFalse(os.path.isfile(self.dst_path_renamed))
        self.assertFalse(os.path.isfile(self.dst_path_moved))

        # Initialize the PDF Renamer application
        self.root = tk.Tk()
        self.pdf_renamer = PDFRenamer(self.root)
        self.pdf_renamer.pack(side="top", expand=1, fill="both")

        # Display our test file
        self.pdf_renamer.open(self.src_path)

    def tearDown(self):
        """Clean up the test case."""

        # Briefly display the application window
        self.root.after(1000, self.pdf_renamer.close_window)

        # Close the PDF Renamer application
        self.root.wait_window(self.root)

        # Clean up temporary directories
        shutil.rmtree(self.src_dir)
        shutil.rmtree(self.dst_dir)

    #
    # Tests for core functionality (renaming and moving files)
    #

    def test_rename(self):
        """Test renaming a file in the same directory."""

        p = self.pdf_renamer
        p._new_name.set(self.dst_base)
        p._process_rename()
        p.reload()

        self.assertFalse(os.path.isfile(self.src_path))
        self.assertTrue(os.path.isfile(self.dst_path_renamed))
        self.assertFalse(os.path.isfile(self.dst_path_moved))

    def test_rename_and_move(self):
        """Test renaming and moving a file."""

        p = self.pdf_renamer
        p._new_name.set(self.dst_base)
        p._process_rename(self.dst_dir)
        p.reload()

        self.assertFalse(os.path.isfile(self.src_path))
        self.assertFalse(os.path.isfile(self.dst_path_renamed))
        self.assertTrue(os.path.isfile(self.dst_path_moved))
