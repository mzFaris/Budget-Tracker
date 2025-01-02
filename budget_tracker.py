from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from pymongo import MongoClient
import datetime
import sys


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
        
        self.amount_input = QLineEdit(self)
        self.category_input = QLineEdit(self)
        
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
        
        self.setLayout(layout)
        self.setWindowTitle("Budget Tracker")
        self.show()
        
    
    def add_income(self):
        amount = float(self.amount_input.text())
        category = self.category_input.text()
        add_income(amount, category)
        self.amount_input.clear()
        self.category_input.clear()
        
        
    def add_expense(self):
        amount = float(self.amount_input.text())
        category = self.category_input.text()
        add_expense(amount, category)
        self.amount_input.clear()
        self.category_input.clear()
    
    
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
    
    return {
        "total_income": list(total_income)[0].get("total", 0) if total_income else 0,
        "total_expense": list(total_expense)[0].get("total", 0) if total_expense else 0,
    }
    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = BudgetTrackerApp()
    sys.exit(app.exec_())