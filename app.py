from flask import Flask
app = Flask(__name__)
if __name__ == '__main__':
    import models
    import login
    

app.config['SECRET_KEY'] = "V1"
@app.route('/signup', methods = ['POST'])
def signup():
    return m.signup()

@app.route('/verify', methods = ['POST'])
def verify():
    return m.otpverify()

# u = models.User()
# print(u)

if __name__ == "__main__":
    m = models.User()
    app.run(debug=True)
    print(m)