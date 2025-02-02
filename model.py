import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

try:
    df = pd.read_csv("dataset.csv")
    logging.info("Dataset loaded successfully.")

    logging.info(f"Columns in the dataset: {df.columns}")

    if 'label' not in df.columns:
        raise ValueError("'label' column is missing in the dataset.")
    
    le = LabelEncoder()
    df['label_encoded'] = le.fit_transform(df['label'])

    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['label_encoded']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    logging.info(f"Training set size: {X_train.shape[0]}, Test set size: {X_test.shape[0]}")

    model = RandomForestClassifier(n_estimators=100, random_state=42)

    model.fit(X_train, y_train)
    logging.info("Model trained successfully.")

    pickle.dump(model, open('models/crop_model.pkl', 'wb'))
    pickle.dump(le, open('models/label_encoder.pkl', 'wb'))
    logging.info("Model and label encoder saved successfully.")

except Exception as e:
    logging.error(f"Error occurred: {e}")
    print(f"Error: {e}")
