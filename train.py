import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import math

# ======================
# 1. Load Data
# ======================
df = pd.read_csv("expenses_income_summary.csv")

# Clean and preprocess
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['amount', 'Date'])
df = df.sort_values('Date')

# Convert categorical to numeric
df['type'] = df['type'].map({'EXPENSE': 0, 'INCOME': 1})
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
df = df.dropna(subset=['amount'])

# ======================
# 2. Feature Scaling
# ======================
scaler = MinMaxScaler()
df['scaled_amount'] = scaler.fit_transform(df[['amount']])

# Create sequences
def create_sequences(data, window):
    X, y = [], []
    for i in range(len(data) - window):
        X.append(data[i:i+window])
        y.append(data[i+window])
    return np.array(X), np.array(y)

window = 30
X, y = create_sequences(df['scaled_amount'].values, window)

# Split data
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

# ======================
# 3. Build Model (Enhanced)
# ======================
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(128, return_sequences=True, input_shape=(window, 1)),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.LSTM(64, return_sequences=False),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1)
])

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
              loss='mse')

# ======================
# 4. Train Model (Adaptive)
# ======================
early_stop = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss', patience=20, restore_best_weights=True
)

reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss', factor=0.5, patience=10, min_lr=1e-5
)

history = model.fit(
    X_train, y_train,
    validation_split=0.1,
    epochs=200,
    batch_size=32,
    verbose=1,
    callbacks=[early_stop, reduce_lr]
)

# ======================
# 5. Evaluate Model
# ======================
y_pred = model.predict(X_test)
y_pred_rescaled = scaler.inverse_transform(y_pred)
y_test_rescaled = scaler.inverse_transform(y_test.reshape(-1, 1))

mae = mean_absolute_error(y_test_rescaled, y_pred_rescaled)
rmse = math.sqrt(mean_squared_error(y_test_rescaled, y_pred_rescaled))
mape = mean_absolute_percentage_error(y_test_rescaled, y_pred_rescaled)

print(f"MAE:  {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"MAPE: {mape:.4f}")

# ======================
# 6. Save Model and Scaler
# ======================
print("\nSaving model and scaler...")
model.save('expense_model')
import joblib
joblib.dump(scaler, 'scaler.pkl')
print("Model and scaler saved successfully!")

# ======================
# 7. SAVE FOR DEPLOYMENT
# ======================
import os
import joblib

print("💾 Saving models for Azure deployment...")

# Create models directory
os.makedirs('models', exist_ok=True)

# Save the trained LSTM model
model.save('models/lstm_model.h5')
print("✅ LSTM model saved to models/lstm_model.h5")

# Save the scaler (already created in your code)
joblib.dump(scaler, 'models/scaler.pkl')
print("✅ Scaler saved to models/scaler.pkl")

# Save sequence parameters
joblib.dump(window, 'models/window_size.pkl')
print("✅ Window size saved to models/window_size.pkl")

# Save feature columns info (for compatibility)
feature_info = {
    'window_size': window,
    'feature_columns': ['scaled_amount'],
    'target_column': 'amount',
    'data_shape': X_train.shape,
    'model_type': 'LSTM'
}
joblib.dump(feature_info, 'models/feature_info.pkl')
print("✅ Feature info saved to models/feature_info.pkl")

print("🎉 All models saved successfully! Ready for Azure deployment.")
print(f"📁 Models saved in 'models/' directory:")
print("   - lstm_model.h5 (main LSTM model)")
print("   - scaler.pkl (MinMaxScaler)")
print("   - window_size.pkl (sequence window size: {})".format(window))
print("   - feature_info.pkl (model metadata)")
