from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QHBoxLayout,
    QGroupBox,
)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt
from pymongo import MongoClient
import datetime
import sys
import os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

client = MongoClient("mongodb://localhost:27017")
db = client["budgetTracker"]
incomes_collection = db["incomes"]
expenses_collection = db["expenses"]
categories_collection = db["categories"]


def format_rupiah(amount):
    return f"Rp {amount:,.2f}".replace(",", ".")


class BudgetTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setStyleSheet(
            """
            QWidget {
                background-color: #f4f4f4;
            }
            QLabel {
                font-family: Arial;
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50; /* Green */
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #45a049; /* Darker green */
            }
            QLineEdit, QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #4CAF50; /* Green */
                color: white;
            }
        """
        )

        main_layout = QHBoxLayout()

        self.nav_menu = QListWidget()
        self.nav_menu.addItem(
            QListWidgetItem(QIcon("icon_income.png"), "Add Income/Expense")
        )
        self.nav_menu.addItem(
            QListWidgetItem(QIcon("icon_report.png"), "View Monthly Report")
        )
        self.nav_menu.addItem(
            QListWidgetItem(QIcon("icon_history.png"), "Transaction History")
        )
        self.nav_menu.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QListWidget::item {
                padding: 10px;
            }
        """
        )
        self.nav_menu.currentRowChanged.connect(self.display_page)
        self.nav_menu.setFixedWidth(200)
        main_layout.addWidget(self.nav_menu)

        self.pages = QStackedWidget()
        self.pages.addWidget(self.create_add_income_expense_page())
        self.pages.addWidget(self.create_monthly_report_page())
        self.pages.addWidget(self.create_transaction_history_page())
        main_layout.addWidget(self.pages)
        main_layout.setStretch(1, 3)  # Make the right side 3x wider than the left

        self.setLayout(main_layout)
        self.setWindowTitle("Budget Tracker")
        self.setWindowIcon(QIcon("icon_app.png"))
        self.resize(800, 600)
        self.show()

    def create_add_income_expense_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Add Income/Expense")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form_group = QGroupBox("Add Transaction")
        form_layout = QVBoxLayout()

        self.amount_input = QLineEdit(self)
        self.amount_input.setPlaceholderText("Enter amount")
        self.category_input = QComboBox(self)
        self.update_category_dropdown()

        form_layout.addWidget(QLabel("Amount:"))
        form_layout.addWidget(self.amount_input)
        form_layout.addWidget(QLabel("Category:"))
        form_layout.addWidget(self.category_input)

        add_income_button = QPushButton("Add Income", self)
        add_income_button.setIcon(QIcon("icon_add_income.png"))
        add_income_button.clicked.connect(self.add_income)
        form_layout.addWidget(add_income_button)

        add_expense_button = QPushButton("Add Expense", self)
        add_expense_button.setIcon(QIcon("icon_add_expense.png"))
        add_expense_button.clicked.connect(self.add_expense)
        form_layout.addWidget(add_expense_button)

        # Section for adding a new category
        self.new_category_input = QLineEdit(self)
        self.new_category_input.setPlaceholderText("Enter new category")
        form_layout.addWidget(QLabel("New Category:"))
        form_layout.addWidget(self.new_category_input)

        add_category_button = QPushButton("Add Category", self)
        add_category_button.setIcon(QIcon("icon_add_category.png"))
        add_category_button.clicked.connect(self.add_category)
        form_layout.addWidget(add_category_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        self.balance_label = QLabel("Balance: Rp 0.00")
        self.balance_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.balance_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.balance_label)
        self.update_balance()

        page.setLayout(layout)
        return page

    def create_monthly_report_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Monthly Report")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        monthly_report_button = QPushButton("View Monthly Report", self)
        monthly_report_button.setIcon(QIcon("icon_report.png"))
        monthly_report_button.clicked.connect(self.view_monthly_report)
        layout.addWidget(monthly_report_button)

        self.report_table = QTableWidget()
        self.report_table.setColumnCount(3)
        self.report_table.setHorizontalHeaderLabels(["Date", "Category", "Amount"])
        self.report_table.setStyleSheet(
            """
            QTableWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """
        )
        layout.addWidget(self.report_table)

        # Add pie chart for income and expense
        self.pie_chart_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(self.pie_chart_canvas)

        page.setLayout(layout)
        return page

    def create_transaction_history_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Transaction History")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.transaction_history_table = QTableWidget()
        self.transaction_history_table.setColumnCount(3)
        self.transaction_history_table.setHorizontalHeaderLabels(
            ["Date", "Category", "Amount"]
        )
        self.transaction_history_table.setStyleSheet(
            """
            QTableWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """
        )
        layout.addWidget(self.transaction_history_table)

        view_history_button = QPushButton("View Transaction History", self)
        view_history_button.setIcon(QIcon("icon_history.png"))
        view_history_button.clicked.connect(self.view_transaction_history)
        layout.addWidget(view_history_button)

        page.setLayout(layout)
        return page

    def display_page(self, index):
        self.pages.setCurrentIndex(index)

    def add_income(self):
        try:
            amount = float(self.amount_input.text())
            category = self.category_input.currentText()
            if not category:
                raise ValueError("Category cannot be empty.")

            add_income(amount, category)
            self.amount_input.clear()
            self.update_balance()
            QMessageBox.information(self, "Success", "Income added successfully!")
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Invalid input: {e}")

    def add_expense(self):
        try:
            amount = float(self.amount_input.text())
            category = self.category_input.currentText()
            if not category:
                raise ValueError("Category cannot be empty.")

            add_expense(amount, category)
            self.amount_input.clear()
            self.update_balance()
            QMessageBox.information(self, "Success", "Expense added successfully!")
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Invalid input: {e}")

    def add_category(self):
        name = self.new_category_input.text()
        if name:
            add_category(name)
            self.new_category_input.clear()
            self.update_category_dropdown()
            QMessageBox.information(self, "Success", "Category added successfully!")
        else:
            QMessageBox.warning(self, "Error", "Category name cannot be empty.")

    def update_category_dropdown(self):
        self.category_input.clear()
        self.category_input.addItems([cat["name"] for cat in get_categories()])

    def update_balance(self):
        total_income = sum(record["amount"] for record in incomes_collection.find())
        total_expense = sum(record["amount"] for record in expenses_collection.find())
        balance = total_income - total_expense
        self.balance_label.setText(f"Balance: {format_rupiah(balance)}")

    def view_monthly_report(self):
        month = datetime.datetime.now().month
        year = datetime.datetime.now().year
        report = get_monthly_report(month, year)

        self.report_table.setRowCount(0)
        row_count = 0

        for record in report["records"]:
            self.report_table.insertRow(row_count)
            self.report_table.setItem(
                row_count, 0, QTableWidgetItem(record["date"].strftime("%Y-%m-%d"))
            )
            self.report_table.setItem(
                row_count, 1, QTableWidgetItem(record["category"])
            )
            self.report_table.setItem(
                row_count, 2, QTableWidgetItem(format_rupiah(record["amount"]))
            )
            row_count += 1

        self.update_balance()
        self.update_pie_chart(report["total_income"], report["total_expense"])

        QMessageBox.information(
            self,
            "Monthly Report",
            f"Total Income: {format_rupiah(report["total_income"])}\nTotal Expense: {format_rupiah(report["total_expense"])}",
        )

    def update_pie_chart(self, income, expense):
        ax = self.pie_chart_canvas.figure.subplots()
        ax.clear()
        labels = ["Income", "Expenses"]
        sizes = [income, expense]
        colors = ["#4CAF50", "#FF6347"]  # Green for income, red for expenses
        ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=140)
        ax.set_title("Income vs Expenses")
        self.pie_chart_canvas.draw()

    def view_transaction_history(self):
        records = list(incomes_collection.find()) + list(expenses_collection.find())

        self.transaction_history_table.setRowCount(0)
        row_count = 0

        for record in records:
            self.transaction_history_table.insertRow(row_count)
            self.transaction_history_table.setItem(
                row_count, 0, QTableWidgetItem(record["date"].strftime("%Y=%m-%d"))
            )
            self.transaction_history_table.setItem(
                row_count, 1, QTableWidgetItem(record["category"])
            )
            self.transaction_history_table.setItem(
                row_count, 2, QTableWidgetItem(format_rupiah(record["amount"]))
            )


# Helper functions for database operations
def add_income(amount, category):
    income = {"amount": amount, "category": category, "date": datetime.datetime.now()}
    incomes_collection.insert_one(income)


def add_expense(amount, category):
    expense = {"amount": amount, "category": category, "date": datetime.datetime.now()}
    expenses_collection.insert_one(expense)


def add_category(name):
    category = {"name": name}
    categories_collection.insert_one(category)


def delete_category(name):
    categories_collection.delete_one({"name": name})


def get_categories():
    return list(categories_collection.find())


def get_monthly_report(month, year):
    start = datetime.datetime(year, month, 1)
    end = datetime.datetime(year, month + 1, 1)

    total_income = incomes_collection.aggregate(
        [
            {"$match": {"date": {"$gte": start, "$lt": end}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
        ]
    )

    total_expense = expenses_collection.aggregate(
        [
            {"$match": {"date": {"$gte": start, "$lt": end}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
        ]
    )

    records = list(
        incomes_collection.find({"date": {"$gte": start, "$lt": end}})
    ) + list(expenses_collection.find({"date": {"$gte": start, "$lt": end}}))

    return {
        "total_income": list(total_income)[0].get("total", 0) if total_income else 0,
        "total_expense": list(total_expense)[0].get("total", 0) if total_expense else 0,
        "records": records,
    }


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = BudgetTrackerApp()
    sys.exit(app.exec_())
