import csv
from prettytable import PrettyTable
import json
import os

### Constants
MAX_COLUMNS = 5
COLUMN_HEADERS = ["Date", "Product", "Quantity", "Price", "Total"]
LIST_NAME = "lista.csv"
AUTHOR = "author"


class ListManager:
    def __init__(self, initial_list=None, list_name=LIST_NAME, author=AUTHOR):
        self.max_columns = MAX_COLUMNS
        self.column_headers = COLUMN_HEADERS
        self._list_name = list_name
        self._author = author
        self.csv_filename = None  # Add this line to store the CSV filename
        if initial_list is None:
            self.list = []
        else:
            self.list = [row[:self.max_columns] for row in initial_list]

    @property
    def list_name(self):
        return self._list_name

    @list_name.setter
    def list_name(self, value):
        self._list_name = value

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        self._author = value

    def add(self, sub_list):
        self.list.append(sub_list[:self.max_columns])

    def delete(self, index):
        if index < len(self.list):
            del self.list[index]
        else:
            print("Index out of range")

    def update(self, index, new_sub_list):
        if index < len(self.list):
            self.list[index] = new_sub_list[:self.max_columns]
        else:
            print("Index out of range")

    def display(self):
        for i, sub_list in enumerate(self.list):
            print(f"line {i}: {sub_list}")

    def save_to_csv(self, filename):
        self.csv_filename = filename  # Store the CSV filename
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write list name and author as the first two rows
            writer.writerow(["LIST_NAME", self.list_name])
            writer.writerow(["AUTHOR", self.author])
            # Write column headers
            writer.writerow(self.column_headers)
            # Write data rows
            for sub_list in self.list:
                writer.writerow(sub_list)
        print(f"List saved to {filename}")

    def load_from_csv(self, filename):
        self.csv_filename = filename  # Store the CSV filename
        try:
            with open(filename, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                first_row = next(reader)
                
                if first_row[0] == "LIST_NAME":
                    # New format with LIST_NAME and AUTHOR
                    self.list_name = first_row[1]
                    author_row = next(reader)
                    if author_row[0] == "AUTHOR":
                        self.author = author_row[1]
                    else:
                        print(f"Warning: AUTHOR row not found. Using default author: {AUTHOR}")
                        self.author = AUTHOR
                        csvfile.seek(0)
                        next(reader)  # Skip LIST_NAME row
                    # Skip the header row
                    next(reader)
                else:
                    # Old format without LIST_NAME and AUTHOR
                    print(f"Loading file in old format. Using default list name: {LIST_NAME}")
                    self.list_name = LIST_NAME
                    self.author = AUTHOR
                    csvfile.seek(0)  # Reset file pointer to beginning
                    
                    # Check if the first row matches the column headers
                    if first_row == self.column_headers:
                        print("File contains headers. Skipping header row.")
                        next(reader)  # Skip header row
                    else:
                        print("File does not contain headers. Reading all rows as data.")
                
                self.list = [row[:self.max_columns] for row in reader]
            print(f"List loaded from {filename}")
            print(f"List Name: {self.list_name}")
            print(f"Author: {self.author}")
        except FileNotFoundError:
            print(f"File {filename} not found.")
        except csv.Error as e:
            print(f"Error reading CSV file: {e}")

    def sum_column(self, column_index):
        if column_index < 0 or column_index >= self.max_columns:
            print(f"Invalid column index. Please choose a column between 0 and {self.max_columns - 1}.")
            return None

        total = 0
        non_numeric_count = 0

        for row in self.list:
            if column_index < len(row):
                try:
                    total += float(row[column_index])
                except ValueError:
                    non_numeric_count += 1

        if non_numeric_count > 0:
            print(f"Warning: {non_numeric_count} non-numeric value(s) were skipped.")

        return total

    def input_line(self):
        new_line = input(f"Enter up to {self.max_columns} comma-separated values: ").split(',')
        new_line = [value.strip() for value in new_line]
        self.add(new_line)

    def delete_from_input(self):
        self.display()
        index = int(input("Enter the index of the line to delete: "))
        self.delete(index)

    def update_from_input(self):
        self.display()
        index = int(input("Enter the index of the line to update: "))
        new_line = input(f"Enter up to {self.max_columns} comma-separated values: ").split(',')
        new_line = [value.strip() for value in new_line]
        self.update(index, new_line)

    def sum_column_from_input(self):
        column_index = int(input(f"Enter the column index to sum (0-{self.max_columns-1}): "))
        result = self.sum_column(column_index)
        if result is not None:
            print(f"Sum of column {column_index}: {result}")

    def display_pretty(self):
        if not self.list:
            print("The list is empty.")
            return

        table = PrettyTable()
        table.field_names = ["Row"] + self.column_headers

        for i, row in enumerate(self.list):
            table_row = [i] + row + [''] * (self.max_columns - len(row))
            table.add_row(table_row)

        print(f"List Name: {self.list_name}")
        print(f"Author: {self.author}")
        print(table)

    def get_dimensions(self):
        rows = len(self.list)
        cols = self.max_columns
        return rows, cols

    def export_to_json(self):
        if not self.list:
            print("No data to export.")
            return

        if not self.csv_filename:
            print("No CSV file has been loaded or saved. Please load or save a CSV file first.")
            return

        json_filename = os.path.splitext(self.csv_filename)[0] + '.json'
        
        try:
            data_to_export = {
                "LIST_NAME": self.list_name,
                "AUTHOR": self.author,
                "data": [self.column_headers] + self.list
            }
            
            with open(json_filename, 'w') as json_file:
                json.dump(data_to_export, json_file, indent=2)
            print(f"Data exported to {json_filename} successfully.")
        except IOError as e:
            print(f"Error exporting to JSON: {e}")

def display_menu(manager):
    while True:
        print("\nList Manager Menu:")
        print("1) Add a line")
        print("2) Delete a line")
        print("3) Update a line")
        print("4) Save the list to a CSV file")
        print("5) Load the list from a CSV file")
        print("6) Export to JSON")
        print("7) Display the list (Pretty)")
        print("8) Sum a column")
        print("9) Get list dimensions")
        print("10) Change list name")
        print("11) Change author")
        print("12) Exit")

        choice = input("Enter your choice (1-12): ")

        if choice == '1':
            manager.input_line()
        elif choice == '2':
            manager.delete_from_input()
        elif choice == '3':
            manager.update_from_input()
        elif choice == '4':
            filename = input("Enter the filename to save: ")
            manager.save_to_csv(filename)
        elif choice == '5':
            filename = input("Enter the filename to load: ")
            manager.load_from_csv(filename)
        elif choice == '6':
            manager.export_to_json()
        elif choice == '7':
            manager.display_pretty()
        elif choice == '8':
            manager.sum_column_from_input()
        elif choice == '9':
            rows, cols = manager.get_dimensions()
            print(f"List dimensions: {rows} rows x {cols} columns")
        elif choice == '10':
            new_name = input("Enter new list name: ")
            manager.list_name = new_name
            print(f"List name changed to: {manager.list_name}")
        elif choice == '11':
            new_author = input("Enter new author: ")
            manager.author = new_author
            print(f"Author changed to: {manager.author}")
        elif choice == '12':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

# Example usage:
if __name__ == "__main__":
    manager = ListManager()
    manager.load_from_csv("lista.csv")
    manager.display_pretty()
    display_menu(manager)
