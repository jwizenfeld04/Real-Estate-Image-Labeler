from flask import Blueprint, render_template, request, jsonify
from firestore import FirestoreUtils

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/get_image", methods=["GET"])
def get_image():
    try:
        firestore_utils = FirestoreUtils()
        image_data = firestore_utils.get_random_unlabeled_image()
        if image_data:
            return jsonify({"success": True, "image": image_data}), 200
        else:
            return (
                jsonify({"success": False, "message": "No unlabeled images available"}),
                404,
            )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@main.route(
    "/start_session", methods=["POST"]
)  # username and session_type should be the variables in the request
def start_session():
    # try:
    #     # parse the request data
    #     data = request.get_json()
    #     username = data.get('username')
    #     session_type = data.get('session_type')

    #     if not username or not session_type:
    #         return jsonify({"success": False, "message": "Missing username or session type"}), 400

    #     firestore_utils = FirestoreUtils()

    #     # create session data
    #     session_data = {
    #         "username": username,
    #         "session_type": session_type,
    #         "start_timestamp": firestore_utils.get_current_timestamp(),
    #         "images_labeled": [],  # track which images have been labeled in this session
    #         "session_score": 0  # start with a score of 0
    #     }

    #     # Store the session in Firestore
    #     session_id = firestore_utils.create_session(session_data)

    #     # Return the session ID to the client
    #     return jsonify({"success": True, "session_id": session_id})

    # except Exception as e:
    #     # Handle any errors and return a 500 status code with the exception message
    #     return jsonify({"success": False, "error": str(e)}), 500
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


@main.route("/update_label", methods=["POST"])
def update_label():
    try:
        data = request.get_json()
        label = data.get("label")
        image_path = data.get("image_path")
        user_id = data.get("user_id")
        # session_id = data.get('session_id') figure out how to do this

        firestore_utils = FirestoreUtils()

        if label:
            result = firestore_utils.label_room_type(image_path, label, user_id)
        # update score if provided
        # elif score:
        #    result = firestore_utils.label_score(image_path, score, data.get('other_labels', {}), user_id)
        else:
            return (
                jsonify(
                    {"success": False, "message": "Room type or score must be provided"}
                ),
                400,
            )

        # if "successfully" in result:
        #     # increment session score if successful
        #     firestore_utils.increment_session_score(session_id)
        #     return jsonify({"success": True, "message": result})
        # else:
        #     return jsonify({"success": False, "message": result}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@main.route("/reset_image_served", methods=["GET"])
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
    pass


@main.route("/get_leaderboard", methods=["GET"])
def get_leaderboard():
    """
    Retrieve a leaderboard of user session scores, sorted by the number of labeled images.

    Functionality:
    - Query Firestore for all user sessions and their scores.
    - Return a sorted list of users with the highest labeling scores.
    """
    pass  # Implementation here


@main.route("/skip_image", methods=["POST"])
def skip_image():
    try:
        data = request.get_json()
        image_id = data.get("image_id")
        session_id = data.get("session_id")

        if not image_id or not session_id:
            return (
                jsonify({"success": False, "message": "Missing required parameters"}),
                400,
            )

        firestore_utils = FirestoreUtils()
        result = firestore_utils.reset_image_served(image_id)  # NOT IMPLEMENTED YET

        if result:
            return jsonify(
                {"success": True, "message": "Image skipped and served status reset"}
            )
        else:
            return jsonify({"success": False, "message": "Error skipping image"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
