#!/bin/bash
# Azure Web App startup script

# Start the application using uvicorn
# Azure Web App will automatically detect and use this
uvicorn app:app --host 0.0.0.0 --port 8000


