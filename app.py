from flask import Flask, request, render_template, jsonify
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import os

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp'
DATABASE = '/tmp/data.db'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def load_data(file_path, file_type):
    if file_type == 'csv':
        df = pd.read_csv(file_path)
    elif file_type == 'json':
        df = pd.read_json(file_path)
    else:
        return None
    return df

def create_database(df):
    engine = create_engine(f'sqlite:///{DATABASE}', echo=False)
    df.to_sql('data', con=engine, index=False, if_exists='replace')
    return engine

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    file_type = request.form['file_type']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    df = load_data(file_path, file_type)
    if df is None:
        return 'Unsupported file type'
    
    create_database(df)
    return jsonify({'message': 'File uploaded successfully'})

@app.route('/query', methods=['POST'])
def query_data():
    query = request.form['query']
    try:
        engine = create_engine(f'sqlite:///{DATABASE}', echo=False)
        result = pd.read_sql_query(query, con=engine)
        return result.to_html()
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
