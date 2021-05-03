from flask import Flask
from pymongo import MongoClient
from twilio.rest import Client
from errorCodes import *
import hashlib
import re
import bson
def md5(string):
	kk=hashlib.md5(str(string).encode())
	return kk.hexdigest()

if __name__ != '__main__':
    from app import app
    app.config['MONGO_DBNAME'] = 'Cluster0'
    app.config['MONGO_URI'] = 'mongodb+srv://anshaj:anshaj123@testbook.ut1ij.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
    app.config['TWILIO_ACCOUNT_SID'] = 'AC0992ac9ab87933946c013431328a1456'
    app.config['TWILIO_AUTH_TOKEN'] = '014ed5e8efa4347ed9964ca3125695e1'
    app.config['sms_limit'] = 3
    app.config['signature'] = md5
    app.config['signupDB'] = 'signup'
    app.config['insertOTPAcct'] = 'insertOTPAcct'


class UserVerification:

    def __init__(self):
        account_sid = app.config['TWILIO_ACCOUNT_SID']
        auth_token = app.config['TWILIO_AUTH_TOKEN']
        client = Client(account_sid, auth_token)
        service = client.verify.services.create(friendly_name='Book My Book')
        app.config['smsSID'] = service._properties['sid']
        self.dayLimit = {}
        self.client = client
        self.db = MongoClient(app.config['MONGO_URI'])
        dbName = app.config['insertOTPAcct']
        self.insert_otp_db = self.db[dbName][dbName]
        dbName = app.config['signupDB']
        self.signup_db = self.db[dbName][dbName]

    def sendOtp(self,details: dict):
        client = self.client
        sid = app.config['smsSID']
        signature = app.config['signature']
        mobileNumber = details['phone']
        if self.dayLimit.get(mobileNumber) == None:
            self.dayLimit[mobileNumber] = {'count':1, 'signature' : signature(mobileNumber)}
            self.insertOTPacct(details)
            E = E2
        else:
            if self.dayLimit[mobileNumber]['count'] >= app.config['sms_limit']:
                return E1
            self.dayLimit[mobileNumber]['count']+=1
            E = E5
        try:
            verification = client.verify.services(sid).verifications.create(to= f'+91{mobileNumber}', channel='sms')
        except Exception as e:
            print(e) 
        return signature(mobileNumber), E


    def verifyOTP(self,compulsoryDetails):
        mobileNumber = compulsoryDetails['phone']
        signature = compulsoryDetails['sign']
        OTP = compulsoryDetails['otp']
        client = self.client
        sid = app.config['smsSID']
        print(self.dayLimit)
        if self.dayLimit.get(mobileNumber) == None:
            return E6
        if self.dayLimit.get(mobileNumber)['signature'] != signature:
            return E7
        try:
            verification_check = client.verify.services(sid).verification_checks.create(to = f'+91{mobileNumber}', code = OTP)
            if verification_check._properties['valid']:
                del self.dayLimit[mobileNumber]
                details = self.insert_otp_db.find_one_and_delete({"phone": mobileNumber})
                details['verified'] = True
                self.signup_db.insert(details)
                del details['_id']
                return details
            else:
                return E4
        except Exception as e:
            print(e)
            return EXE
    
    def insertOTPacct(self,details):
        db = self.insert_otp_db
        userId = str(db.insert(details))
        details.update({"userId": userId})
        # del details['password']
        return details



    def acctExists(self, email: str, mobileNumber: int):
        db = self.signup_db
        if db.find_one({"email":email.upper()}):
            if db.find_one({"email":email.upper(), "phone": mobileNumber}):
                return E9
            else:
                return E10
        elif db.find_one({"phone": mobileNumber}):
            return E11
        else:
            return E12
    
    def phoneNumberValidator(self, mobileNumber: str):
        regex = re.compile(r'(\b^[9876]\d{9}$)')
        if regex.match(str(mobileNumber)) == None:
            return False
        else:
            return True

    def createAccount(self, details: dict):
        signature = app.config['signature']
        email = details['email'].upper()
        password = signature(details['password'].upper())
        phone = int(details['phone'])
        otpVerified = False
        details.update({"email":email, "password":password, "phone": phone, "verified": otpVerified})
        return self.sendOtp(details)
        
        
    


    
    
