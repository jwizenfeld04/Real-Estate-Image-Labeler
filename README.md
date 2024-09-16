# Real-Estate-Image-Labeler

This project is an image labeling tool built with Flask and Tailwind CSS, designed to help label real estate property images. It serves images from Google Cloud Storage, allows users to label them, and stores the results in Google Cloud Firestore.

## File Structure

The project is organized as follows:

```plaintext
Real-Estate-Image-Labeler/
├── backend/
│   └── app/
│       ├── __init__.py                    # Initializes the Flask app and registers blueprints
│       ├── main.py                        # Entry point for running the Flask server
│       ├── config.py                      # Configuration settings for the Flask app
│       ├── routes.py                      # Defines routes and API endpoints for the app
│       └── utils/                         # Utility functions for interacting with GCP services
│           ├── firestore.py               # Functions for interacting with Firestore
│           ├── storage.py                 # Functions for interacting with Google Cloud Storage
│           ├── image_serving.py           # Functions for serving images
│           └── user_stats.py              # Functions for tracking user statistics
│   └── templates/                         # HTML templates
│       ├── index.html                     # Main HTML file for image labeling
├── tests/                                 # Test files
│   └── test_config.py                     # Unit tests for configuration settings
├── .gitignore                             # Files to be excluded from git
├── pytest.ini                             # Python Path for PyTest
├── requirements.txt                       # List of python packages for project
└── README.md                              # Documentation for setup and usage

```
