# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container to /app
WORKDIR /bar_replay_processor

# Copy the current directory contents into the container at /app
COPY . /bar_replay_processor

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run your script when the container launches
CMD ["python", "./BAR_get_replays.py"]