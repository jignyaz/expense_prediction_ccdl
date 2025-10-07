import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
import random

# Create a simple dataset if the actual data is not available
def create_sample_data(n_samples=100):
    dates = pd.date_range(start='2023-01-01', periods=n_samples)
    # Generate some realistic expense data with weekly and monthly patterns
    expenses = []
    
    for i in range(n_samples):
        # Base expense
        base = 500
        # Add some weekly pattern (weekends have higher expenses)
        day_of_week = dates[i].dayofweek
        weekly_factor = 1.2 if day_of_week >= 5 else 1.0
        # Add some monthly pattern (end of month has higher expenses)
        day_of_month = dates[i].day
        monthly_factor = 1.3 if day_of_month >= 25 else 1.0
        # Add some noise
        noise = random.uniform(0.8, 1.2)
        
        expense = base * weekly_factor * monthly_factor * noise
        expenses.append(expense)
    
    df = pd.DataFrame({
        'Date': dates,
        'amount': expenses,
        'type': 0  # 0 for expense
    })
    
    return df

# Create sequences for LSTM model
def create_sequences(data, window_size):
    X, y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i:i+window_size])
        y.append(data[i+window_size])
    return np.array(X), np.array(y)

# Main function to train and save model
def train_and_save_model():
    print("Starting model training...")
    
    # Try to load actual data, or use sample data if not available
    try:
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'expenses_income_summary_1.csv')
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            print(f"Loaded actual data from {data_path}")
        else:
            print("Actual data not found, creating sample data")
            df = create_sample_data()
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        print("Creating sample data instead")
        df = create_sample_data()
    
    # Preprocess data
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Ensure we have the amount column
    if 'amount' not in df.columns:
        print("'amount' column not found in data, using first numeric column")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            df['amount'] = df[numeric_cols[0]]
        else:
            raise ValueError("No numeric columns found in data")
    
    # Scale the data
    scaler = MinMaxScaler()
    df['scaled_amount'] = scaler.fit_transform(df[['amount']])
    
    # Create sequences
    window_size = 10  # Smaller window for simplicity
    X, y = create_sequences(df['scaled_amount'].values, window_size)
    
    # Reshape for LSTM [samples, time steps, features]
    X = X.reshape(X.shape[0], X.shape[1], 1)
    
    # Split data
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # Build a simple LSTM model
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(window_size, 1)),
        tf.keras.layers.LSTM(50),
        tf.keras.layers.Dense(1)
    ])
    
    # Compile model
    model.compile(optimizer='adam', loss='mean_squared_error')
    
    # Train model (with fewer epochs for speed)
    print("Training model...")
    model.fit(
        X_train, y_train,
        epochs=10,
        batch_size=32,
        validation_data=(X_test, y_test),
        verbose=1
    )
    
    # Save model and scaler
    model_path = os.path.join(os.path.dirname(__file__), 'expense_model.h5')
    scaler_path = os.path.join(os.path.dirname(__file__), 'scaler.pkl')
    
    model.save(model_path)
    joblib.dump(scaler, scaler_path)
    
    print(f"Model saved to {model_path}")
    print(f"Scaler saved to {scaler_path}")
    
    return model, scaler

if __name__ == "__main__":
    train_and_save_model()