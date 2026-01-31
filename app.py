from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "saarthi_ultra_secret_key" # Change this for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saarthi.db'
db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class Citizen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    mobile = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(200))

class GovOfficial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    gov_id = db.Column(db.String(50), unique=True)
    dept = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

# Create Database
with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        role = request.form.get('role')
        password = request.form.get('password')
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')

        if role == 'user':
            new_user = Citizen(
                fullname=request.form.get('fullname'),
                mobile=request.form.get('mobile'),
                email=request.form.get('email'),
                password=hashed_pw
            )
        else:
            new_user = GovOfficial(
                fullname=request.form.get('gov_name'),
                gov_id=request.form.get('gov_id'),
                dept=request.form.get('dept'),
                email=request.form.get('gov_email'),
                password=hashed_pw
            )
        
        db.session.add(new_user)
        db.session.commit()
        flash("Registration Successful! Please Login.")
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('username') # This is Email or Mobile
        password = request.form.get('password')

        user = None
        if role == 'user':
            # Check Citizen Table by Mobile or Email
            user = Citizen.query.filter((Citizen.mobile == username) | (Citizen.email == username)).first()
        else:
            # Check Gov Table by Email or Gov ID
            user = GovOfficial.query.filter((GovOfficial.email == username) | (GovOfficial.gov_id == username)).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = role
            session['name'] = user.fullname
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Credentials. Try again.")
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session['role'] == 'user':
        return render_template('user_dashboard.html', name=session['name'])
    else:
        return render_template('gov_dashboard.html', name=session['name'])


# Track Status Route
@app.route('/track')
def track():
    return render_template('track.html')

# Explore Schemes
@app.route('/scheme')
def scheme():
    return render_template('scheme.html')

# Form Routes
@app.route('/form')
def form():
    return render_template('form.html')

# 3. Saarthi Connect Route
@app.route('/connect')
def connect():
    return render_template('connect.html')

# 4. Post/Plus Route
@app.route('/post')
def post():
    return render_template('post.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)