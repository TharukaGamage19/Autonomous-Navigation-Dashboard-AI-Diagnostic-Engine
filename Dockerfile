FROM python:3.9-slim

# 1. Set the working directory
WORKDIR /app

# 2. Create the non-root user
RUN useradd -m -u 10014 appuser

# 3. EXPLICITLY copy the requirements file first 
# (If this fails, the file is definitely missing or named wrong in GitHub)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
COPY . .

# 6. Change ownership for security
RUN chown -R appuser:appuser /app

# 7. Switch to the restricted user
USER 10014

# 8. Expose port and run Streamlit
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
