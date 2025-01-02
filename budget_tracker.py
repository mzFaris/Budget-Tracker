from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
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
        layout = QVBoxLayout()
        
        # self.logo = QLabel(self)
        # pixmap = QPixmap("img\\MacBook Pro 14_ - 1.png")
        # self.logo.setPixmap(pixmap)
        # layout.addWidget(self.logo)
        
        title = QLabel("Personal Budget Tracker")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.amount_input = QLineEdit(self)
        self.amount_input.setPlaceholderText("Enter amount")
        self.category_input = QLineEdit(self)
        self.category_input.setPlaceholderText("Enter category")
        
        layout.addWidget(QLabel("Amount:"))
        layout.addWidget(self.amount_input)
        layout.addWidget(QLabel("Category:"))
        layout.addWidget(self.category_input)
        
        add_income_button = QPushButton("Add Income", self)
        add_income_button.clicked.connect(self.add_income)
        
        add_expense_button = QPushButton("Add Expense", self)
        add_expense_button.clicked.connect(self.add_expense)
        
        layout.addWidget(add_income_button)
        layout.addWidget(add_expense_button)
        
        monthly_report_button = QPushButton("View Monthly Report", self)
        monthly_report_button.clicked.connect(self.view_monthly_report)
        layout.addWidget(monthly_report_button)
        
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(3)
        self.report_table.setHorizontalHeaderLabels(["Date", "Category", "Amount"])
        layout.addWidget(self.report_table)
        
        self.setLayout(layout)
        self.setWindowTitle("Budget Tracker")
        self.resize(500, 400)
        self.show()
        
    
    def add_income(self):
        try:
            amount = float(self.amount_input.text())
            category = self.category_input.text()
            if not category:
                raise ValueError("Category cannot be empty.")
            
            add_income(amount, category)
            self.amount_input.clear()
            self.category_input.clear()
            QMessageBox.information(self, "Success", "Income added successfully!")
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Invalid input: {e}")
        
        
    def add_expense(self):
        try:
            amount = float(self.amount_input.text())
            category = self.category_input.text()
            if not category:
                raise ValueError("Category cannot be empty.")
            
            add_expense(amount, category)
            self.amount_input.clear()
            self.category_input.clear()
            QMessageBox.information(self, "Success", "Expense added successfully!")
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Invalid input: {e}")
            
            
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
            
        QMessageBox.information(
            self,
            "Monthly Report",
            f"Total Income: {report["total_income"]}\nTotal Expense: {report["total_expense"]}",
        )
    
    
def add_income(amount, category):
    income = {"amount": amount, "category": category, "date": datetime.datetime.now()}
    incomes_collection.insert_one(income)
    
    
def add_expense(amount, category):
    expense = {"amount": amount, "category": category, "date": datetime.datetime.now()}
    expenses_collection.insert_one(expense)
    
    
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