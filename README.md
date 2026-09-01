# Quotation Generator

Professional quotation generator for freelance web development business.

## Prerequisites
- Python 3.12+
- PostgreSQL

## Installation Steps
1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

## PostgreSQL Setup
1. Open your PostgreSQL terminal or pgAdmin.
2. Create the database:
   ```sql
   CREATE DATABASE quotation_generator;
   ```
3. Ensure your `.env` file reflects your local database credentials (e.g., username `postgres` and your password).

## Environment Variables
- `DB_HOST`: Hostname of your database (e.g., `localhost`)
- `DB_PORT`: Database port (e.g., `5432`)
- `DB_NAME`: Database name (`quotation_generator`)
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `STORAGE_PATH`: Path for storing files (default: `storage`)

## File Storage
The application will automatically create storage directories:
- `storage/quotations/`: For generated PDFs and images
- `storage/logos/`: For company logos

## Database Initialization & Seed Data
The database tables are automatically initialized on the first run of the application.
To seed the database with default web development services, run:
```bash
python seed_data.py
```

## Running the Application
```bash
streamlit run app.py
```

## Features
- **Quotation Numbering**: Automatically generates sequential numbers in the format `QT-YYYY-NNNN`.
- **Services Management**: Easily add or edit services via the Services page.
- **Client Management**: Maintains a record of clients for easy re-quoting.
