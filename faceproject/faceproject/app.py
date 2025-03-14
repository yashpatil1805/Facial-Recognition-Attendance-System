from flask import Flask
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object('config.Config')

app.config['UPLOAD_FOLDER'] = 'uploads/'  # Directory to save uploaded images
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
mysql = MySQL(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
