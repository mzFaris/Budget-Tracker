from pymongo import MongoClient
import datetime


client = MongoClient("mongodb://localhost:27017")
db = client["financeApp"]
incomes_collection = db["incomes"]
expenses_collection = db["expenses"]
categories_collection = db["categories"]


def main():
    ...
    
    
if __name__ == "__main__":
    main()