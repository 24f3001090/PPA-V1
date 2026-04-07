import os
from flask import Flask, render_template, request, redirect, session, url_for
from dbmodel import db, Student as st, Company as com, Drive as dr, Skill as sk, Application as apl

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

#Skills
skills = [
    # Core Programming
    'Python', 'Java', 'C', 'C++', 'JavaScript',

    # Web Development
    'HTML', 'CSS', 'Bootstrap', 'Tailwind CSS',
    'Flask', 'Django', 'FastAPI', 'Spring', 'Spring Boot',
    'REST API Development',

    # Databases
    'SQL', 'MySQL', 'PostgreSQL', 'SQLite', 'MongoDB',

    # Tools & Technologies
    'Git', 'GitHub', 'VS Code', 'Linux', 'Docker',

    # Data Science / AI (your branch 👀)
    'NumPy', 'Pandas', 'Matplotlib', 'Seaborn',
    'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch',
    'Data Analysis', 'Data Visualization',

    # Computer Science Fundamentals
    'Data Structures', 'Algorithms', 'OOP',
    'Operating Systems', 'Computer Networks', 'DBMS',

    # Software Engineering Practices
    'Debugging', 'Testing', 'Version Control',
    'API Integration', 'System Design (Basics)',

    # Other Engineering Skills
    'Problem Solving', 'Analytical Thinking',
    'Mathematics', 'Statistics',

    # Soft Skills
    'Communication', 'Leadership', 'Management',
    'Teamwork', 'Time Management', 'Adaptability'

    # Mechanical
    'AutoCAD', 'SolidWorks', 'CATIA',
    'ANSYS', 'Finite Element Analysis (FEA)',
    'Thermodynamics', 'Fluid Mechanics',
    'Heat Transfer', 'Machine Design',
    'CNC Programming', 'Manufacturing Processes',
    'Robotics', '3D Printing'

    # Civil
    'AutoCAD Civil', 'STAAD Pro', 'ETABS',
    'Structural Analysis', 'Geotechnical Engineering',
    'Surveying', 'Construction Management',
    'Soil Mechanics', 'Concrete Technology',
    'Transportation Engineering', 'Environmental Engineering'

    # Electrical
    'MATLAB', 'Simulink',
    'Circuit Design', 'Power Systems',
    'Control Systems', 'Signal Processing',
    'PLC Programming', 'SCADA',
    'Embedded Systems', 'Microcontrollers (Arduino, ESP32)',
    'Power Electronics', 'Electrical Machines'
]

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

@app.route("/company/drive/<int:com_id>", methods=['GET', 'POST'])
def drive(com_id):
    if request.method == 'POST':
        role = request.form.get('role')
        package = request.form.get('package')
        experience = request.form.get('experience')

        if role and package and experience:
            drive = dr(role = role, package = package, experience = experience, company_id = com_id)
            db.session.add(drive)
            db.session.commit()
            id = drive.d_id
            return redirect(url_for("edit", id = id))
        else:
            return render_template("drive.html", error = "All fields are mandatory.")
    else:
        return render_template("drive.html")

@app.route("/company/drive/edit/<int:id>", methods = ['GET', 'POST'])
def edit(id):
    drive = dr.query.get(id)
    if request.method == 'POST':
        skill = request.form.get('skill')
        if skill:
            new_skill = sk(name = skill, drive_id = id)
            db.session.add(new_skill)
            db.session.commit()
            return redirect(url_for("edit", id = id))
        else:
            return redirect(url_for("edit", id = id))
        
    return render_template("driveupdate.html", id = id, role = drive.role, package = drive.package, experience = drive.experience, skills = drive.skills)

@app.route("/student/<int:id>")
def student(id):
    if session.get('user') != 'student':
        return redirect("/login")
    if session.get('student_id') != id:
        return "Unauthorized access"
    student = st.query.get(id)
    return render_template("stdashboard.html", student = student)

if __name__ == "__main__":
    app.run(debug=True)