from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import logging
from datetime import datetime

# Setup Flask app
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://dss-461-server-admin:30HtF0meiZNR@dss-461-server.database.windows.net:1433/energy?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the data model
class EnergyData(db.Model):
    __tablename__ = 'EnergyData'
    __table_args__ = {'schema': 'dss'}
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.Date)
    region = db.Column(db.String)
    price = db.Column(db.Float)
    megawatt = db.Column(db.Float)
    revenue = db.Column(db.Float)

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        # Retrieve query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        region = request.args.get('region')

        # Construct query based on parameters
        query = db.session.query(EnergyData)
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(EnergyData.date_time >= start_date)
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(EnergyData.date_time <= end_date)
        if region:
            query = query.filter(EnergyData.region.ilike(region))

        # Execute query and fetch results
        result = query.all()
        data = [{'date_time': record.date_time, 'region': record.region, 'price': record.price, 'megawatt': record.megawatt, 'revenue': record.revenue} for record in result]

        return jsonify(data)

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"error": "An error occurred processing your request."}), 500

#@app.route('/welcome')
#def welcome():
#    # Serve the static HTML file on the /welcome route
#    return app.send_static_file('welcomepage.html')
#
#if __name__ == '__main__':
#    app.run(debug=True)
#