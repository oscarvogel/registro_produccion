# registro_produccion

FastAPI + Vue.js Fullstack Application

## Setup

### Backend

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Update .env with your database credentials

5. Run database migrations (if using Alembic):
   ```bash
   alembic upgrade head
   ```

6. Start the server:
   ```bash
   # From the backend/ directory
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend will run on http://localhost:8000

Tip: from the repository root you can run the same app with a single command:

```bash
# from repository root (where this README is)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend/app
```

### Frontend

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start dev server:
   ```bash
   npm run dev
   ```

   Frontend will run on http://localhost:5173

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
registro_produccion/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── core/     # Config, DB, security
│   │   ├── models/   # SQLAlchemy models
│   │   └── schemas/  # Pydantic schemas
│   └── requirements.txt
└── frontend/         # Vue.js application
    ├── src/
    │   ├── components/
    │   ├── views/
    │   ├── stores/   # Pinia stores
    │   └── services/ # API integration
    └── package.json
```

## Database

Current database: mysql
Connection string in: backend/.env
