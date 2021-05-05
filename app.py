from flask import Flask, make_response
app = Flask(__name__)
if __name__ == '__main__':
    import models
    import login
    
    

app.config['SECRET_KEY'] = "V1"




@app.route('/', methods = ['GET'])
def k():
    data = {'he': 'Ansh'}
    headers = {'Access_Key': 'dsfg'}
    return make_response(data, headers)






@app.route('/signup', methods = ['POST'])
def signup():
    return m.signup()

@app.route('/verify', methods = ['POST'])
def verify():
    return m.otpverify()

@app.route('/private', methods = ['POST'])
def prive():
    return m.private()

@app.route('/login', methods=['POST'])
def login():
    return m.login()
# u = models.User()
# print(u)

if __name__ == "__main__":
    m = models.User()
    import os
    app.run(debug=True)
    print(m)
    os.system('clear')