"""Student Management System GUI to manage student data.

Provides a student management solution where you can add, edit, delete, and serch students.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QGridLayout, QVBoxLayout, QLabel, QWidget, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QComboBox, \
    QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sqlite3
import sys
import config.cfg as cfg


class DatabaseConnection:
    """Handles database connection
    """

    def __init__(self, database_file: str = None) -> None:
        """Initializes the database connection object.

        Args:
            database_file: The path to the database file.

        Returns:
            None
        """
        self.database_file = database_file or cfg.database_file

    def connect(self) -> sqlite3.Connection:
        """Connects to the database.

        Returns:
            sqlite3.Connection: The database connection object.
        """
        connection = sqlite3.connect(self.database_file)
        return connection


class MainWindow(QMainWindow):
    """Main application window of the Student Management System.
    """

    def __init__(self) -> None:
        """Initializes the main application window.

        This contains the different menu bar and displays the table of student.

        Returns:
            None
        """
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("../../resources/icons/add.png"),"Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon("../../resources/icons/search.png"),"Search", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self) -> None:
        """Handles the click event to show edit and delete options.

        Returns:
            None
        """
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self) -> None:
        """Retrieves the database data and diplays the table.

        Returns:
            None
        """
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self) -> None:
        """Display the insert dialog box to add new student.

        Returns:
            None
        """
        dialog = InsertDialog()
        dialog.exec()
    
    def search(self) -> None:
        """Display the search dialog box to find student.

        Returns:
            None
        """
        dialog = SearchDialog()
        dialog.exec()

    def edit(self) -> None:
        """Display the edit dialog box to update student.

        Returns:
            None
        """
        dialog = EditDialog()
        dialog.exec()

    def delete(self) -> None:
        """Display the delete dialog box to remove student.

        Returns:
            None
        """
        dialog = DeleteDialog()
        dialog.exec()

    def about(self) -> None:
        """Display the about dialog box to show application information.

        Returns:
            None
        """
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    """Window showing information about the application."""

    def __init__(self) -> None:
        """Initializes the About window with application information.

        Returns:
            None
        """
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created the course "The Python Mega Course".
        Feel free to modify and reuse this app.
        """
        self.setText(content)


class DeleteDialog(QDialog):
    """Window showing an option to delete a student record."""

    def __init__(self) -> None:
        """Initializes the Delete window for deletion of student record.

        Returns:
            None
        """
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()

        index = main_window.table.currentRow()
        self.student_id = main_window.table.item(index, 0).text()

        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")
        yes.clicked.connect(self.delete_student)
        no.clicked.connect(self.delete_student)
        
        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

    def delete_student(self) -> None:
        """Deletes a student record to the database.

        Returns:
            None
        """
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (self.student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully.")
        confirmation_widget.exec()


class EditDialog(QDialog):
    """Window showing an option to edit a student record."""

    def __init__(self) -> None:
        """Initializes the Edit window for updating of student record.

        Returns:
            None
        """
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        # Get stdent name from selected row
        index = main_window.table.currentRow()
        student_name = main_window.table.item(index, 1).text()
        self.student_id = main_window.table.item(index, 0).text()
        # Add student name field
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        course_name = main_window.table.item(index, 2).text()
        # Add courses field
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        mobile = main_window.table.item(index, 3).text()
        # Add mobile field
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add update button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)
    
    def update_student(self) -> None:
        """Updates a student record to the database.

        Returns:
            None
        """
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?", 
            (self.student_name.text(),
            self.course_name.itemText(self.course_name.currentIndex()),
            self.mobile.text(), 
            self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class InsertDialog(QDialog):
    """Window showing an option to insert a student record."""

    def __init__(self) -> None:
        """Initializes the Insert window for inserting of student record.

        Returns:
            None
        """
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        
        # Add student name field
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add courses field
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add mobile field
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)
    
    def add_student(self) -> None:
        """Inserts a student record to the database.

        Returns:
            None
        """
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor =  connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
            (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class SearchDialog(QDialog):
    """Window showing an option to search a student record."""

    def __init__(self) -> None:
        """Initializes the Search window for searching of student record.

        Returns:
            None
        """
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        
        # Add student name field
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add search button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)
    
    def search(self) -> None:
        """Search a student record to the database.

        Returns:
            None
        """
        name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor =  connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?",
            (name,))
        rows = list(result)
        print(rows)
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            main_window.table.item(item.row(), 1).setSelected(True)
        cursor.close()
        connection.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    main_window.load_data()
    sys.exit(app.exec())