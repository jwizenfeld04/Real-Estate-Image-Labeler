from flask import Blueprint, render_template, Flask, request

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html")



@main.route('/get_image', methods=['GET'])
def get_image():
    """
    Fetch a random property image from GCP Storage that hasn’t been labeled yet.

    Functionality:
    - Query Firestore for images where `served = False`.
    - Retrieve a random image from GCP Storage using the `image_path` stored in Firestore.
    - Set the `served` field to `True` to ensure no other users are served the same image.

    Notes:
    - Handle cases where no unlabeled images are available.
    """
    pass  # Implementation here


@main.route('/start_session', methods=['POST'])
def start_session():
    """
    Initialize a new user session with a username and session type (room labeling or score labeling).

    Functionality:
    - Store session information in Firestore, including `username`, `session type`, 
    and the timestamp when the session starts.
    - Track which images have been labeled in the session based on the `image_path` or ID.

    Notes:
    - Session data should include image labeling status.
    """
    pass  # Implementation here


@main.route('/update_label', methods=['POST'])
def update_label():
    """
    Update Firestore with the room type or score for a specific image, set the image’s 
    labeled status to True, and increment the session score.

    Functionality:
    - Receive the labeled image ID, room type/score, and session information.
    - Update the Firestore document associated with the image with the room type or score.
    - Increment the user’s session score in Firestore.

    Room Types:
    - Exterior, Bathroom, Bedroom, Kitchen, Living Room, Basement, Attic, Garage, Other.

    Scores:
    - A scale from 1-9. (Descriptions for each score will be added later).

    Notes:
    - Ensure robust error handling and validation for input data.
    """
    pass  # Implementation here


@main.route('/reset_image_served', methods=['GET'])
def reset_image_served():
    """
    Reset any images that have been served but not labeled after a defined time period (stale images).

    Functionality:
    - Query Firestore for images with `served = True` and `labeled = False`.
    - Reset `served = False` for these images, allowing them to be re-served to new users.

    Scheduler:
    - This endpoint should run periodically using a cloud scheduler (e.g., Cloud Scheduler) 
    to prevent stale images.
    """
    pass  # Implementation here


@main.route('/get_leaderboard', methods=['GET'])
def get_leaderboard():
    """
    Retrieve a leaderboard of user session scores, sorted by the number of labeled images.

    Functionality:
    - Query Firestore for all user sessions and their scores.
    - Return a sorted list of users with the highest labeling scores.
    """
    pass  # Implementation here


@main.route('/skip_image', methods=['POST'])
def skip_image():
    """
    Allows users to skip an image and reset its served status to False.

    Functionality:
    - Receive the image ID and session information.
    - Update the Firestore document to reset `served = False`.
    """
    pass  # Implementation here