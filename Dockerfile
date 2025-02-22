# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry==1.8.4

# Copy the current directory contents into the container at /app
COPY . /app

# Include files
COPY data.json /app/data.json

# Install dependencies using Poetry
RUN poetry install --no-dev

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run the bot
CMD ["poetry", "run", "python", "BEAN.py"]
