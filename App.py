from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "123456"

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Diseasetype(db.Model):
    __tablename__ = 'diseasetypes'
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(140), nullable = False)
    # Relationships
    diseases = db.relationship('Disease', backref='diseasetypes', lazy=True)
    specializations = db.relationship('Specialize', backref='diseasetypes', passive_deletes='all')

    def __init__ (self, id, description):
        self.id = id
        self.description = description

class Country(db.Model):
    __tablename__ = 'countries'
    cname = db.Column(db.String(50), primary_key = True)
    population = db.Column(db.BIGINT, nullable = False)
    # Relationships
    discoveries = db.relationship('Discovery', backref='countries', passive_deletes='all')
    users = db.relationship('User', backref='countries', passive_deletes='all')
    records = db.relationship('Record', backref='countries', passive_deletes='all')

    def __init__ (self, cname, population):
        self.cname = cname
        self.population = population

class Disease(db.Model):
    __tablename__ = 'diseases'
    disease_code = db.Column(db.String(50), primary_key = True)
    pathogen = db.Column(db.String(20))
    description = db.Column(db.String(140), nullable = False)
    id = db.Column(db.Integer, db.ForeignKey('diseasetypes.id'), nullable = False)
    # Relationships
    discoveries = db.relationship('Discovery', backref='diseases', passive_deletes='all')
    records = db.relationship('Record', backref='diseases', passive_deletes='all')

    def __init__ (self, disease_code, pathogen, description, id):
        self.disease_code = disease_code
        self.pathogen = pathogen
        self.description = description
        self.id = id

class Discovery(db.Model):
    __tablename__ = 'discoveries'
    cname = db.Column(db.String(50), db.ForeignKey('countries.cname'), primary_key=True)
    disease_code = db.Column(db.String(50), db.ForeignKey('diseases.disease_code'), primary_key=True)
    first_enc_date = db.Column(db.Date, nullable = False)

    def __init__ (self, cname, disease_code, first_enc_date):
        self.cname = cname
        self.disease_code = disease_code
        self.first_enc_date = first_enc_date

class User(db.Model):
    __tablename__ = 'users'
    email = db.Column(db.String(60), primary_key = True)
    name = db.Column(db.String(30), nullable = False)
    surname = db.Column(db.String(40), nullable = False)
    salary = db.Column(db.Integer, nullable = False)
    phone = db.Column(db.String(20), nullable = False)
    cname = db.Column(db.String(50), db.ForeignKey('countries.cname'), nullable = False)
    # Relationships
    publicservants = db.relationship('PublicServant', backref='users', passive_deletes='all')
    doctors = db.relationship('Doctor', backref='users', passive_deletes='all')

    def __init__ (self, email, name, surname, salary, phone, cname):
        self.email = email
        self.name = name
        self.surname = surname
        self.salary = salary
        self.phone = phone
        self.cname = cname

class PublicServant(db.Model):
    __tablename__ = 'publicservants'
    email = db.Column(db.String(60), db.ForeignKey('users.email', ondelete='CASCADE'), primary_key = True)
    department = db.Column(db.String(50), nullable = False)
    # Relationships
    records = db.relationship('Record', backref='publicservants', passive_deletes='all')

    def __init__ (self, email, department):
        self.email = email
        self.department = department

class Doctor(db.Model):
    __tablename__ = 'doctors'
    email = db.Column(db.String(60), db.ForeignKey('users.email', ondelete='CASCADE'), primary_key = True)
    degree = db.Column(db.String(20), nullable = False)
    # Relationships
    specializations = db.relationship('Specialize', backref='doctors', passive_deletes='all')

    def __init__ (self, email, degree):
        self.email = email
        self.degree = degree

class Specialize(db.Model):
    __tablename__ = 'specializes'
    id = db.Column(db.Integer, db.ForeignKey('diseasetypes.id', ondelete='CASCADE'), primary_key = True)
    email = db.Column(db.String(60), db.ForeignKey('doctors.email', ondelete='CASCADE'), primary_key = True)

    def __init__ (self, id, email):
        self.id = id
        self.email = email

