from os import abort
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemySchema,auto_field
from marshmallow import fields
from datetime import datetime
from sqlalchemy.orm import sessionmaker
import random, secrets
import enum
from sqlalchemy import update , and_, func, extract,create_engine
import sqlalchemy as db
app = Flask(__name__)
engine = create_engine('sqlite:///sales.db', echo = True)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
engine = db.create_engine("sqlite:///database.db")
meta_data = db.MetaData(bind=engine)
db.MetaData.reflect(meta_data)
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()
load_instance = True
###Models####
class Country(enum.Enum):
    Vietnam = "704"
    American = "113"
    Ukraine = "114"
    UnitedArabEmirates ="119" 
    NorthernIreland = "110"
    UnitedStatesofAmerica ="115" 
    UnitedStatesMinorOutlyingIslands ="116" 
    Uruguay = "117"
    Uzbekistan = "118"
    India = "356"
    Indonesia = "225"
    Iran = "324"
    Iraq = "412"
    Ireland = "761"
class Applicant(Base):
    __tablename__ = "Applicant"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    applicant_id = db.Column(db.Integer())
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200),nullable=False)
    dob = db.Column(db.Date())
    country = db.Column(db.Enum(Country))
    status = db.Column(db.String(100), default = "pending" )
    created_dttm = db.Column(db.Date())

    def create(self):
      db.session.add(self)
      db.session.commit()
      return self
    def __init__(self, name, email, dob, country,status,created_dttm): 
        self.name = name
        self.email = email
        self.dob = dob
        self.country = country
        self.status = status 
        self.created_dttm = created_dttm
    def __repr__(self):
        return '%s' % self.id
class results(Base):
    __tablename__ = "results"
    processapplicant_id = db.Column(db.Integer(),primary_key=True)
    client_key = db.Column(db.String(128)) 
    applicant_status = db.Column(db.String(100))
    processed_dttm = db.Column(db.DateTime, default=datetime.utcnow())
    
    def key_client(self,client_key):
        self.client_key = client_key(random(secrets.token_hex(16)))
    

    def __init__(self,applicant_status,processed_dttm):
        self.applicant_status = applicant_status
        self.processed_dttm = processed_dttm
db.create_all()
class ApplicantSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
        model = Applicant
        sqla_session = db.session
    id = fields.Number(dump_only = True)
    applicant_id = fields.Number()
    name = fields.String(required=True)
    email = fields.Email()
    dob = fields.Date()
    country = fields.String(description="The object type",enum=[x.value for x in Country])
    status = fields.String(dump_default = "pending")
    created_dttm = auto_field(dump_only=True)
class Applicant_out(SQLAlchemySchema):
     def __init__(self, appicant_id, status):
        self.applicant_id = appicant_id
        self.status = status
class Meta(SQLAlchemySchema.Meta):
        model = Applicant
        sqla_session = db.session
        applicant_id = fields.Number()
        status = fields.String(dump_default = "pending")
    
class process_schema(SQLAlchemySchema):
    class meta(SQLAlchemySchema.Meta):
        model = results
        sqla_session = db.session
    id = fields.Number(dump_only=True)
    client_key = fields.String(required=True)
    applicant_status = fields.String()
    process_dttm = fields.DateTime()
    processapplicant_id = fields.Number()
@app.route('/Applicant/Applicant_out', methods = ['GET'])
def get_applicant_out():
    get_applicant_o = Applicant.query.all()
    applicant_schema = Applicant_out(many = True)
    applicant_schema.dump(get_applicant_o)
    return make_response(jsonify({"applicant_out": get_applicant_o}))
@app.route('/Applicant', methods = ['GET'])
def index():
    get_applicants = Applicant.query.all()
    applicant_schema = ApplicantSchema(many=True)
    applicants = applicant_schema.dump(get_applicants)
    return make_response(jsonify({"applicants": applicants}))
@app.route('/Applicant/<int:id>', methods = ['GET'])
def get_applicant_by_id(id):
    applicant = Applicant.query.get(id)
    applicant_schema = ApplicantSchema()
    if applicant:
        return applicant_schema.jsonify(applicant)
    else:
        return jsonify({"message": "Not found applicant"}), 404
