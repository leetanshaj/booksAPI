from flask import jsonify, request
import pymongo
from pymongo import MongoClient
from errorCodes import *
import os
# from app import app
# import sys
# sys.path.append('/Users/anshajgoyal/Documents/GitHub/booksAPI')
# from app import app
# from login import *
# sys.path.pop()
from login import UserVerification
from books import Books

class User:

    def __init__(self):
        self.client = MongoClient(app.config['MONGO_URI'])
        self.UserVerification = UserVerification()
        self.Books = Books()
        return

    def signup(self):
        print(request.form)
        compulsoryDetails = {
                    "email": request.json.get('email',None),
                    # "phone": request.json.get('phone',None),
                    "fname": request.json.get('fname',None),
                    "password": request.json.get('password',None),
                    "gender": request.json.get('gender', None)
            }
        phoneNumber = request.json.get('phone',None)
        compulsoryDetails['phone'] = None if phoneNumber==None else str(phoneNumber)
        if not all(compulsoryDetails.values()):
            return E13
        compulsoryDetails.update({"mname": request.json.get('mname',"None"),
                                  "lname": request.json.get('lname',"None"),
                                  "dob"  : request.json.get("dob", "None")
                                  })
        print(compulsoryDetails)
        if not all(list(map(lambda x: isinstance(x, str), list(compulsoryDetails.values())))):
            return E15
        if not all([self.UserVerification.phoneNumberValidator(phoneNumber), len(str(phoneNumber))==10], self.UserVerification.genderVerify(details['gender'])):
            return E14
        if not (compulsoryDetails['dob']!="None" and self.UserVerification.dobVerify(compulsoryDetails['dob'])):
            return E22
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
        if not all(list(map(str, list(compulsoryDetails.values())))):
            return E13        
        if not all([isinstance(compulsoryDetails['sign'],str), isinstance(compulsoryDetails['otp'], str), isinstance(compulsoryDetails['phone'],str)]):
            print(compulsoryDetails)
            return E15
        if not all([self.UserVerification.phoneNumberValidator(compulsoryDetails['phone']), len(str(compulsoryDetails['phone']))==10]):
            return E14
        if not self.UserVerification.insert_otp_db.find_one({"phone":compulsoryDetails['phone']}):
            return E6
        return self.UserVerification.verifyOTP(compulsoryDetails)
    
    
    def login(self):
        email = request.json.get('email',None)
        phoneNumber = request.json.get('phone',None)
        password = request.json.get('password',None)
        if not ((email or phoneNumber) and password):
            return E13
        if isinstance(password, str):
            if email and isinstance(email, str):
                return self.UserVerification.login(password, email.upper())
            elif phoneNumber and isinstance(phoneNumber, str):
                return self.UserVerification.login(password, password = password)
            else:
                return E15
        else: return E15
        
    def private(self):
        token = request.headers.get('AUTHORIZATION', None)
        if not token: return E16
        if not (isinstance(token, str)): print(71);return E17
        if not self.UserVerification.checkValidJwt(token): print(72);return E17
        active = self.UserVerification.checkActiveSession(token)
        if not active: return E18
        E19.update(active)
        return E19

    def logout(self, current_user):
        return self.UserVerification.deleteSession(current_user)


    def insertBook(self):
        if not request.json: return E25
        get = request.json.get
        keys = {str:["bookName" ,"authorNames"] ,int: ["MRP" ,"rental" ,"securityDeposit" ,"timePeriod" ,"qtyAvailable" ],dict :["otherDetails"]}
        data = {j: get(j, None) for i in keys for j in keys[i]}
        # return data
        # print(data.values())
        if not all(data.values()): return E13
        # locals().update(data)
        # print(locals())
        # print(bookName)
        for i in keys:
            # print(i)
            if not all(map(lambda x: isinstance(data[x], i), keys[i])):
                return E15
        return self.Books.insertBook(data)
        # if not all(map(lambda x: isinstance(exec(x), str), keys['str']) or map(lambda x: isinstance(exec(x), int), keys['int'])): return E15
        

        
        # bookName: str, 
        # authorNames: str, 
        # bookPriceInMRP: int, 
        # rentalPrice: int, 
        # securityDeposit: int, 
        # timePeriod: int, 
        # qtyAvailable: int, 
        # details: dict
            
if __name__ != "__main__":
    from app import app
