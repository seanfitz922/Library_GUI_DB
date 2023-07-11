import tkinter as tk 
from tkinter import messagebox
from library_database import LibraryDatabase

class LibraryGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set up the window properties
        self.title("Library Database")
        self.geometry("800x600")  # Set the window size to 800x600

        # Initialize the library database
        self.library_db = LibraryDatabase()
        
        # Call methods to set up the GUI components
        self.create_widgets()
        self.populate_book_list()

    def create_widgets(self):
        # Create and configure GUI components (labels, buttons, etc.)
        # ... Place them using grid(), pack(), or place() methods
        
        self.book_listbox = tk.Listbox(self, font=("Arial", 15), height=25, width = 50)
        self.book_listbox.grid(row=0, column=0)

    
    def populate_book_list(self):
        # Retrieve book titles from the library database and populate the listbox
        book_titles = self.library_db.sort_database_title()

        for title in book_titles:
            self.book_listbox.insert(tk.END, title)

    # Add other methods for event handling, button clicks, etc.
    # ...

# Create an instance of the LibraryGUI class and run the GUI
library_gui = LibraryGUI()
library_gui.mainloop()