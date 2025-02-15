FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y python3 python3-pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy script and model loading files
COPY . .

# Set environment variables
ENV HF_HOME=/app/.cache/huggingface

# Start the bot
CMD ["python3", "bot.py"]