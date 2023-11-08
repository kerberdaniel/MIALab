#!/bin/bash

# Define variables
REMOTE_USER="mt19n014"
REMOTE_HOST="submit01.unibe.ch"
REMOTE_FOLDER="/storage/homefs/mt19n014/MIALab/bin/mia-result"
LOCAL_DESTINATION="C:/Users/tmatt/Desktop"
ZIP_FILE_NAME="mia-result.zip"

# Zip the remote folder
ssh ${REMOTE_USER}@${REMOTE_HOST} "zip -r ${ZIP_FILE_NAME} ${REMOTE_FOLDER}"

# Download the zip file to the local machine
scp ${REMOTE_USER}@${REMOTE_HOST}:${ZIP_FILE_NAME} ${LOCAL_DESTINATION}

# Optional: Remove the zip file from the remote server
ssh ${REMOTE_USER}@${REMOTE_HOST} "rm ${ZIP_FILE_NAME}"
