from flask import Flask, render_template, request, jsonify, send_from_directory
import random
import math
import os
import csv
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Azure configuration check function
def check_azure_config():
    required_vars = ['AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET', 'AZURE_TENANT_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        app.logger.warning(f"Missing Azure environment variables: {missing_vars}")
    
    return len(missing_vars) == 0

# Route to serve the dark mode UI
@app.route('/')
def index():
    return render_template('index.html')

# Route to serve the dark mode demo directly if needed
@app.route('/dark_mode_demo')
def dark_mode_demo():
    return send_from_directory('.', 'dark_mode_demo.html')

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        # Check if expenses data is provided
        if 'expenses' not in data or not data['expenses']:
            return jsonify({'error': 'Please provide historical expense values'}), 400
        
        expenses = data['expenses']
        
        # Ensure we have at least 3 expense values
        if len(expenses) < 3:
            return jsonify({'error': 'Please provide at least 3 historical expense values'}), 400
        
        # Simple prediction logic based on historical data
        avg_expense = sum(expenses) / len(expenses)
        
        # Add some trend analysis
        recent_trend = expenses[-1] - expenses[0]
        trend_factor = 1 + (recent_trend / expenses[0]) * 0.5
        trend_factor = max(0.9, min(1.1, trend_factor))
        
        # Add some randomness
        random_factor = 0.98 + random.random() * 0.04
        
        # Calculate prediction
        prediction = avg_expense * trend_factor * random_factor
        
        return jsonify({
            'prediction': round(prediction, 2),
            'confidence': 0.85,
            'trend': 'upward' if recent_trend > 0 else 'downward'
        })
    
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Process the CSV file
            expenses = []
            categories = []
            dates = []
            
            with open(file_path, 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                
                # Find the expense, category, and date columns
                headers = csv_reader.fieldnames
                expense_col = next((h for h in headers if 'expense' in h.lower() or 'amount' in h.lower() or 'cost' in h.lower()), None)
                category_col = next((h for h in headers if 'category' in h.lower() or 'type' in h.lower()), None)
                date_col = next((h for h in headers if 'date' in h.lower() or 'month' in h.lower()), None)
                
                if not expense_col:
                    return jsonify({'error': 'Could not find expense column in CSV'}), 400
                
                # Process each row
                for row in csv_reader:
                    try:
                        # Clean and parse the expense value
                        expense_str = row[expense_col].replace('$', '').replace(',', '').strip()
                        expense = float(expense_str)
                        expenses.append(expense)
                        
                        # Get category if available
                        category = row.get(category_col, 'Other') if category_col else 'Other'
                        categories.append(category)
                        
                        # Get date if available
                        date = row.get(date_col, '') if date_col else ''
                        dates.append(date)
                    except (ValueError, KeyError) as e:
                        # Skip rows with invalid data
                        continue
            
            # Return the processed data
            return jsonify({
                'message': f'Successfully processed {len(expenses)} expense records',
                'expenses': expenses,
                'categories': categories,
                'dates': dates
            })
        
        return jsonify({'error': 'File type not allowed'}), 400
    
    except Exception as e:
        print(f"CSV upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/save-expense', methods=['POST'])
def save_expense():
    try:
        # Get data from request
        data = request.get_json()
        
        if not data or 'amount' not in data:
            return jsonify({'error': 'Please provide expense amount'}), 400
        
        # In a real application, you would save this to a database
        # For now, we'll just return success
        return jsonify({
            'message': 'Expense saved successfully',
            'expense': {
                'amount': data.get('amount'),
                'category': data.get('category', 'Other'),
                'date': data.get('date', '')
            }
        })
    
    except Exception as e:
        print(f"Save expense error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/train', methods=['POST'])
def train_model():
    try:
        # This would typically trigger model training
        # For now, we'll just return a success message
        return jsonify({'status': 'success', 'message': 'Model training initiated successfully'})
    except Exception as e:
        print(f"Training error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Check Azure configuration before starting
    if check_azure_config():
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("Warning: Missing Azure configuration. App may not function properly in cloud environment.")
        app.run(host='0.0.0.0', port=5000, debug=False)
