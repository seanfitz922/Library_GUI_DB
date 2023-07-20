import sqlite3, csv
from book_class import Book
import tkinter as tk
from tkinter import messagebox, filedialog


class LibraryDatabase:
    def __init__(self, parent):
        
        self.parent = parent
        self.current_file = None
        # Connect to the database
        self.conn = sqlite3.connect('library.db') 
        # Create a cursor object 
        self.cursor = self.conn.cursor() 
        # Create the books table if it doesn't exist 
        self.create_books_table()  
        
        #self.fill_db()

    def create_books_table(self):
        # Create the books table with the specified columns
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY,
                title TEXT,
                author TEXT,
                pub_date INTEGER
            )
        ''')  
        # Commit the changes to the database
        self.conn.commit()  

    def populate_books(self, columns, book_listbox):
        # Clear the book_listbox before inserting results
        book_listbox.delete(0, tk.END)

        # Display books
        for column in columns:
            # Format the book information
            book_info = f"ID: {column[0]} | Title: {column[1]} | Author: {column[2]} | Publication Date: {column[3]}"

            # Insert the formatted book information into the book_listbox
            book_listbox.insert(tk.END, book_info)
            book_listbox.insert(tk.END, "")


    def add_book(self, title, author, pub_date, popup_window, book_listbox):
        # Validate the input
        if not title or not author or not pub_date:
            messagebox.showwarning("Invalid Input", "Please provide all book details.")
            return
        
        # Check if pub_date is a valid four-digit number
        try:
            if len(str(int(pub_date))) != 4:
                raise ValueError("Publication date must be a valid four-digit number.")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Publication date must be a valid four-digit number.")
            return     

        # Get the current maximum book_id from the database
        max_book_id = self.get_max_book_id()

        # Calculate the new book_id by incrementing the maximum book_id by 1
        book_id = max_book_id + 1

        # Insert the book into the library database
        self.cursor.execute('''
            INSERT INTO books (book_id, title, author, pub_date)
            VALUES (?, ?, ?, ?)
        ''', (book_id, title, author, pub_date))
        self.conn.commit()

        book_listbox.insert(tk.END, f"ID: {book_id} | Title: {title} | Author: {author} | Publication Date: {pub_date}")
        messagebox.showinfo("Success", "Book added successfully.")
        
        popup_window.destroy()

    def get_max_book_id(self):
        self.cursor.execute("SELECT MAX(book_id) FROM books")
        max_id = self.cursor.fetchone()[0]
        return max_id if max_id is not None else 0

    def remove_book(self, book_id, popup_window, book_listbox):
        # Remove book from table with book id
        if not book_id:
            messagebox.showwarning("Invalid Input", "Please provide the book's ID.")
            return

        # Execute the SQL query to fetch the book with the provided book ID
        self.cursor.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
        book = self.cursor.fetchone()

        # Check if the book ID exists in the database
        if not book:
            messagebox.showwarning("Invalid Book ID", "The provided book ID does not exist.")
            return

        self.cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,)) 
        self.conn.commit()

        # Remove book from the book_listbox
        selected_indices = book_listbox.curselection()
        if selected_indices:
            book_listbox.delete(selected_indices[0])

        messagebox.showinfo("Success", "Book removed successfully.")

        popup_window.destroy()


    def sort_database_title(self, book_listbox, order):
        # Execute the SQL query to select all columns from the books table
        self.cursor.execute("SELECT * FROM books")
        rows = self.cursor.fetchall()

        if rows:
            # Define a custom sorting key function
            def sort_key(row):
                # Extract the title from the row
                title = row[1]
                # Split the title into words
                words = title.split()
                # Ignore certain words at the beginning
                if len(words) > 1 and words[0].lower() in ["the", "a", "an"]:
                    # Sort based on the second word
                    return words[1]
                else:
                    # Sort as is
                    return title

            if order == "ASC":
                # Sort the rows based on the custom sorting key function
                sorted_rows = sorted(rows, key=sort_key)
            else:
                # Sort the rows based on the custom sorting key function in descending order
                sorted_rows = sorted(rows, key=sort_key, reverse=True)

            self.populate_books(sorted_rows, book_listbox)

    def sort_database_author(self, book_listbox, order):
        self.cursor.execute(f"SELECT * FROM books ORDER BY author {order}")
        rows = self.cursor.fetchall()

        if rows:
            self.populate_books(rows, book_listbox)

    def sort_database_int(self, column, book_listbox, order):
        # Execute the SQL query to select all columns from the books table and order by the publication date in ascending order
        self.cursor.execute(f"SELECT * FROM books ORDER BY {column} {order}")
        rows = self.cursor.fetchall()

        if rows:
            self.populate_books(rows, book_listbox)

    def close_file(self):
        # Close the current window
        self.parent.destroy()

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            self.current_file = file_path
            self.update_title()

    def export_database_csv(self):
        # Open file browser dialog to select the save location
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])

        # Check if a file was selected
        if filepath:
            # Execute SQL query to select all rows from the books table
            self.cursor.execute("SELECT * FROM books")
            rows = self.cursor.fetchall()

            if rows:
                # Open the CSV file at the selected location in write mode
                with open(filepath, 'w', newline='') as file:
                    # Create a CSV writer object
                    writer = csv.writer(file)
                    # Write the column headers to the CSV file
                    writer.writerow(['Book ID', 'Title', 'Author', 'Publication Date'])
                    # Write all the rows to the CSV file
                    writer.writerows(rows)
                    
                messagebox.showinfo("Export Success", "Library database exported to " + filepath)
            else:
                messagebox.showwarning("Export Failed", "No books found in the database.")
        else:
            messagebox.showwarning("Export Cancelled", "No file selected.")

    def update_title(self):
        if self.current_file:
            self.file_label.config(text="Current File: " + self.current_file)
            self.title("Library Database - " + self.current_file)
        else:
            self.file_label.config(text="Current File: ")
            self.title("Library Database")

    def close_connection(self):
        self.conn.close()  # Close the database connection

    def search_books(self, search_query):
        # Execute the SQL query to search for books matching the query
        self.cursor.execute(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR book_id LIKE ? OR pub_date LIKE ?",
            ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%')
        )
        rows = self.cursor.fetchall()

        # Return the search results
        return rows


"""
    def fill_db(self):
        for book_data in books_data:
            book = Book(book_data["book_id"], book_data["title"], book_data["author"], book_data["pub_date"])
            self.add_books_db(book)


    def add_books_db(self, book):
        self.cursor.execute('''
            INSERT INTO books (book_id, title, author, pub_date)
            VALUES (?, ?, ?, ?)
        ''', (book.book_id, book.title, book.author, book.pub_date))
        self.conn.commit()

        print(f"Book added to the database: {book.title} by {book.author} ({book.pub_date})")
"""
