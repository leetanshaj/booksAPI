from pymongo import MongoClient
import time
from flask_login import current_user
if __name__ != '__main__':
    from app import app
import bson
from errorCodes import *
class Books:

    def __init__(self):
        app.config['authorsDB'] = 'authors'
        app.config['booksDB'] = 'books'
        self.db = MongoClient(app.config['MONGO_URI'])
        self.books = self.db[app.config['booksDB']][app.config['booksDB']]
        self.authors = self.db[app.config['authorsDB']][app.config['authorsDB']]
    
    def insertBook(self, data):
        authors = data["authorNames"].split(",")
        userId = current_user.userId['userId']
        print(userId)
        for authorName in authors:
            author = Author(self.authors, authorName)
            author.insert_author()
            structure = {   "bookName": data['bookName'],
                            "authorName": author.authorName,
                            "authorId": author.authorId,
                            "MRP": data['MRP'],
                            "rental": data['rental'],
                            "securityDeposit": data['securityDeposit'],
                            "timePeriod" : data["timePeriod"],
                            "qtyAvailable": data['qtyAvailable'],
                            "seller": userId,
                            "otherdata": data['otherDetails'], #Book_Images #description #any other message for user'] 
                            "timestamp":time.time()
                        }
            self.books.insert_one(structure)
            del structure['authorId']
            del structure['authorName']
            structure['bookId'] = str(structure['_id'])
            author.insertBooksInAuthor(structure['_id'])
            del structure['_id']
            print(structure)
            return structure
    
    # def find


class Author:

    def __init__(self, authorDB, authorName = None, authorId = None):
        self.authorDB = authorDB
        result = self.authorDB.find_one({"$or": [{"AUTHOR_NAME": authorName}, {"_id": bson.ObjectId(authorId)}]})
        if result:
            self.exist = True
            self.authorId = result['_id']
            self.authorName = result['AUTHOR_NAME']
            self.books = result['books']
        else:
            self.exist = False
            self.authorId = None
            self.authorName = authorName
            self.books = []

    def existing(self):
        return self.exist
    
    def insert_author(self):
        if (not self.exist) and isinstance(self.authorName, str):
            structure = {"AUTHOR_NAME": self.authorName, "books": self.books}
            self.authorDB.insert(structure)
            self.authorId = structure['_id']
            self.exist = True
        else:
            return E24 if self.exist else E15
    
    def insertBooksInAuthor(self, bookId):
        if (not self.exist):
            self.insert_author()
        self.authorDB.find_one_and_update({"_id": self.authorId},
        {"$push": 
            {"books": {
                "$each": [str(bookId)]
                }
            }
        })
    



    
