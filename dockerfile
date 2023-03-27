FROM python:3.9
ENV PYTHONBUFFERED=1
ENV REDIS_HOST "redis"

# Set the working directory
WORKDIR /django

# Copy the requirements file to the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install cmake pandas opencv-python-headless && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get install libpq-dev libssl-dev openssl

# Copy the source code to the container
COPY . .
USER root
ENV PATH="py/bin:$PATH"
EXPOSE 8000
STOPSIGNAL SIGINT
CMD ["python","-u", "manage.py", "runserver", "0.0.0.0:8000"]
