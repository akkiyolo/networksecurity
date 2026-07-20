# 🛡️ NetworkSecurity — Phishing Detection MLOps Pipeline

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-ECR%20%7C%20EC2%20%7C%20S3-FF9900.svg)](https://aws.amazon.com/)
[![MLflow](https://img.shields.io/badge/MLflow-Experiment%20Tracking-0194E2.svg)](https://mlflow.org/)
[![License](https://img.shields.io/badge/License-Educational-lightgrey.svg)](#license)

An end-to-end **MLOps pipeline** for detecting phishing websites using machine learning. The project automates the full lifecycle — from data ingestion (MongoDB) through validation, transformation, model training with experiment tracking (MLflow / DagsHub), and serving predictions via a **FastAPI** REST API — containerized with Docker and deployed to AWS through a fully automated GitHub Actions CI/CD pipeline.

---

## 📐 Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  MongoDB     │────▶│  Data        │────▶│  Data            │────▶│  Data            │────▶│  Model      │
│  (Raw Data)  │     │  Ingestion   │     │  Validation      │     │  Transformation  │     │  Trainer    │
└─────────────┘     └──────────────┘     └──────────────────┘     └──────────────────┘     └──────┬──────┘
                                                                                                    │
                                                                                                    ▼
                    ┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌─────────────┐
                    │  FastAPI     │◀────│  Saved Model     │◀────│  MLflow /        │◀────│  Best Model │
                    │  (Predict)   │     │  (.pkl)          │     │  DagsHub Logging │     │  Selection  │
                    └──────────────┘     └──────────────────┘     └──────────────────┘     └─────────────┘
```

**CI/CD flow (GitHub Actions → AWS):**

```
Push to main ──▶ CI (lint + test) ──▶ CD (build & push image to ECR) ──▶ Deploy (pull & run on self-hosted EC2 runner)
```

---

## 📁 Project Structure

```
networksecurity/
├── .github/workflows/
│   └── main.yml                   # CI/CD — build, push to ECR, deploy to EC2
├── data_schema/
│   └── schema.yaml                # Expected column names & data types
├── networksecurity/                # Core Python package
│   ├── cloud/                     # AWS S3 sync utilities
│   ├── components/                # Pipeline stage implementations
│   │   ├── data_ingestion.py      # Pull data from MongoDB, train/test split
│   │   ├── data_validation.py     # Schema checks & data-drift detection
│   │   ├── data_transformation.py # KNN imputation & preprocessing
│   │   └── model_trainer.py       # Multi-model training & MLflow logging
│   ├── constant/                  # All configuration constants
│   ├── entity/                    # Config & artifact dataclasses
│   ├── exception/                 # Custom exception handler
│   ├── logging/                   # Centralised logger
│   ├── pipeline/
│   │   ├── training_pipeline.py   # Orchestrates all 4 stages sequentially
│   │   └── batch_prediction.py    # Batch inference pipeline
│   └── utils/
│       ├── main_utils/            # save/load objects, evaluate models
│       └── ml_utils/              # NetworkModel wrapper, classification metrics
├── templates/
│   └── table.html                 # Jinja2 template for prediction results
├── app.py                          # FastAPI application (train + predict endpoints)
├── main.py                         # Standalone pipeline runner (no API)
├── push_data.py                    # One-time script to load CSV → MongoDB
├── Dockerfile                      # Container image definition
├── requirements.txt                # Python dependencies
└── setup.py                        # Package metadata & install config
```

---

## 🔄 ML Pipeline Stages

| # | Stage | What It Does |
|---|-------|---------------|
| 1 | **Data Ingestion** | Exports data from MongoDB → CSV, then splits into train (80%) / test (20%) sets. |
| 2 | **Data Validation** | Validates schema against `schema.yaml`, checks column count & data types, generates a **data-drift report** (Chi-squared test). |
| 3 | **Data Transformation** | Applies **KNN Imputer** (k=3, uniform weights) to handle missing values, saves transformed numpy arrays (`.npy`). |
| 4 | **Model Training** | Trains 5 classifiers with **GridSearchCV** hyperparameter tuning, selects the best model, logs metrics to **MLflow**, and saves the model as `.pkl`. |

### Models Evaluated

| Model | Hyperparameters Tuned |
|-------|------------------------|
| Random Forest | `n_estimators`: [8, 16, 32, 128, 256] |
| Decision Tree | `criterion`: [gini, entropy, log_loss] |
| Gradient Boosting | `learning_rate`, `subsample`, `n_estimators` |
| Logistic Regression | Defaults |
| AdaBoost | `learning_rate`, `n_estimators` |

---

## 🧰 Tech Stack

| Category | Technology |
|----------|-------------|
| Language | Python 3.10 |
| ML | scikit-learn, NumPy, Pandas |
| API | FastAPI, Uvicorn |
| Database | MongoDB (via PyMongo) |
| Experiment Tracking | MLflow, DagsHub |
| Containerization | Docker |
| Cloud | AWS (ECR, EC2, S3) |
| CI/CD | GitHub Actions |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- MongoDB instance (local or Atlas)
- Git
- Docker (optional, for containerized runs)

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/networksecurity.git
cd networksecurity

# Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Configure Environment Variables

Create a `.env` file in the project root:

```env
MONGODB_URL_KEY=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

### Load Data into MongoDB (first-time setup)

```bash
python push_data.py
```

This reads `Network_Data/phisingData.csv`, converts it to JSON, and inserts the records into the `KRISHAI.NetworkData` MongoDB collection.

---

## 🏋️ Running the Training Pipeline

### Option 1 — Standalone Script

```bash
python main.py
```

Runs all 4 pipeline stages sequentially and saves artifacts to the `Artifacts/` directory.

### Option 2 — Via the FastAPI Server

```bash
python app.py
```

Then trigger training by visiting:

```
GET http://localhost:8000/train
```

---

## 🔮 Serving Predictions (FastAPI)

```bash
python app.py
# Server starts on http://localhost:8000
```

The root route (`/`) redirects to the interactive Swagger docs at `/docs`.

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Redirects to `/docs` (Swagger UI) |
| `GET` | `/train` | Triggers the full training pipeline |
| `POST` | `/predict` | Upload a CSV file to get phishing predictions |

### Prediction Example

```bash
curl -X POST "http://localhost:8000/predict" \
     -F "file=@test_data.csv"
```

The response renders an HTML table with the original features plus a `predicted_column` (1 = legitimate, -1 = phishing). Results are also saved to `prediction_output/output.csv`.

---

## 📊 Experiment Tracking with MLflow

All training runs are logged to **DagsHub's hosted MLflow** instance:

- **Tracking URI:** `https://dagshub.com/krishnaik06/networksecurity.mlflow`
- **Metrics logged:** F1 Score, Precision, Recall (for both train and test sets)
- **Artifacts logged:** Trained model objects

View experiment history, compare runs, and manage model versions through the DagsHub MLflow UI.

---

## 🐳 Docker

### Build the Image

```bash
docker build -t networksecurity .
```

### Run the Container

```bash
docker run -d -p 8000:8000 \
  -e MONGODB_URL_KEY="<your-mongodb-url>" \
  networksecurity
```

---

## ⚙️ CI/CD — GitHub Actions

The pipeline (`.github/workflows/main.yml`) runs on every push to `main` (excluding `README.md` changes) and consists of three stages:

1. **Continuous Integration** — Linting & unit tests
2. **Continuous Delivery** — Builds the Docker image and pushes it to **AWS ECR**
3. **Continuous Deployment** — Pulls the image on a **self-hosted EC2 runner** and starts the container

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key |
| `AWS_SECRET_KEY_ID` | AWS IAM secret key |
| `AWS_REGION` | AWS region (e.g. `us-east-1`) |
| `AWS_ECR_LOGIN_URI` | ECR login URI |
| `ECR_REPOSITORY_NAME` | ECR repository name |

### EC2 Self-Hosted Runner Setup

```bash
# Update packages
sudo apt-get update -y && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker
```

Then register the instance as a self-hosted GitHub Actions runner under **Settings → Actions → Runners** in your repository.

---

## 📋 Dataset & Features

The dataset contains **30 features** extracted from URLs to determine whether a website is a phishing site or legitimate. Each feature is encoded as an integer (`-1`, `0`, or `1`).

<details>
<summary><strong>Click to expand full feature list</strong></summary>

| Feature | Description |
|---------|--------------|
| `having_IP_Address` | Whether the URL uses an IP address |
| `URL_Length` | Length classification of the URL |
| `Shortining_Service` | Whether a URL shortener was used |
| `having_At_Symbol` | Presence of `@` in the URL |
| `double_slash_redirecting` | Position of `//` in the URL |
| `Prefix_Suffix` | Presence of `-` in the domain |
| `having_Sub_Domain` | Number of sub-domains |
| `SSLfinal_State` | SSL certificate status |
| `Domain_registeration_length` | Domain registration duration |
| `Favicon` | Whether favicon is loaded from external domain |
| `port` | Non-standard port usage |
| `HTTPS_token` | HTTPS token in the domain |
| `Request_URL` | Percentage of external objects |
| `URL_of_Anchor` | Percentage of anchor URLs |
| `Links_in_tags` | Percentage of links in `<meta>`, `<script>`, `<link>` |
| `SFH` | Server Form Handler |
| `Submitting_to_email` | Use of `mailto:` in form action |
| `Abnormal_URL` | Whether hostname is in the URL |
| `Redirect` | Number of redirects |
| `on_mouseover` | Status bar customisation |
| `RightClick` | Right-click disabled |
| `popUpWidnow` | Pop-up window usage |
| `Iframe` | Iframe usage |
| `age_of_domain` | Age of the domain |
| `DNSRecord` | DNS record availability |
| `web_traffic` | Alexa rank of the website |
| `Page_Rank` | Google PageRank |
| `Google_Index` | Whether indexed by Google |
| `Links_pointing_to_page` | Number of inbound links |
| `Statistical_report` | Whether listed in statistical reports |
| **`Result`** | **Target — 1 (legitimate) / -1 (phishing)** |

</details>

---

## 🌱 Environment Variables

| Variable | Required | Description |
|----------|:--------:|--------------|
| `MONGODB_URL_KEY` | ✅ | MongoDB connection string |
| `MLFLOW_TRACKING_URI` | ❌ | MLflow server URL (defaults to DagsHub) |
| `MLFLOW_TRACKING_USERNAME` | ❌ | MLflow auth username |
| `MLFLOW_TRACKING_PASSWORD` | ❌ | MLflow auth token |

---

## 🗺️ Roadmap

- [ ] Add automated integration tests for API endpoints
- [ ] Add model performance monitoring / drift alerts in production
- [ ] Support multi-environment deployments (staging / production)
- [ ] Add authentication to the `/train` and `/predict` endpoints

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to open a pull request or an issue if you'd like to improve this project.

---

## 📄 License

This project is for educational purposes.