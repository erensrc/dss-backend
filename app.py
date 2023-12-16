from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

def load_excel_data():
    try:
        data = pd.read_excel('/Users/eren/Desktop/re-gridopt/api/processed_data3.xlsx')
        print("Loaded data columns:", data.columns)
        if 'Hour Ending' not in data.columns:
            raise ValueError("Column 'Hour Ending' not found in Excel file.")
        data['Hour Ending'] = pd.to_datetime(data['Hour Ending'])
        return data
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

def parse_date_based_on_flags(date_str, flags):
    if date_str is None:
        return None

    date_format = ''
    date_format += '%Y' if flags.get('y') else ''
    date_format += '-%m' if flags.get('m') else ''
    date_format += '-%d' if flags.get('d') else ''
    date_format += ' %H' if flags.get('h') else ''
    date_format = date_format.strip('- ')
    try:
        return datetime.strptime(date_str, date_format)
    except ValueError:
        return None

def filter_data(data, start_date_str, end_date_str, flags):
    if 'Hour Ending' not in data.columns:
        print("Error: 'Hour Ending' column not found in data.")
        return pd.DataFrame()  # Return empty DataFrame or handle as needed

    start_date = parse_date_based_on_flags(start_date_str, flags) if start_date_str else None
    end_date = parse_date_based_on_flags(end_date_str, flags) if end_date_str else None

    if start_date is None or end_date is None:
        print("Error: Invalid start or end date.")
        return pd.DataFrame()

    mask = (data['Hour Ending'] >= start_date) & (data['Hour Ending'] <= end_date)
    return data.loc[mask]



def filter_data_by_region(data, region):
    if region not in data.columns:
        print(f"Region {region} not found in the data.")
        return pd.DataFrame()
    filtered_region_data = data[['Hour Ending', region]]
    print(f"Region '{region}' filtered data count:", filtered_region_data.shape[0])
    return filtered_region_data

def get_regions(data):
    regions = [col for col in data.columns if col != 'Hour Ending']
    return regions

def dynamic_aggregation(data, flags):
    if flags.get('h'):
        granularity = 'hour'
    elif flags.get('d'):
        granularity = 'day'
    elif flags.get('m'):
        granularity = 'month'
    elif flags.get('y'):
        granularity = 'year'
    else:
        return data  # No aggregation if no flags are set

    # Extract date parts for aggregation
    data = data.copy()
    data['year'] = data['Hour Ending'].dt.year
    if granularity in ['month', 'day', 'hour']:
        data['month'] = data['Hour Ending'].dt.month
    if granularity in ['day', 'hour']:
        data['day'] = data['Hour Ending'].dt.day
    if granularity == 'hour':
        data['hour'] = data['Hour Ending'].dt.hour

    # Group and aggregate data
    grouping_columns = ['year', 'month', 'day', 'hour'][:['year', 'month', 'day', 'hour'].index(granularity) + 1]
    numeric_columns = data.select_dtypes(include='number').columns.tolist()
    aggregated_data = data.groupby(grouping_columns)[numeric_columns].sum()

    return aggregated_data

@app.route('/api/data', methods=['GET', 'OPTIONS'])
def get_data():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    region = request.args.get('region')
    flags = {
        'y': request.args.get('year', 'false') == 'true',
        'm': request.args.get('month', 'false') == 'true',
        'd': request.args.get('day', 'false') == 'true',
        'h': request.args.get('hour', 'false') == 'true'
    }
    print(f"Received Start Date: {start_date_str}, End Date: {end_date_str}, Region: {region}")
    print("Start Date:", start_date_str)
    print("End Date:", end_date_str)
    print("Flags:", flags)

    data = load_excel_data()
    print("Data columns:", data.columns)
    if start_date_str or end_date_str:
        filtered_data = filter_data(data, start_date_str, end_date_str, flags)
        print("Filtered Data columns:", filtered_data.columns)
    else:
        filtered_data = data

    if region and region in data.columns:
        filtered_data = filter_data_by_region(filtered_data, region)
    print("Region Filtered Data columns:", filtered_data.columns)
    
    aggregated_data = dynamic_aggregation(filtered_data, flags)
    return jsonify(aggregated_data.to_dict(orient='records'))

@app.route('/api/regions', methods=['GET', 'OPTIONS'])
def list_regions():
    data = load_excel_data()
    regions = get_regions(data)
    return jsonify(regions)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
