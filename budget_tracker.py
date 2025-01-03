from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QListWidget, QStackedWidget, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from pymongo import MongoClient
import datetime
import sys
import os


client = MongoClient("mongodb://localhost:27017")
db = client["budgetTracker"]
incomes_collection = db["incomes"]
expenses_collection = db["expenses"]
categories_collection = db["categories"]


class BudgetTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    
    def initUI(self):
        main_layout = QHBoxLayout()
        
        self.nav_menu = QListWidget()
        self.nav_menu.addItem("Add Income/Expense")
        self.nav_menu.addItem("View Monthly Report")
        self.nav_menu.addItem("Transaction History")
        self.nav_menu.currentRowChanged.connect(self.display_page)
        main_layout.addWidget(self.nav_menu)
        
        self.pages = QStackedWidget()
        self.pages.addWidget(self.create_add_income_expense_page())
        self.pages.addWidget(self.create_monthly_report_page())
        self.pages.addWidget(self.create_transaction_history_page())
        main_layout.addWidget(self.pages)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Budget Tracker")
        self.resize(700, 500)
        self.show()
        
    
    def create_add_income_expense_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Add Income/Expense")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.amount_input = QLineEdit(self)
        self.amount_input.setPlaceholderText("Enter amount")
        self.category_input = QComboBox(self)
        self.update_category_dropdown()
        
        layout.addWidget(QLabel("Amount:"))
        layout.addWidget(self.amount_input)
        layout.addWidget(QLabel("Category:"))
        layout.addWidget(self.category_input)
        
        add_income_button = QPushButton("Add Income", self)
        add_income_button.clicked.connect(self.add_income)
        layout.addWidget(add_income_button)
        
        add_expense_button = QPushButton("Add Expense", self)
        add_expense_button.clicked.connect(self.add_expense)        
        layout.addWidget(add_expense_button)
        
        self.category_name_input = QLineEdit(self)
        self.category_name_input.setPlaceholderText("Enter category name")
        layout.addWidget(QLabel("New Category:"))
        layout.addWidget(self.category_name_input)
        
        add_category_button = QPushButton("Add Category", self)
        add_category_button.clicked.connect(self.add_category)
        layout.addWidget(add_category_button)
        
        self.balance_label = QLabel("Balance: $0.00")
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
        monthly_report_button.clicked.connect(self.view_monthly_report)
        layout.addWidget(monthly_report_button)
        
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(3)
        self.report_table.setHorizontalHeaderLabels(["Date", "Category", "Amount"])
        layout.addWidget(self.report_table)
        
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
        self.transaction_history_table.setHorizontalHeaderLabels(["Date", "Category", "Amount"])
        layout.addWidget(self.transaction_history_table)
        
        view_history_button = QPushButton("View Transaction History", self)
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

            
    def update_category_dropdown(self):
        self.category_input.clear()
        self.category_input.addItems([cat["name"] for cat in get_categories()])

    def add_category(self):
        name = self.category_name_input.text()
        if name:
            add_category(name)
            self.category_name_input.clear()
            self.update_category_dropdown()
            QMessageBox.information(self, "Success", "Category added successfully!")
        else:
            QMessageBox.warning(self, "Error", "Category name cannot be empty.")

    def view_monthly_report(self):
        month = datetime.datetime.now().month
        year = datetime.datetime.now().year
        report = get_monthly_report(month, year)
        
        self.report_table.setRowCount(0)
        row_count = 0
        
        for record in report["records"]:
            self.report_table.insertRow(row_count)
            self.report_table.setItem(row_count, 0, QTableWidgetItem(record["date"].strftime("%Y-%m-%d")))
            self.report_table.setItem(row_count, 1, QTableWidgetItem(record["category"]))
            self.report_table.setItem(row_count, 2, QTableWidgetItem(f"{record["amount"]:.2f}"))
            row_count += 1
            
        self.update_balance()
            
        QMessageBox.information(
            self,
            "Monthly Report",
            f"Total Income: {report["total_income"]}\nTotal Expense: {report["total_expense"]}",
        )
        
        
    def view_transaction_history(self):
        records = list(incomes_collection.find()) + list(expenses_collection.find())
        
        self.transaction_history_table.setRowCount(0)
        row_count = 0
        
        for record in records:
            self.transaction_history_table.insertRow(row_count)
            self.transaction_history_table.setItem(row_count, 0, QTableWidgetItem(record["date"].strftime("%Y=%m-%d")))
            self.transaction_history_table.setItem(row_count, 1, QTableWidgetItem(record["category"]))
            self.transaction_history_table.setItem(row_count, 2, QTableWidgetItem(f"{record['amount']:.2f}"))
            
    
    def update_balance(self):
        total_income = sum(record["amount"] for record in incomes_collection.find())
        total_expense = sum(record["amount"] for record in expenses_collection.find())
        balance = total_income - total_expense
        self.balance_label.setText(f"Balance: ${balance:.2f}")
        
        
   
    
    
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
    
    total_income = incomes_collection.aggregate([
        {"$match": {"date": {"$gte": start, "$lt": end}}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ])
    
    total_expense = expenses_collection.aggregate([
        {"$match": {"date": {"$gte": start, "$lt": end}}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ])
    
    records = list(incomes_collection.find({"date": {"$gte": start, "$lt": end}})) + \
              list(expenses_collection.find({"date": {"$gte": start, "$lt": end}}))
    
    return {
        "total_income": list(total_income)[0].get("total", 0) if total_income else 0,
        "total_expense": list(total_expense)[0].get("total", 0) if total_expense else 0,
        "records": records,
    }
    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = BudgetTrackerApp()
    sys.exit(app.exec_())