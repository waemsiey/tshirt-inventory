# T-shirt Inventory Management 

This is a simple inventory management system designed for a ENY Prints a T-shirt printing business.  
It allows you to track your T-shirt stock using SKUs and manage inventory with ease through a REST API built with FastAPI and SQLAlchemy.  

## Features

- Add new T-shirts with detailed SKU information  
- Update existing T-shirt stock levels  
- Delete T-shirts from inventory  
- View all T-shirts in inventory  
- Uses PostgreSQL as the database backend  
- Simple CLI or API interaction (no frontend UI yet)  

## Technologies Used

- Python 3.11+  
- FastAPI (for API endpoints)  
- SQLAlchemy (ORM for database interaction)  
- PostgreSQL (database)  
- Uvicorn (ASGI server)  

## Setup Instructions

1. Clone the repository:  
   ```bash
   git clone https://github.com/waemsiey/tshirt-inventory.git
   cd tshirt-inventory
2. Create and activate a Python virtual environment:
  python -m venv venv
  # On Windows PowerShell:
  .\venv\Scripts\activate
  # On macOS/Linux:
  source venv/bin/activate

3. Install the virtual environment
     pip install -r requirements.txt

4. Set up postgres database

5. Run the FastAPI application
    uvicorn app.main:app --reload
6. Open browser go to:
   http://127.0.0.1:8000/docs