class Record(db.Model):
    __tablename__ = 'records'
    email = db.Column(db.String(60), db.ForeignKey('publicservants.email', ondelete='CASCADE'), primary_key = True)
    cname = db.Column(db.String(50), db.ForeignKey('countries.cname', ondelete='CASCADE'), primary_key = True)
    disease_code = db.Column(db.String(50), db.ForeignKey('diseases.disease_code', ondelete='CASCADE'), primary_key = True)
    total_deaths = db.Column(db.Integer, nullable = False)
    total_patients = db.Column(db.Integer, nullable = False)

    def __init__ (self, email, cname, disease_code, total_deaths, total_patients):
        self.email = email
        self.cname = cname
        self.disease_code = disease_code
        self.total_deaths = total_deaths
        self.total_patients = total_patients

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")


########################## DISEASE TYPES ##########################

@app.route('/disease_types')
def diseasetypes():
    all_data = Diseasetype.query.all()
    return render_template("disease_types.html", diseasetypes = all_data)

@app.route('/disease_types/insert', methods = ['POST'])
def insert_diseasetype():
    if request.method == 'POST':
        id = request.form['id']
        description = request.form['description']

        data = Diseasetype(id, description)
        db.session.add(data)
        db.session.commit()
        flash("Disease type inserted successfully")
        return redirect(url_for('diseasetypes'))

@app.route('/disease_types/update', methods = ['GET', 'POST'])
def update_diseasetype():
    if request.method == 'POST':
        data = Diseasetype.query.get(request.form.get('id'))
        data.description = request.form['description']
        db.session.commit()
        flash("Disease type updated successfully")
        return redirect(url_for('diseasetypes'))

# @app.route('/disease_types/delete/<id>/', methods = ['GET', 'POST'])
# def delete_diseasetype(id):
#     data = Diseasetype.query.get(id)
#     db.session.delete(data)
#     db.session.commit()
#     flash("Disease type deleted successfully")
#     return redirect(url_for('diseasetypes'))


########################## Countries ##########################

@app.route('/countries')
def countries():
    all_data = Country.query.all()
    return render_template("countries.html", countries = all_data)

@app.route('/countries/insert', methods = ['POST'])
def insert_country():
    if request.method == 'POST':
        cname = request.form['cname']
        population = request.form['population']

        data = Country(cname, population)
        db.session.add(data)
        db.session.commit()
        flash("Country inserted successfully")
        return redirect(url_for('countries'))

@app.route('/countries/update', methods = ['GET', 'POST'])
def update_country():
    if request.method == 'POST':
        data = Country.query.get(request.form.get('cname'))
        data.population = request.form['population']
        db.session.commit()
        flash("Country updated successfully")
        return redirect(url_for('countries'))

# @app.route('/countries/delete/<cname>/', methods = ['GET', 'POST'])
# def delete_country(cname):
#     data = Country.query.get(cname)
#     db.session.delete(data)
#     db.session.commit()
#     flash("Country deleted successfully")
#     return redirect(url_for('countries'))


########################## Diseases ##########################

@app.route('/diseases')
def diseases():
    disease_data = Disease.query.all()
    for disease in disease_data:
        disease.type = Diseasetype.query.filter_by(id=disease.id).first().description

    types_data = Diseasetype.query.all()
    return render_template("diseases.html", diseases = disease_data, diseasetypes = types_data)

@app.route('/diseases/insert', methods = ['POST'])
def insert_disease():
    if request.method == 'POST':
        disease_code = request.form['disease_code']
        pathogen = request.form['pathogen']
        description = request.form['description']
        id = Diseasetype.query.filter_by(description = request.form['type']).first().id 

        data = Disease(disease_code, pathogen, description, id)
        db.session.add(data)
        db.session.commit()
        flash("Disease inserted successfully")
        return redirect(url_for('diseases'))

@app.route('/diseases/update', methods = ['GET', 'POST'])
def update_disease():
    if request.method == 'POST':
        data = Disease.query.get(request.form.get('disease_code'))
        data.pathogen = request.form['pathogen']
        data.description = request.form['description']
        data.id = Diseasetype.query.filter_by(description = request.form['type']).first().id 

        db.session.commit()
        flash("Disease updated successfully")
        return redirect(url_for('diseases'))

