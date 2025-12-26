# REST API for PyCM Library

## Usage (dev)
After installing requirements, run the below command:
```bash
uvicorn app.main:app --reload
```
This runs a reloading Fastapi web service on `http://127.0.0.1:8000`. Find the API documentation in `/docs` or `/redoc`.

## App Structure

### `__init__.py`
Init Python file

### `main.py`
Main module contain all routers

### `database.py`
Utilities for interacting with SQLite database

### `models.py`
Models associated to database tables

### `utils.py`
Utility modules

### `crud.py`
The module for create, read, update and delete. This module serves as a interface between routers in `main.py` and utility functions in `utils.py`

### `schemas.py`
Classes which indicates router output type.

### `params.py`
Application parameters