@app.route('/Applicant/<int:id>', methods = ['PUT'])
def update_applicant_by_id(id):
    data = request.get_json()
    get_applicant = Applicant.query.get(id)
    # if data.get('applicant_id'):
    #     get_applicant.applicant_id = data['applicant_id']
    if data.get('name'):
        get_applicant.name = data['name']
    if data.get('email'):
        get_applicant.email = data['email']
    if data.get('dob'):
        get_applicant.dob =  datetime.strptime(data['dob'],'%m-%d-%Y').date()
    if data.get('country'):
        get_applicant.country= data['country']    
    if data.get('status'):
        get_applicant.status= data['status'] 
    if data.get('created_dttm'):
        get_applicant.created_dttm= datetime.strptime(data['created_dttm'],'%m-%d-%Y').date()
    db.session.add(get_applicant)
    db.session.commit()
    applicant_schema = ApplicantSchema(only=['id', 'name', 'email', 'dob', 'country','status','created_dttm'])
    applicant = applicant_schema.dump(get_applicant)
    return make_response(jsonify({"applicant": applicant}))
@app.route('/Applicant/<id>', methods = ['DELETE'])
def delete_applicant_by_id(id):
        applicant = Applicant.query.get(id)
        db.session.delete(applicant)
        db.session.commit()
        return "applicant Deleted"
@app.route('/Applicant', methods = ['DELETE'])
def delete_applicant_all():
        applicant = Applicant.query.all()
        try:
                db.session.delete(applicant)
                db.session.commit()
                return "applicant Deleted"
        except IndentationError:
                db.session.rollback()
                return jsonify({"message": "Can not delete applicant!"}), 400
@app.route('/Applicant', methods = ['POST'])
def add_applicant():
    # if not request.json:
    #     abort(400)
    # applicant = Applicant(
    #     name = request.json.get('name'),
    #     email = request.json.get('email'),
    #     dob = datetime.strptime(request.json.get('dob'), '%m-%d-%Y').date(),
    #     country = request.json.get('country'),
    #     status = request.json.get('status'),
    #     created_dttm = datetime.strptime(request.json.get('created_dttm'), '%m-%d-%Y').date()
    # )
    # db.session.add(applicant)
    # db.session.commit()
    # return make_response(jsonify({"applicant": applicant}), 201)
    data = request.json
    if (data and ('name' in data) and ('email' in data) and ('dob' in data) and ('country' in data) and ('status' in data) and ('created_dttm'in data)):
        #applicant_id = data['applicant_id']
        Session = sessionmaker(bind = engine)
        session = Session()
        name = data['name']
        email = data['email']
        dob = datetime.strptime(data['dob'],'%m-%d-%Y').date()
        country = data['country']
        status = data['status']
        created_dttm = datetime.strptime(data['created_dttm'],'%m-%d-%Y').date()
        try:
            new_applicant = Applicant(name, email, dob, country, status, created_dttm)
            sqlQuery = "INSERT INTO Applicant(name, email, dob, country, status, created_dttm) VALUES(%s,%s,%s,%s,%s,%s)"
            session.execute(new_applicant,sqlQuery)
            session.commit()
            db.session.add(new_applicant)
            db.session.commit()
            return jsonify({"message": "Add success!"}), 201
        except IndentationError:
            db.session.rollback()
            return jsonify({"message": "Can not add applicant!"}), 400
    else:
        return jsonify({"message": "Request error"}), 400
# def create_applicant():
#     # get_applicant = Applicant.query.get(id)
#     data = request.get_json()
#     applicant_schema = ApplicantSchema()
#     applicant = applicant_schema.load(data)
#     result = applicant_schema.dump(applicant.create())
#     return make_response(jsonify({"applicant": result}),200)
@app.route('/Applicant/process', methods  = ['POST'])
def process_applicant():
    date = datetime.day(Applicant)
    print(type(date))
    if date % 2==0:
        db.session.query(Applicant).filter(Applicant.status).update({Applicant.status: Applicant.status + "processed"})
    else:
        db.session.query(Applicant).filter(Applicant.status).update({Applicant.status: Applicant.status + "failed"})
    # applicant = meta_data.tables['Applicant']
    # date = db.session.query(Applicant).filter(extract('day', Applicant.dob)).all()
    # if date % 2 ==0:

    # else:
    # query = db.session.query(Applicant).filter(and_(func.datetime.date(Applicant.dob) % 2 == 0 ))
    # date = db.session.query(Applicant.dob).filter(Applicant.dob).all()
    # if date % 2 == 0: 
    #     # db.session.query(Applicant)
    #     db.session.query(Applicant).filter(Applicant.dob).first()
    #     db.session.query(Applicant).update({Applicant.status: Applicant.status  + "Processed"})
    # else:
    #     db.session.query(Applicant).filter(Applicant.dob).first()
    #     db.session.query(Applicant).update({Applicant.status: Applicant.status +"Failed"})
    
    # data = request.get_json()
    # print(data)
    # results_schema = process_schema()
    # print (results_schema)
    # result = results_schema.load(data)
    # rs = results_schema.dump(result)
    # return make_response(jsonify({"result": rs}),200)
    
if __name__ == "__main__":
    app.run('0.0.0.0',debug=False)
