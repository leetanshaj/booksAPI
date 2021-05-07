from flask import Flask, make_response
from flask_login import LoginManager, login_required, current_user
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
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

@app.route('/login', methods=['POST'])
def login():
    return m.login()


@login_manager.request_loader
def request_loader(request):
    print("Checkerrrrrr")
    token = request.headers.get('Authorization')
    if token: 
        user = m.UserVerification.checkActiveSession(token)
        if user: return user
    return None

@app.route('/private')
@login_required
def prive():
    print('Check')
    # print(current_user.__dict__)
    # r = current_user.__dict__
    # del r['_id']
    # return r
    return {"erro": 1}
    # return m.private()

@app.route('/logout')
@login_required
def logout():
    return m.logout(current_user)


@app.route('/addBook', methods = ['POST'])
@login_required
def insertbook():
    return m.insertBook()

if __name__ == "__main__":
    m = models.User()
    import os
    app.run(debug=True)
    print(m)
    os.system('clear')