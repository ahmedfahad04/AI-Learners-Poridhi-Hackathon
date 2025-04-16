# E-commerce Search Application

This project is an e-commerce search application with a FastAPI backend and a Streamlit frontend. It allows users to search for products in a database and displays the results with highlighted search terms.

## Project Structure

```
application/
├── .gitignore     
├── requirements.txt      # Project dependencies
├── backend/
│   ├── __init__.py
│   ├── database.py       # Database connection and queries
│   ├── main.py           # FastAPI application
│   ├── models.py         # Data models
│   └── data/
│       └── merged_10K_updated.csv  # Product data
└── frontend/
    └── app.py            # Streamlit application

```

## Prerequisites

- Python 3.11+ 
- pip (Python package manager)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd application
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

### Backend Server

1. Navigate to the project directory:

```bash
cd ~/Documents/Poridhi AI Hackathon/application
```

2. Start the FastAPI backend server:

```bash
cd ~/Documents/Poridhi AI Hackathon/application/backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

This will start the backend server at `http://127.0.0.1:8000`.

You can access the API documentation at `http://127.0.0.1:8000/docs` to test the API endpoints directly.

### Frontend Server

1. In a new terminal window, navigate to the project directory:

```bash
cd /home/fahad/Documents/Poridhi AI Hackathon/application/frontend
```

2. Start the Streamlit frontend server:

```bash
streamlit run app.py
```

This will start the Streamlit app and automatically open it in your default web browser, typically at `http://localhost:8501`.

## API Endpoints [`Will be updated`]

- `GET /`: Welcome message
- `GET /products`: Get a list of products with pagination
- `GET /products/{product_id}`: Get a specific product by ID
- `GET /search?query=<search_term>`: Search for products by name or description
- `GET /count`: Get the total count of products in the database

## Features

- Search for products using keywords
- Highlighted search terms in results
- Display of product details including name, description, and price

## Troubleshooting

- Make sure both servers are running simultaneously
- Check that the backend server is running on port 8000, as the frontend is configured to connect to it at `http://127.0.0.1:8000`
- If you encounter any issues with dependencies, try creating a virtual environment before installing requirements