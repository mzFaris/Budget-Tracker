from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from pymongo import MongoClient
import datetime


client = MongoClient("mongodb://localhost:27017")
db = client["financeApp"]
incomes_collection = db["incomes"]
expenses_collection = db["expenses"]
categories_collection = db["categories"]


def main():
    ...
    
    
def add_income(amount, category):
    income = {"amount": amount, "category": category, "date": datetime.datetime.now()}
    incomes_collection.insert_one(income)
    
    
def add_expense(amount, category):
    expense = {"amount": amount, "category": category, "date": datetime.datetime.now()}
    expenses_collection.insert_one(expense)
    
    

    
    
if __name__ == "__main__":
    main()