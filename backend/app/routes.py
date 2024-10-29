from flask import Blueprint, render_template, request, jsonify, session
import uuid
from .firestore import FirestoreUtils

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


@main.route("/get_session_id", methods=["GET"])
def get_session_id():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())  # Generate a unique ID
    return jsonify({"session_id": session["user_id"]})


@main.route("/update_label", methods=["POST"])
def update_label():
    try:
        data = request.get_json()
        image_path = data.get("image_path")
        label = data.get("label")
        user_id = data.get("user_id")
        # session_id = data.get('session_id') figure out how to do this

        firestore_utils = FirestoreUtils()

        if label:
            firestore_utils.label_room_type(image_path, label, user_id)
            return jsonify({"success": True})
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
        result = firestore_utils.reset_image_served(image_id)

        if result:
            return jsonify(
                {"success": True, "message": "Image skipped and served status reset"}
            )
        else:
            return jsonify({"success": False, "message": "Error skipping image"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
