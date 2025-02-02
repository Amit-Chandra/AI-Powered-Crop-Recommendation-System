from flask import Flask, render_template, request
import sqlite3
import pickle
import numpy as np
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    model = pickle.load(open('models/crop_model.pkl', 'rb'))
    label_encoder = pickle.load(open('models/label_encoder.pkl', 'rb'))
    logging.info("Model and label encoder loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model or label encoder: {e}")
    raise

def create_database():
    conn = sqlite3.connect('crop_recommendation.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            N REAL,
            P REAL,
            K REAL,
            temperature REAL,
            humidity REAL,
            ph REAL,
            rainfall REAL,
            recommended_crop TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("Database and table (recommendations) checked/created successfully.")

create_database()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        N = float(request.form['N'])
        P = float(request.form['P'])
        K = float(request.form['K'])
        temperature = float(request.form['temperature'])
        humidity = float(request.form['humidity'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        logging.info(f"Received input: N={N}, P={P}, K={K}, Temp={temperature}, Humidity={humidity}, pH={ph}, Rainfall={rainfall}")

        features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])

        predicted_label = model.predict(features)[0]
        recommended_crop = label_encoder.inverse_transform([predicted_label])[0]

        logging.info(f"Predicted crop: {recommended_crop}")

        conn = sqlite3.connect('crop_recommendation.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO recommendations (N, P, K, temperature, humidity, ph, rainfall, recommended_crop)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (N, P, K, temperature, humidity, ph, rainfall, recommended_crop))
        conn.commit()
        conn.close()
        logging.info("Recommendation saved to database.")

        return render_template('result.html', crop=recommended_crop)

    except Exception as e:
        logging.error(f"Error occurred during prediction or database operation: {e}")
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
