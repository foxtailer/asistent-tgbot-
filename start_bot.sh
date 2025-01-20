#!/bin/bash

# Step 1: Start ngrok and expose port 88
echo "Starting ngrok on port 88..."
ngrok http 88 > /dev/null &

# Give ngrok time to start
sleep 5

# Step 2: Get the public URL from ngrok's API
NGROK_API_URL="http://127.0.0.1:4040/api/tunnels"
NGROK_URL=$(curl -s $NGROK_API_URL | jq -r '.tunnels[0].public_url')

# Check if the URL was retrieved
if [ -z "$NGROK_URL" ]; then
    echo "Failed to retrieve the ngrok URL. Exiting."
    exit 1
fi

echo "ngrok URL: $NGROK_URL"

# Step 3: Save the URL to the config file
CONFIG_FILE="/home/zoy/bot/config"
echo "Saving ngrok URL to $CONFIG_FILE..."
echo "$NGROK_URL" > "$CONFIG_FILE"

# Step 4: Run the Docker container
echo "Starting the Docker container..."
docker run --rm -d -v /home/zoy/bot:/app/data bot:my

# Confirm completion
echo "Script completed. Docker container is running."
