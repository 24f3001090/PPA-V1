import os
from flask import Flask, render_template, request, redirect, session
from dbmodel import db, Student as st, Company as com

app = Flask(__name__)

app.secret_key = "your_secret_key_here"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db.init_app(app)

with app.app_context():
    amazon = com.query.filter_by(name = 'Amazon')
    db.create_all()

#Last year highest placement stats
place_data = [{"sno":1,"name":"Bipin Tiwari", "company":"Google", "package":"45LPA"},
              {"sno":2,"name":"Dewashish Tikas", "company":"Google", "package":"42LPA"},
              {"sno":3,"name":"Devishi Jain", "company":"TCS", "package":"35LPA"},
              {"sno":4,"name":"Deepesh Gupta", "company":"Google", "package":"30LPA"},
              {"sno":5,"name":"Om Pandey", "company":"Amazon", "package":"30LPA"},
              {"sno":6,"name":"Yashvi Upadhyay", "company":"Google", "package":"25LPA"},
              {"sno":7,"name":"Mayank Kushwaha", "company":"Amazon", "package":"24LPA"},
              {"sno":8,"name":"Ilesha Shrivastava", "company":"Microsoft", "package":"20LPA"},
              {"sno":9,"name":"Jeeveash Kumar", "company":"Infosys", "package":"18LPA"},
              {"sno":10,"name":"Aayushmaan Patel", "company":"Google", "package":"18LPA"}]

@app.route("/")
def main_page():
    return render_template("index.html", place_data = place_data)

@app.route("/register", methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        level = request.form.get('level')
        role = request.form.get('role')
        file = request.files.get('resume') 


        if not request.form.get('declaration'):
            return render_template("registrationpage.html", error="Please accept the declaration")
        
        # Is it a Student?
        if role == 'student':
            checkStudent = st.query.filter_by(email=email).first()
            if checkStudent:
                return render_template("registrationpage.html", error = 'Email already registered')
            else:
                if name and email and password and level and role and file and file.filename != '':
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(filepath)
                    student= st(name=name, password=password, email=email, level=level, resume=filepath)
                    db.session.add(student)
                    db.session.commit()
                    return redirect("/login")
                else:
                    print(name, email, password, level, role, file)
                    return render_template("registrationpage.html")
            
        # Is it a Company?    
        else:
            checkCompany = com.query.filter_by(email=email).first()
            if checkCompany:
                return render_template("registrationpage.html", error = 'Email already registered')
            else:
                if name and email and password and role:
                    company = com(name=name, password=password, email=email, status = 'pending')
                    db.session.add(company)
                    db.session.commit()
                    st.query.all()
                    return redirect("/login")
                else:
                    return render_template("registrationpage.html")
    else:
        return render_template("registrationpage.html")

@app.route("/login", methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        #Is it a student?
        checkStudent = st.query.filter_by(email=email).first()
        if checkStudent:
            if checkStudent.password == password:
                return render_template("userdashboard.html", name=checkStudent.name)
            else:
                return render_template("loginpage.html")
        #Is it a company?
        checkCompany = com.query.filter_by(email=email).first()
        if checkCompany:
            if checkCompany.status == 'approved' and checkCompany.password == password:
                return render_template("comdashboard.html", name=checkCompany.name)
            else:
                return render_template("loginpage.html", error = "Either company not registered or wrong password.")
            

        #Is it admin?
        if email == 'admin@tenacious.com' and password == "superior":
            session['user'] = 'admin'
            return redirect("/administrator")
        else:
            return render_template("loginpage.html")
    else:
        return render_template("loginpage.html")

@app.route("/administrator")
def admin():
    if session.get('user') != 'admin':
        return redirect("/login")
    pending_reg = com.query.filter_by(status = 'pending')
    return render_template("admindashboard.html", pending_reg = pending_reg)

@app.route("/company")
def company():
    return render_template("comdashboard.html")

if __name__ == "__main__":
    app.run(debug=True)