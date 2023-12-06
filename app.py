from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
# from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://dss-461-server-admin:J2TWTNN8A7EQ46US$@dss-461-server.database.windows.net:1433/energy?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# # Simple Authentication Function
# def check_auth(username, password):
#     # Replace these with desired credentials for demonstration
#     return username == "admin" and password == "password"

# # Decorator to Require Authentication
# def requires_auth(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth = request.authorization
#         if not auth or not check_auth(auth.username, auth.password):
#             return jsonify({"message": "Authentication Required"}), 401
#         return f(*args, **kwargs)
#     return decorated

# Database Model for GenerationData
class GenerationData(db.Model):
    __table_args__ = {'schema': 'generation'}
    __tablename__ = 'GenerationData'
    id = db.Column(db.Integer, primary_key=True)
    Year = db.Column(db.Integer)
    Month = db.Column(db.Integer)
    State = db.Column(db.String(50))
    ProducerType = db.Column(db.String(50))
    EnergySource = db.Column(db.String(50))
    Generation = db.Column(db.Float)

# Database Model for ConsumptionData
class ConsumptionData(db.Model):
    __table_args__ = {'schema': 'consumption'}
    __tablename__ = 'ConsumptionData'
    id = db.Column(db.Integer, primary_key=True)
    Year = db.Column(db.Integer)
    Hydroelectric = db.Column(db.Float)
    Geothermal = db.Column(db.Float)
    Solar = db.Column(db.Float)
    Wind = db.Column(db.Float)
    Wood = db.Column(db.Float)
    Waste = db.Column(db.Float)
    Biofuels = db.Column(db.Float)
    TotalBiomass = db.Column(db.Float)
    TotalRenewable = db.Column(db.Float)

# Route for fetching GenerationData
@app.route('/generation', methods=['GET'])
# @requires_auth
def get_generation_data():
    data = GenerationData.query.all()
    result = [{'id': d.id, 'Year': d.Year, 'Month': d.Month, 'State': d.State, 
               'ProducerType': d.ProducerType, 'EnergySource': d.EnergySource, 
               'Generation': d.Generation} for d in data]
    return jsonify(result)

# Route for fetching ConsumptionData
@app.route('/consumption', methods=['GET'])
# @requires_auth
def get_consumption_data():
    data = ConsumptionData.query.all()
    result = [{'id': d.id, 'Year': d.Year, 'Hydroelectric': d.Hydroelectric, 'Geothermal': d.Geothermal, 
               'Solar': d.Solar, 'Wind': d.Wind, 'Wood': d.Wood, 'Waste': d.Waste, 
               'Biofuels': d.Biofuels, 'TotalBiomass': d.TotalBiomass, 
               'TotalRenewable': d.TotalRenewable} for d in data]
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
