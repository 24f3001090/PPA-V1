from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class Skill(db.Model):
    __tablename__ = 'skill'
    s_id = db.Column(db.Integer(), primary_key = True, unique = True, autoincrement = True)
    def skill_id(self):
        return f"D{self.s_id}"
    name = db.Column(db.String(100), nullable = False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.d_id'), nullable=False)

class Application(db.Model):
    __tablename__ = 'application'
    a_id = db.Column(db.Integer(), primary_key = True, unique = True, autoincrement = True)
    def application_id(self):
        return f"D{self.a_id}"
    student_id = db.Column(db.Integer, db.ForeignKey('student.s_id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.d_id'), nullable=False)

class Drive(db.Model):
    __tablename__ = 'drive'
    d_id = db.Column(db.Integer(), primary_key = True, unique = True, autoincrement = True)
    def drive_id(self):
        return f"D{self.d_id}"
    role = db.Column(db.String(100), nullable = False)
    package = db.Column(db.String(100), nullable = False)
    experience =  db.Column(db.String(100), nullable = False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.c_id'), nullable=False)
    skills = db.relationship('Skill', backref = 'drive', lazy = True)
    applications = db.relationship('Application', backref = 'drive', lazy = True)

class Student(db.Model):
    __tablename__ = 'student'
    s_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    def student_id(self):
        return f"S{self.s_id}"
    email = db.Column(db.String(200), unique = True, nullable = False)
    name = db.Column(db.String(200), nullable = False)
    password = db.Column(db.String(20), nullable = False)
    level = db.Column(db.String(10), nullable = False)
    blacklisted = db.Column(db.Boolean, default=False)
    application = db.relationship('Application', backref = 'applicant', lazy = True)
    resume = db.Column(db.String(200), nullable = False)
    
class Company(db.Model):
    __tablename__ = 'company'
    c_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    @property
    def company_id(self):
        return f"C{self.c_id}"
    email = db.Column(db.String(200), unique = True, nullable = False)
    name = db.Column(db.String(200), nullable = False)
    password = db.Column(db.String(20), nullable = False)
    status = db.Column(db.String(20), nullable = False)
    blacklisted = db.Column(db.Boolean, default=False)
    drives = db.relationship('Drive', backref = 'company', lazy = True)

    






    