@app.route('/diseases/delete/<disease_code>/', methods = ['GET', 'POST'])
def delete_disease(disease_code):
    data = Disease.query.get(disease_code)
    db.session.delete(data)
    db.session.commit()
    flash("Disease deleted successfully")
    return redirect(url_for('diseases'))


########################## Discoveries ##########################

@app.route('/discoveries')
def discoveries():
    discoveries_data = Discovery.query.all()
    diseases_data = Disease.query.all()
    countries_data = Country.query.all()

    return render_template("discoveries.html", discoveries = discoveries_data, diseases = diseases_data, countries = countries_data)

@app.route('/discoveries/insert', methods = ['POST'])
def insert_discovery():
    if request.method == 'POST':
        cname = request.form['cname']
        disease_code = request.form['disease_code']
        first_enc_date = request.form['first_enc_date']

        data = Discovery(cname, disease_code, first_enc_date)
        db.session.add(data)
        db.session.commit()
        flash("Discovery inserted successfully")
        return redirect(url_for('discoveries'))

@app.route('/discoveries/update', methods = ['GET', 'POST'])
def update_discovery():
    if request.method == 'POST':
        data = Discovery.query.get((request.args['c'], request.args['d']))
        data.first_enc_date = request.form['first_enc_date']
        
        db.session.commit()
        flash("Discovery updated successfully")
        return redirect(url_for('discoveries'))

@app.route('/discoveries/delete', methods = ['GET', 'POST'])
def delete_discovery():
    data = Discovery.query.get((request.args['c'], request.args['d']))
    db.session.delete(data)
    db.session.commit()
    flash("Discovery deleted successfully")
    return redirect(url_for('discoveries'))


########################## Users ##########################

@app.route('/users')
def users():
    users_data = User.query.all()
    countries_data = Country.query.all()
    
    return render_template("users.html", users = users_data, countries = countries_data)

@app.route('/users/insert', methods = ['POST'])
def insert_user():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        surname = request.form['surname']
        salary = request.form['salary']
        phone = request.form['phone']
        cname = request.form['cname']

        data = User(email, name, surname, salary, phone, cname)
        db.session.add(data)
        db.session.commit()
        flash("User inserted successfully")
        return redirect(url_for('users'))

@app.route('/users/update', methods = ['GET', 'POST'])
def update_user():
    if request.method == 'POST':
        data = User.query.get(request.form.get('email'))
        data.name = request.form['name']
        data.surname = request.form['surname']
        data.salary = request.form['salary']
        data.phone = request.form['phone']
        data.cname = request.form['cname']
        
        db.session.commit()
        flash("User updated successfully")
        return redirect(url_for('users'))

@app.route('/users/delete/<email>/', methods = ['GET', 'POST'])
def delete_user(email):
    data = User.query.get(email)
    db.session.delete(data)
    db.session.commit()
    flash("User deleted successfully")
    return redirect(url_for('users'))


########################## PublicServants ##########################

@app.route('/public_servants')
def publicservants():
    public_servants_data = PublicServant.query.all()
    users_data = User.query.all()
    
    return render_template("public_servants.html", publicservants = public_servants_data, users = users_data)

@app.route('/public_servants/insert', methods = ['POST'])
def insert_public_servant():
    if request.method == 'POST':
        email = request.form['email']
        department = request.form['department']

        data = PublicServant(email, department)
        db.session.add(data)
        db.session.commit()
        flash("Public servant inserted successfully")
        return redirect(url_for('publicservants'))

@app.route('/public_servants/update', methods = ['GET', 'POST'])
def update_public_servant():
    if request.method == 'POST':
        data = PublicServant.query.get(request.form.get('email'))
        data.department = request.form['department']
        
        db.session.commit()
        flash("Public servant updated successfully")
        return redirect(url_for('publicservants'))

@app.route('/public_servants/delete/<email>/', methods = ['GET', 'POST'])
def delete_public_servant(email):
    data = PublicServant.query.get(email)
    db.session.delete(data)
    db.session.commit()
    flash("Public servant deleted successfully")
    return redirect(url_for('publicservants'))

