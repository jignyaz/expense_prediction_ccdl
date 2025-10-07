# Expense Prediction Application

This application predicts future expenses based on historical expense data using a LSTM neural network model.

## Project Structure

```
├── app.py                 # Flask application
├── train.py               # Model training script
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker container configuration
├── docker-compose.yml     # Local development setup
├── azure-pipelines.yml    # Azure CI/CD pipeline
├── static/                # Static assets
│   ├── css/               # CSS styles
│   └── js/                # JavaScript files
└── templates/             # HTML templates
```

## Local Development

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Train the model:
   ```
   python train.py
   ```
4. Run the application:
   ```
   python app.py
   ```

## Docker Development

1. Build and run with Docker Compose:
   ```
   docker-compose up --build
   ```
2. Access the application at http://localhost:5000

## Azure Deployment

### Prerequisites

1. Azure account with subscription
2. Azure Container Registry
3. Azure App Service plan
4. Azure DevOps project

### Deployment Steps

1. Push your code to a Git repository connected to Azure DevOps
2. Set up the Azure Pipeline using the provided `azure-pipelines.yml` file
3. Configure the following pipeline variables:
   - `containerRegistry`: Your Azure Container Registry name
   - `imageName`: Name for your Docker image
4. Run the pipeline to build and deploy the application

### Azure Resources Used

- Azure App Service: Hosts the containerized application
- Azure Container Registry: Stores the Docker image
- Azure DevOps: Manages CI/CD pipeline

## API Usage

### Predict Endpoint

```
POST /predict
Content-Type: application/json

{
  "historical_expenses": [100, 120, 95, 110, ...]  // At least 30 values
}
```

Response:
```json
{
  "predicted_expense": 115.25,
  "status": "success"
}
```