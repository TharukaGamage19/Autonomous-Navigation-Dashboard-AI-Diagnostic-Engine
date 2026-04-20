FROM python:3.9-slim

# 1. Set the working directory
WORKDIR /app

# 2. Create a non-root user (matching your Checkov example ID)
# -m creates a home directory (needed by Streamlit for cache/configs)
# -u 10014 assigns the specific user ID
RUN useradd -m -u 10014 appuser

# 3. Copy the files into the container
COPY . .

# 4. Install dependencies (running as root so it has permission to install globally)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Change the ownership of the /app directory to our new non-root user
RUN chown -R appuser:appuser /app

# 6. Switch to the non-root user ID before executing the application
USER 10014

# 7. Expose the port and run the app
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
