from pymongo import MongoClient
from app import app
client = MongoClient(app.config['MONGO_URI'])
# client.signup.signup.drop()
# client.signup.signup.drop()
# client.insertOTPAcct.insertOTPAcct.drop()
# client.activeSessions.activeSessions.drop()
client.authors.authors.drop()
client.books.books.drop()
print("Dropped All")