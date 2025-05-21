# Use an official Python base image
FROM python:3.12-slim

# Install dependencies if requirements.txt exists
RUN pip3 install toml \ 
  httpx>=0.26.0 \ 
  pyee>=9.0.4 \ 
  betterproto==2.0.0b7 \ 
  ffmpy>=0.3.0 \ 
  websockets_proxy==0.1.3 \ 
  async-timeout>=4.0.3 \ 
  mashumaro>=3.5 \ 
  protobuf3-to-dict>=0.1.5 \ 
  protobuf>=2.19.4

# install ffmpeg
RUN apt-get update && \
  apt-get install -y ffmpeg && \
  rm -rf /var/lib/apt/lists/*

USER 1000:1000
# Set the working directory in the container
WORKDIR /app

# Copy the application code into the container
COPY . /app

ENV CONFIG_FILE=/app/config.toml

# Command to run the application (adjust as needed)
CMD ["python", "/app/src/main.py"]
