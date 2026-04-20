FROM python:3.9-slim

# 1. Create the non-root user immediately
RUN useradd -m -u 10014 appuser

# 2. Set working directory
WORKDIR /app

# 3. Copy ONLY requirements first (This speeds up future builds)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your Python code into the container
COPY . .

# 6. Give the new user ownership of the files
RUN chown -R appuser:appuser /app

# 7. Switch to the secure user
USER 10014

# 8. Run the app
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