########################## Doctors ##########################

@app.route('/doctors')
def doctors():
    doctors_data = Doctor.query.all()
    users_data = User.query.all()
    
    return render_template("doctors.html", doctors = doctors_data, users = users_data)

@app.route('/doctors/insert', methods = ['POST'])
def insert_doctors():
    if request.method == 'POST':
        email = request.form['email']
        degree = request.form['degree']

        data = Doctor(email, degree)
        db.session.add(data)
        db.session.commit()
        flash("Doctor inserted successfully")
        return redirect(url_for('doctors'))

@app.route('/doctors/update', methods = ['GET', 'POST'])
def update_doctor():
    if request.method == 'POST':
        data = Doctor.query.get(request.form.get('email'))
        data.degree = request.form['degree']
        
        db.session.commit()
        flash("Doctor updated successfully")
        return redirect(url_for('doctors'))

@app.route('/doctors/delete/<email>/', methods = ['GET', 'POST'])
def delete_doctor(email):
    data = Doctor.query.get(email)
    db.session.delete(data)
    db.session.commit()
    flash("Doctor deleted successfully")
    return redirect(url_for('doctors'))


########################## Specializations ##########################

@app.route('/specializations')
def specializations():
    specializations_data = Specialize.query.all()
    diseasetypes_data = Diseasetype.query.all()
    doctors_data = Doctor.query.all()
    for specialization in specializations_data:
        specialization.type = Diseasetype.query.filter_by(id=specialization.id).first().description
    
    return render_template("specializations.html", specializations = specializations_data, doctors = doctors_data, diseasetypes = diseasetypes_data)

@app.route('/specializations/insert', methods = ['POST'])
def insert_specialization():
    if request.method == 'POST':
        email = request.form['email']
        id = Diseasetype.query.filter_by(description = request.form['type']).first().id 

        data = Specialize(id, email)
        db.session.add(data)
        db.session.commit()
        flash("Specialization inserted successfully")
        return redirect(url_for('specializations'))

# @app.route('/specializations/update', methods = ['GET', 'POST'])
# def update_specialization():
#     if request.method == 'POST':
#         data = Specialization.query.get(request.args['id'], request.args['d'])
        
#         db.session.commit()
#         flash("Specialization updated successfully")
#         return redirect(url_for('specializations'))

@app.route('/specializations/delete/', methods = ['GET', 'POST'])
def delete_specialization():
    data = Specialize.query.get((request.args['id'], request.args['d']))
    db.session.delete(data)
    db.session.commit()
    flash("Specialization deleted successfully")
    return redirect(url_for('specializations'))


########################## Records ##########################

@app.route('/records')
def records():
    records_data = Record.query.all()
    diseases_data = Disease.query.all()
    public_servants_data = PublicServant.query.all()
    contries_data = Country.query.all()
    
    return render_template("records.html", records = records_data, diseases = diseases_data, publicservants = public_servants_data, countries = contries_data)

@app.route('/records/insert', methods = ['POST'])
def insert_record():
    if request.method == 'POST':
        email = request.form['email']
        cname = request.form['cname']
        disease_code = request.form['disease_code']
        total_deaths = request.form['total_deaths']
        total_patients =request.form['total_patients']

        data = Record(email, cname, disease_code, total_deaths, total_patients)
        db.session.add(data)
        db.session.commit()
        flash("Record inserted successfully")
        return redirect(url_for('records'))

@app.route('/records/update', methods = ['GET', 'POST'])
def update_record():
    if request.method == 'POST':
        data = Record.query.get((request.args['e'], request.args['c'], request.args['d']))
        data.total_deaths = request.form['total_deaths']
        data.total_patients = request.form['total_patients']

        db.session.commit()
        flash("Record updated successfully")
        return redirect(url_for('records'))

@app.route('/records/delete/', methods = ['GET', 'POST'])
def delete_record():
    data = Record.query.get((request.args['e'], request.args['c'], request.args['d']))
    db.session.delete(data)
    db.session.commit()
    flash("Record deleted successfully")
    return redirect(url_for('records'))

if __name__ == "__main__":
    app.run(debug=True) # remove debug on publish
