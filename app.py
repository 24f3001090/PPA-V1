import os
from flask import Flask, render_template, request, redirect, session, url_for
from dbmodel import db, Student as st, Company as com, Drive as dr, Skill as sk, Application as apl
from datetime import datetime

app = Flask(__name__)

app.secret_key = "bipin"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db.init_app(app)

with app.app_context():
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
        cgpa = request.form.get('cgpa')


        if not request.form.get('declaration'):
            return render_template("registrationpage.html", error="Please accept the declaration")
        
        # Is it a Student?
        if role == 'student':
            checkStudent = st.query.filter_by(email=email).first()
            if checkStudent:
                return render_template("registrationpage.html", error = 'Email already registered')
            else:
                if name and email and password and level and cgpa and role and file and file.filename != '':
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(filepath)
                    student= st(name=name, password=password, email=email, level=level, resume=file.filename, cgpa = cgpa)
                    db.session.add(student)
                    db.session.commit()
                    return redirect("/login")
                else:
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
                session['user'] = 'student'
                session['student_id'] = checkStudent.s_id
                s_id = checkStudent.s_id
                return redirect(url_for("student", id = s_id))
            else:
                return render_template("loginpage.html")
        #Is it a company?
        checkCompany = com.query.filter_by(email=email).first()
        if checkCompany:
            if checkCompany.status == 'approved' and checkCompany.password == password:
                session['user'] = 'company'
                session['company_id'] = checkCompany.c_id
                c_id = checkCompany.c_id
                return redirect(url_for("company", id = c_id))
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

@app.route("/administrator", methods = ['GET', 'POST'])
def admin():
    if session.get('user') != 'admin':
        return redirect("/login")
    if request.method == 'POST':
        approval = request.form.get('approval')
        com_id = request.form.get('com_id')

        company = com.query.get(com_id)
        if company:
            if approval == 'yes':
                company.status = 'approved'
        else:
            company.status = 'rejected'
        db.session.commit()

    pending_reg = com.query.filter_by(status = 'pending')
    return render_template("admindashboard.html", pending_reg = pending_reg)

@app.route("/company/<int:id>")
def company(id):
    if session.get('user') != 'company':
        return redirect("/login")
    if session.get('company_id') != id:
        return "Unauthorized access"
    company = com.query.get(id)
    return render_template("comdashboard.html", company = company)

@app.route("/company/all-drives/<int:com_id>")
def com_drives(com_id):
    company = com.query.get(com_id)
    drives = company.drives
    return render_template("comdrives.html", drives = drives)

@app.route("/company/drive/<int:com_id>", methods=['GET', 'POST'])
def drive(com_id):
    if request.method == 'POST':
        role = request.form.get('role')
        package = request.form.get('package')
        experience = request.form.get('experience')

        if role and package and experience:
            drive = dr(role = role, package = package, experience = experience, status = 'active', company_id = com_id)
            db.session.add(drive)
            db.session.commit()
            id = drive.d_id
            return redirect(url_for("edit", id = id))
        else:
            return render_template("createdrive.html", error = "All fields are mandatory.")
    else:
        return render_template("createdrive.html")

@app.route("/company/drive/edit/<int:id>", methods = ['GET', 'POST'])
def edit(id):
    drive = dr.query.get(id)
    if request.method == 'POST':
        skill = request.form.get('skill')
        status = request.form.get('status')
        if status:
            if status == 'closed':
                drive.status = 'closed'
            else:
                drive.status = 'active'
        if skill:
            new_skill = sk(name = skill, drive_id = id)
            db.session.add(new_skill)

        db.session.commit()
        return redirect(url_for("edit", id = id))
        
    return render_template("driveupdate.html", drive = drive)

@app.route("/student/<int:id>")
def student(id):
    if session.get('user') != 'student':
        return redirect("/login")
    if session.get('student_id') != id:
        return "Unauthorized access"
    student = st.query.get(id)
    return render_template("stdashboard.html", student = student)

@app.route("/student/all-drives/<int:st_id>")
def st_drives(st_id):
    drives = dr.query.filter_by(status = 'active')
    return render_template("stdrives.html", drives = drives, st_id = st_id)

@app.route("/student/apply/<int:st_id>/<int:drive_id>", methods=['GET', 'POST'])
def apply(st_id, drive_id):
    drive = dr.query.get(drive_id)
    existing_application = apl.query.filter_by(student_id=st_id, drive_id=drive_id).first()
    if request.method == 'POST':
        declaration = request.form.get('declaration')
        apply = request.form.get('apply')
        if declaration and apply:
            application = apl(status = 'applied', student_id = st_id, drive_id = drive_id)
            db.session.add(application)
            db.session.commit()
            return redirect(url_for("apply", st_id = st_id, drive_id = drive_id))
    return render_template("apply.html", drive = drive, applied_already = existing_application)

@app.route("/company/applications/<int:com_id>")
def applications(com_id):
    company = com.query.get(com_id)
    drives = company.drives
    j_apps = []
    for drive in drives:
        j_apps.extend(drive.applications)
    return render_template("comapplications.html", j_apps = j_apps)

@app.route("/company/applications/view/<int:app_id>", methods = ['GET', 'POST'])
def view_st_application(app_id):
    j_app = apl.query.get(app_id)
    if request.method == 'POST':
        approval = request.form.get('approval')
        sch_date = request.form.get('sch_date')
        interview = request.form.get('interview')
        select = request.form.get('select')

        if approval:
            if approval == 'yes':
                j_app.status = 'shortlisted'
            else:
                j_app.status == 'rejected'
        
        if sch_date and interview:
                j_app.status = 'interview scheduled'
                j_app.int_date = datetime.strptime(sch_date, "%Y-%m-%d").date()

        if select:
            j_app.status = 'selected'

        db.session.commit()
        return redirect (url_for('view_st_application', app_id = app_id))

    return render_template("comapplicationview.html", j_app = j_app)

@app.route("/student/applications/<int:st_id>")
def st_applications(st_id):
    student = st.query.get(st_id)
    j_apps = student.applications
    return render_template("stapplications.html", j_apps = j_apps)

@app.route("/student/applications/track/<int:app_id>")
def track(app_id):
    j_app = apl.query.get(app_id)
    return render_template("track.html", j_app = j_app)


if __name__ == "__main__":
    app.run(debug=True)