from flask import Flask, Response
from pymongo import MongoClient
from twilio.rest import Client
from errorCodes import *
import hashlib
import re
import bson
import jwt
from uuid import uuid1
import time
def md5(string):
	kk=hashlib.md5(str(string).encode())
	return kk.hexdigest()

if __name__ != '__main__':
    from app import app
    app.config['MONGO_DBNAME'] = 'Cluster0'
    app.config['MONGO_URI'] = 'mongodb+srv://anshaj:anshaj123@testbook.ut1ij.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
    # import tests
    app.config['TWILIO_ACCOUNT_SID'] = 'AC0992ac9ab87933946c013431328a1456'
    app.config['TWILIO_AUTH_TOKEN'] = '014ed5e8efa4347ed9964ca3125695e1'
    app.config['sms_limit'] = 3
    app.config['signature'] = md5
    app.config['signupDB'] = 'signup'
    app.config['insertOTPAcctDB'] = 'insertOTPAcct'
    app.config['activeSessionsDB'] = 'activeSessions'

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
        dbName = app.config['insertOTPAcctDB']
        self.insert_otp_db = self.db[dbName][dbName]
        dbName = app.config['signupDB']
        self.signup_db = self.db[dbName][dbName]
        dbName = app.config['activeSessionsDB']
        self.activeSessions = self.db[dbName][dbName]

    def sendOtp(self,details: dict):
        client = self.client
        sid = app.config['smsSID']
        signature = app.config['signature']
        mobileNumber = details['phone']
        if self.dayLimit.get(mobileNumber) == None:
            self.dayLimit[mobileNumber] = {'count':1, 'signature' : signature(mobileNumber)}
            details['timestamp'] = time.time()
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
                return self.registerAccountinDB(mobileNumber)
            else:
                return E4
        except Exception as e:
            print(e)
            return EXE
    
    def registerAccountinDB(self,mobileNumber):
        del self.dayLimit[mobileNumber]
        details = self.insert_otp_db.find_one_and_delete({"phone": mobileNumber})
        details['verified'] = True
        details['timestamp'] = time.time()
        self.signup_db.insert(details)
        details['userId'] = str(details.pop('_id'))
        token = self.createjwtToken(details['userId'])
        details['activeSessions'] = [token]
        self.activeSessions.insert(details)
        del details['_id']
        del details['activeSessions']
        details['auth'] = token
        return details


    def insertOTPacct(self,details):
        db = self.insert_otp_db
        userId = str(db.insert(details))
        details.update({"userId": userId})
        return details

    def genderVerify(self, gender):
        if gender.upper() not in ['MALE', 'FEMALE', 'NA']:
            return False
        return True
    
    def dobVerify(self, dob):
        regex = re.compile('^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$')
        if regex.match(dob) is not None:
            return True
        return False
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

    def createjwtToken(self, userId):
        secretKey = app.config['SECRET_KEY']
        encoded = jwt.encode({'userId': userId, 'guid': str(uuid1())}, secretKey, algorithm='HS256').decode()
        return encoded
    
    def checkValidJwt(self, token):
        secretKey = app.config['SECRET_KEY']
        print(secretKey)
        try:
            valid = bool(jwt.decode(token, key = secretKey, verify = True))
        except jwt.exceptions.InvalidSignatureError:
            print("Invalid Sign")
            valid = False
        return valid
    
    def checkActiveSession(self, token):
        userId = self.activeSessions.find_one({"activeSessions": token})
        if userId:
            return User(True, userId, token)
        return False
    
    
    def login(self, password, email = None, phoneNumber = None):
        query = {"email":email} if email else {"phone": phoneNumber}
        result = self.signup_db.find_one(query)
        print(result)
        if not result: return E20
        if password != result['password']: return E21
        token = self.createjwtToken(str(result['_id']))
        json = self.activeSessions.find_one_and_update(query, {"$push":{"activeSessions":token}})
        query['fname'] = json['fname']
        query['auth'] = token
        query['userId'] = json['userId']
        return query

    def deleteSession(self, current_user):
        token = current_user.token
        self.activeSessions.find_one_and_update({"activeSessions":token}, {"$pull":{"activeSessions":token}})
        return E23

class User:
    def __init__(self, isauthenticated, userId, token):
        self.isauthenticated = isauthenticated
        self.userId = userId
        self.token = token
    def is_authenticated(self):
        return self.isauthenticated
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.userId
    def auth(self, auth):
        return self.token






        
        
    


    
    
