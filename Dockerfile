# Use official lightweight Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY backend/requirements.txt ./backend/

# Install dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the rest of the backend files
COPY backend/ ./backend/

# Change to backend directory
WORKDIR /app/backend

# Run the training script to generate the models (.joblib files)
RUN python train_model.py

# Expose the port the app runs on
EXPOSE 10000

# Start the FastAPI server using uvicorn, reading from the PORT env var
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}
