# 🚀 Text Analyzer Serverless API

A robust, enterprise-grade cloud-native microservice built with **FastAPI** and **Python 3.13**, deployed as an **AWS Lambda** function behind **Amazon API Gateway** with automated **CI/CD via GitHub Actions**.

This repository demonstrates best practices for building, cross-compiling, and deploying Python serverless applications on AWS, featuring automated deployment pipelines targeting Amazon Linux runtimes.

---

## 🏗️ Architecture & Flow

```
+------------------+         +----------------------+         +--------------------+
|  GitHub Pages    |  POST   |  Amazon API Gateway  |  HTTP   |  AWS Lambda        |
|  (Frontend UI)   | ------->|  (HTTP API Payload v2) | ------->|  (FastAPI + Mangum)|
+------------------+         +----------------------+         +--------------------+
                                                                        |
                                                                        v
                                                              +--------------------+
                                                              |  CloudWatch Logs   |
                                                              +--------------------+
```

1. **Client Request:** The single-page web app sends an HTTP `POST` request with JSON payload and custom header (`x-api-key`).
2. **API Routing:** Amazon API Gateway proxies the request to AWS Lambda using HTTP API Payload Format v2.0.
3. **ASGI Adapter:** `Mangum` translates the API Gateway event into an ASGI scope for `FastAPI`.
4. **Business Logic & Validation:** FastAPI evaluates authentication headers and computes text metrics (word count, character counts, paragraph metrics).
5. **Response:** Structured JSON responses return to the frontend UI with configured CORS headers.

---

## 🛠️ Tech Stack & Tooling

| Domain | Technology |
|---|---|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) + [Pydantic v2](https://docs.pydantic.dev/) |
| **Serverless Adapter** | [Mangum](https://mangum.io/) (ASGI to AWS Lambda handler) |
| **Cloud Infrastructure** | AWS Lambda (Python 3.13 Runtime), Amazon API Gateway |
| **CI/CD Pipeline** | GitHub Actions (`ubuntu-latest` runner) |
| **Frontend UI** | HTML5, Tailwind CSS, JavaScript (Fetch API), GitHub Pages |

---

## 💡 Key Engineering Challenges & Solutions

### 1. Cross-Compiling Native C-Extensions for AWS Lambda (`pydantic-core`)
* **Challenge:** Developing on macOS (Apple Silicon ARM64 / Darwin) installs `.dylib` dynamic libraries during local `pip install`. Pushing these binaries directly to AWS Lambda causes `Runtime.ImportModuleError: No module named 'pydantic_core._pydantic_core'`.
* **Solution:** Configured the GitHub Actions workflow to explicitly fetch pre-compiled `manylinux2014_x86_64` wheels using `pip install --platform manylinux2014_x86_64 --only-binary=:all: --target ./package`. This guarantees 100% binary compatibility with the Amazon Linux Lambda environment.

### 2. AWS API Gateway Payload v2 Integration
* **Challenge:** Mangum requires complete request context attributes (e.g., `sourceIp`) when translating raw API Gateway events to ASGI request scopes. Missing mock fields in manual console testing caused `KeyError: 'sourceIp'`.
* **Solution:** Schema alignment for test event payloads matching API Gateway HTTP API v2 specifications, ensuring reliable payload parsing in both unit tests and production environments.

### 3. Environment & Runtime Alignment
* **Challenge:** Mismatches between local virtual environments (Python 3.13), CI build runners, and Lambda execution runtimes cause ABI incompatibilities in C-extensions.
* **Solution:** Enforced strict environment pinning across `.github/workflows/deploy.yml` and AWS Lambda runtime settings (pinned to Python 3.13).

---

## 🚀 CI/CD Pipeline Workflow

The repository uses GitHub Actions for continuous integration and automated deployment on pushes to `main`:

```yaml
name: Deploy to AWS Lambda

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Build Linux-Compatible Package
        run: |
          rm -rf package lambda_package.zip
          mkdir -p package
          pip install             --platform manylinux2014_x86_64             --target ./package             --implementation cp             --python-version 3.13             --only-binary=:all:             --upgrade             mangum fastapi pydantic
          cd package && zip -r ../lambda_package.zip . && cd ..
          zip -g lambda_package.zip main.py

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Deploy to AWS Lambda
        run: |
          aws lambda update-function-code             --function-name text-analyzer-api             --zip-file fileb://lambda_package.zip
```

---

## 💻 Local Development Setup

### Prerequisites
* Python 3.13
* Git
* AWS CLI configured (for manual deployments or infrastructure management)

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/your-username/text-analyzer-api.git
cd text-analyzer-api

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Locally with Uvicorn
```bash
uvicorn main:app --reload --port 8000
```
Access the interactive API documentation (Swagger UI) at: `http://127.0.0.1:8000/docs`.

---

## 📡 API Reference

### POST `/analizar`

Analyzes input string metrics.

#### Request Headers
| Header | Type | Description |
|---|---|---|
| `Content-Type` | `string` | `application/json` |
| `x-api-key` | `string` | Authentication key |

#### Request Body
```json
{
  "texto": "FastAPI and AWS Lambda processing serverless data in real time."
}
```

#### Response (200 OK)
```json
{
  "status": "success",
  "resultado": {
    "total_caracteres": 62,
    "total_palabras": 9,
    "total_parrafos": 1
  }
}
```

---

## 📈 Key Takeaways & Developer Insights

* **Zero Infrastructure Overhead:** Serverless compute with AWS Lambda ensures pay-per-use execution and auto-scaling without server maintenance.
* **Packaging Hygiene:** Never bundle host-OS compiled virtual environment binaries (`.dylib` / `.so`) into deployment zips. Always build deployment packages using targeted `--platform` flags in CI runners.
* **Modern API Tooling:** FastAPI offers automatic OpenAPI doc generation, robust Pydantic data validation, and clean ASGI architecture natively compatible with serverless adapters.