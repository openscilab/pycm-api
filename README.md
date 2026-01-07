# PyCM API

This project is a REST API wrapper built around the [PyCM](https://github.com/sepandhaghighi/pycm) library, designed to streamline the creation, storage, comparison, and reporting of confusion matrices for machine learning model evaluation. The API offers comprehensive support for standard classification metrics, multi-label classification scenarios, and performance curve generation including ROC and PR curves. Key capabilities include full confusion matrix management with persistent storage, access to essential metrics like accuracy, precision, recall, and F1-score, and rich visualization options through HTML reports and PNG plots. Users can compare multiple confusion matrices side-by-side to evaluate model performance, handle complex multi-label classification with per-class and per-sample metrics, and generate performance curves complete with Area Under the Curve calculations. The system also incorporates secure user management with API key-based authentication and provides an admin dashboard for overseeing both users and confusion matrices, making it a complete solution for machine learning practitioners who need robust model evaluation tools.

## Installation

### Prerequisites

- Python >= 3.10
- pip package manager

### Setup Steps

1. **Clone the repository** (if applicable) or navigate to the project directory:
```bash
cd pycm-api
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set environment variables** for admin authentication. These credentials are required to access administrative endpoints (`/users/`, `/cms/`).
```bash
export PYCM_API_ADMIN="your_admin_username"
export PYCM_API_ADMIN_PASSWORD="your_admin_password"
```

4. **Run the application**:
```bash
uvicorn app.main:app --reload
```

The `--reload` flag enables auto-reload on code changes (useful for development).

5. **Access the API**:
- API Base URL: `http://127.0.0.1:8000`
- Interactive API Documentation: `http://127.0.0.1:8000/docs`

## API Endpoints

### User Management

#### `POST /sign_up/`
Register a new user account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response**: User object with `id`, `email`, `api_key`, `credit`, `is_active`, and `cms` (user confusion matrices list) fields. Note that using `api_key` user will be authenticated for using the APIs.


#### `POST /sign_in/`
Authenticate an existing user.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response**: User object (same as sign_up).

---

### Confusion Matrix Operations

#### `POST /cm/create`
Create a new confusion matrix.

**Request Body**:
```json
{
  "api_key": "your_api_key_here",
  "actual_vector": [1, 0, 1, 1, 0, 1, 0, 0],
  "predicted_vector": [1, 0, 1, 0, 0, 1, 1, 0]
}
```

**Response**: Confusion matrix object with `uid` (unique identified) field.

**Note**: The `actual_vector` and `predicted_vector` can contain integers, floats, or strings representing class labels.

#### `GET /cm/`
Retrieve a confusion matrix by UID.

**Query Parameters**:
- `api_key` (required): Your API key
- `cm_uid` (required): The UID of the confusion matrix

**Response**: Confusion matrix with metrics:
```json
{
  "uid": "cm_uid_here",
  "accuracy": 0.75,
  "precision": 0.8,
  "recall": 0.8,
  "f1": 0.8,
  "confusion_matrix": [[3, 1], [1, 3]]
}
```

#### `POST /cm/update`
Update an existing confusion matrix.

**Query Parameters**:
- `cm_uid` (required): The UID of the confusion matrix to update

**Request Body**: Same as `/cm/create`

**Response**: Updated confusion matrix object.

#### `DELETE /cm/{cm_uid}`
Delete a confusion matrix.

**Query Parameters**:
- `api_key` (required): Your API key

**Response**: `{"message": "Confusion matrix deleted"}`

**Note**: Only the owner of the confusion matrix can delete it.

#### `GET /cm/report`
Generate an HTML report for a confusion matrix.

**Query Parameters**:
- `api_key` (required): Your API key
- `cm_uid` (required): The UID of the confusion matrix

**Response**: HTML content with comprehensive statistics and visualizations.

#### `GET /cm/plot`
Generate a PNG plot visualization for a confusion matrix.

**Query Parameters**:
- `api_key` (required): Your API key
- `cm_uid` (required): The UID of the confusion matrix

**Response**: PNG image file.

---

### Comparison Operations

#### `POST /compare/`
Compare multiple confusion matrices.

**Request Body**:
```json
{
  "api_key": "your_api_key_here",
  "cm_uids": ["uid1", "uid2", "uid3"]
}
```

**Response**: Comparison results including:
- `cm_uids`: List of compared confusion matrix UIDs
- `best_name`: Identifier of the best performing model
- `cm_scores`: Dictionary of scores for each confusion matrix
- `cm_orders`: Ordered list of confusion matrices by performance

---

### Multi-Label Classification

#### `POST /mlcm/`
Create a multi-label confusion matrix (one-time use, not persisted).

**Request Body**:
```json
{
  "api_key": "your_api_key_here",
  "actual_vector": [{"class1", "class2"}, {"class2"}, {"class1"}],
  "predicted_vector": [{"class1"}, {"class2"}, {"class1", "class2"}],
  "classes": ["class1", "class2"]
}
```

**Response**: Multi-label confusion matrix with:
- `multihot_actual`: Multi-hot encoded actual labels
- `multihot_predicted`: Multi-hot encoded predicted labels
- `classes`: List of class names
- `cm_by_classes`: Per-class confusion matrices
- `cm_by_samples`: Per-sample confusion matrices

**Note**: This endpoint does not persist the confusion matrix to the database.

---

### Performance Curves

#### `POST /curve`
Generate ROC or PR curves.

**Request Body**:
```json
{
  "api_key": "your_api_key_here",
  "type": "ROC",
  "actual_vector": [0, 1, 0, 1, 1],
  "probability_vector": [[0.1, 0.9], [0.3, 0.7], [0.2, 0.8], [0.4, 0.6], [0.5, 0.5]],
  "classes": ["class0", "class1"]
}
```

**Parameters**:
- `type`: Either `"ROC"` or `"PR"`
- `actual_vector`: Ground truth labels
- `probability_vector`: Predicted probabilities for each class (list of lists)
- `classes`: Optional list of class names/labels

**Response**: Curve data including:
- `thresholds`: List of threshold values
- `auc_trp`: Dictionary mapping class names to AUC (Area Under Curve) values

---

### Administrative Endpoints (admin only)

#### `GET /users/`
List all users.

**Query Parameters**:
- `skip` (optional): Number of users to skip (default: 0)
- `limit` (optional): Maximum number of users to return (default: 100)

**Response**: List of user objects.

#### `GET /cms/`
List all confusion matrices.

**Query Parameters**:
- `skip` (optional): Number of confusion matrices to skip (default: 0)
- `limit` (optional): Maximum number of confusion matrices to return (default: 100)

**Response**: List of confusion matrix objects.

---

## Usage Examples

```mermaid
flowchart LR
    %% =========================
    %% Normal User Flow
    %% =========================
    subgraph UserFlow["Normal User API Flow"]
        UStart([Start])

        SignUp[POST /sign_up\nCreate user & API key]
        SignIn[POST /sign_in\nAuthenticate user]

        CreateCM[POST /cm/create\nCreate confusion matrix]
        GetCM[GET /cm\nGet metrics & matrix]
        UpdateCM[POST /cm/update\nUpdate confusion matrix]
        DeleteCM[DELETE /cm/{cm_uid}\nDelete confusion matrix]

        Report[GET /cm/report\nGenerate HTML report]
        Plot[GET /cm/plot\nGenerate PNG plot]

        Compare[POST /compare\nCompare confusion matrices]

        MLCM[POST /mlcm\nMulti-label CM\n(no persistence)]
        Curve[POST /curve\nROC / PR curve]

        UEnd([End])

        UStart --> SignUp
        UStart --> SignIn
        SignUp --> CreateCM
        SignIn --> CreateCM

        CreateCM --> GetCM
        GetCM --> UpdateCM
        UpdateCM --> GetCM

        GetCM --> Report
        GetCM --> Plot

        CreateCM --> Compare
        Compare --> UEnd

        GetCM --> DeleteCM
        DeleteCM --> UEnd

        UStart -.-> MLCM
        UStart -.-> Curve
    end

    %% =========================
    %% Admin Flow
    %% =========================
    subgraph AdminFlow["Admin-Only API Flow"]
        AStart([Admin Auth\n(env credentials)])

        ListUsers[GET /users\nList all users]
        ListCMs[GET /cms\nList all confusion matrices]

        AEnd([End])

        AStart --> ListUsers
        AStart --> ListCMs
        ListUsers --> AEnd
        ListCMs --> AEnd
    end
```

### Complete Workflow Example

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# 1. Sign up a new user
signup_response = requests.post(f"{BASE_URL}/sign_up/", json={
    "email": "ml_engineer@example.com",
    "password": "secure_password"
})
user_data = signup_response.json()
api_key = user_data["api_key"]
print(f"API Key: {api_key}")

# 2. Create a confusion matrix
cm_response = requests.post(f"{BASE_URL}/cm/create", json={
    "api_key": api_key,
    "actual_vector": [0, 1, 0, 1, 1, 0, 1, 0],
    "predicted_vector": [0, 1, 1, 1, 1, 0, 0, 0]
})
cm_data = cm_response.json()
cm_uid = cm_data["uid"]
print(f"Confusion Matrix UID: {cm_uid}")

# 3. Retrieve the confusion matrix
get_cm_response = requests.get(
    f"{BASE_URL}/cm/",
    params={"api_key": api_key, "cm_uid": cm_uid}
)
cm_metrics = get_cm_response.json()
print(f"Accuracy: {cm_metrics['accuracy']}")
print(f"Precision: {cm_metrics['precision']}")
print(f"Recall: {cm_metrics['recall']}")
print(f"F1-Score: {cm_metrics['f1']}")

# 4. Generate HTML report
report_response = requests.get(
    f"{BASE_URL}/cm/report",
    params={"api_key": api_key, "cm_uid": cm_uid}
)
with open("report.html", "w") as f:
    f.write(report_response.text)

# 5. Download plot
plot_response = requests.get(
    f"{BASE_URL}/cm/plot",
    params={"api_key": api_key, "cm_uid": cm_uid}
)
with open("plot.png", "wb") as f:
    f.write(plot_response.content)

# 6. Compare multiple models
compare_response = requests.post(f"{BASE_URL}/compare/", json={
    "api_key": api_key,
    "cm_uids": [cm_uid, "another_cm_uid"]
})
comparison = compare_response.json()
print(f"Best model: {comparison['best_name']}")
```

### Using cURL

```bash
# Sign up
curl -X POST "http://127.0.0.1:8000/sign_up/" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'

# Create confusion matrix (replace YOUR_API_KEY with actual key)
curl -X POST "http://127.0.0.1:8000/cm/create" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "YOUR_API_KEY",
    "actual_vector": [0, 1, 0, 1],
    "predicted_vector": [0, 1, 1, 1]
  }'

# Get confusion matrix
curl "http://127.0.0.1:8000/cm/?api_key=YOUR_API_KEY&cm_uid=CM_UID"
```

## Storage

The application uses a hybrid storage approach:

### Database (SQLite)
- **Location**: `app/DB.db`
- **Stores**: 
  - User accounts (email, hashed password, API key, credit, status)
  - Confusion matrix metadata (UID, owner relationship, creation timestamp)

### File System
- **Confusion Matrix Objects**: `app/cms/`
  - Serialized PyCM confusion matrix objects
  - Filename format: `{cm_uid}.obj`
  
- **HTML Reports**: `app/reports/`
  - Generated HTML reports for confusion matrices
  - Filename format: `{cm_uid}.html`
  
- **Plot Images**: `app/plots/`
  - PNG images of confusion matrix visualizations
  - Filename format: `{cm_uid}.png`

All storage directories are created automatically if they don't exist.
