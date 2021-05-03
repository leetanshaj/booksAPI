from flask import jsonify, request
import pymongo
from pymongo import MongoClient
from errorCodes import *
# from app import app
# import sys
# sys.path.append('/Users/anshajgoyal/Documents/GitHub/booksAPI')
# from app import app
# from login import *
# sys.path.pop()
from login import UserVerification

class User:

    def __init__(self):
        self.client = MongoClient(app.config['MONGO_URI'])
        self.UserVerification = UserVerification()
        return

    def signup(self):
        print(request.form)
        # with app.app_context():
        compulsoryDetails = {
                    "email": request.form.get('email',None),
                    "phone": request.form.get('phone',None),
                    "fname": request.form.get('fname',None),
                    "password": request.form.get('password',None)
            }
        if not all(compulsoryDetails.values()):
            return E13
        compulsoryDetails.update({"mname": request.form.get('mname',"None"),
                    "lname": request.form.get('lname',"None")})
        print(compulsoryDetails)
        # if not isinstance(compulsoryDetails['phone'],int):
            # return E15
        phoneNumber = compulsoryDetails['phone']
        # del compulsoryDetails['phone']
        if not all(list(map(lambda x: isinstance(x, str), list(compulsoryDetails.values())))):
            return E15
        compulsoryDetails['phone'] = phoneNumber
        if not all([self.UserVerification.phoneNumberValidator(phoneNumber), len(str(phoneNumber))==10]):
            return E14
        existing = self.UserVerification.acctExists(compulsoryDetails['email'], phoneNumber)
        if existing[0]:
            return existing[1]
        return self.UserVerification.createAccount(compulsoryDetails)

    def otpverify(self):
        compulsoryDetails = {
                    "phone": request.json.get('phone',None),
                    "sign": request.json.get('signature',None),
                    "otp": request.json.get('otp',None)
            }
        # phoneNumber = compulsoryDetails['ph']
        if not all(list(map(str, list(compulsoryDetails.values())))):
            return E13        
        if not all([isinstance(compulsoryDetails['sign'],str), isinstance(compulsoryDetails['otp'], str), isinstance(compulsoryDetails['phone'],int)]):
            print(compulsoryDetails)
            return E15
        if not all([self.UserVerification.phoneNumberValidator(compulsoryDetails['phone']), len(str(compulsoryDetails['phone']))==10]):
            return E14
        if not self.UserVerification.insert_otp_db.find_one({"phone":compulsoryDetails['phone']}):
            return E6
        return self.UserVerification.verifyOTP(compulsoryDetails)

        
            
if __name__ != "__main__":
    from app import app
