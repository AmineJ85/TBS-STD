# Use an official Python runtime as a parent image
FROM python:3.11-alpine

# Installer les dépendances système nécessaires pour mysqlclient
RUN apk add --no-cache gcc musl-dev mariadb-connector-c-dev pkgconfig

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the working directory
COPY . .

# Expose the port that Flask will run on
EXPOSE 5000

# Define environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the Flask application
# CMD ["flask", "run"]

# Run the Flask application
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]