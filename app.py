"""
Project:   task-manager
File:      app.py
Author:    Josiah De Leon
Date:      2026-07-30

Description: application built to learn how apis/auth/sessions work
"""

import os

import database as db
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

def create_app(test_config=None) -> Flask: # App factory for dynamic sessions
    """Creates an instance of the application.

    :param test_config: dictionary (optional), testing configuration for app
        instance.
    :return: app (obj), fully functioning app.
    """
    app = Flask(__name__)
    load_dotenv()
    
    key = os.getenv('JWT_SECRET_KEY')
    if key is None:
        raise RuntimeError("JWT key missing.")

    app.config.from_mapping({
        "DATABASE": "task_manager.db",
        "JWT_SECRET_KEY": key
        })
    jwt = JWTManager(app)
    
    if test_config:
        app.config.update(test_config)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #             NON-PERSISTENT IMPLEMENTATION FOR INITIAL CRUD            #
    # tasks = [                                                             #
    #         {"id": 1, "title": "workout", "completed": False},            #
    #         {"id": 2, "title": "study", "completed": False},              #
    #         {"id": 3, "title": "budget", "completed": True},              #
    #         {"id": 4, "title": "email Sara", "completed": False},         #
    #         {"id": 5, "title": "work on mle unit 9", "completed": False}, #
    #         {"id": 6, "title": "java 1", "completed": False}              #
    #     ]                                                                 #
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    # -- GET --
    @app.route("/health", methods=["GET"])
    def health_status():
        """Checks the health of the API connection.

        :return: JSON, verification that route is successful.
        """
        return jsonify({"status": "ok"})


    @app.route("/tasks", methods=["GET"])
    @jwt_required()
    def get_tasks():
        """Retrieves an existing cluster of tasks according to user_id.

        :return: JSON, full contents of tasks associated with the user_id.
        """
        user_id = int(get_jwt_identity())
        return jsonify(db.get_user_tasks(user_id))


    # -- POST --
    @app.route("/tasks", methods=["POST"])
    @jwt_required()
    def add_task():
        """Adds a new task to the Tasks according to the user logged in.

        :return: JSON, contents for newly added task.
        """
        user_id = int(get_jwt_identity())
        data = request.get_json(silent=True)

        if data is None:
            return jsonify({"error": "Request body must be valid JSON."}), 400
        elif not isinstance(data, dict):
            return jsonify({"error": "Request body must be a dictionary."}), 400
        elif "title" not in data:
            return jsonify({"error": "title is required."}), 400
        elif not isinstance(data["title"], str):
            return jsonify({"error": "title has to be string."}), 400
        elif data["title"].strip() == "":
            return jsonify({"error": "title cannot be empty"}), 400
        elif db.get_single_task(data["title"].strip(), user_id) != []:
            return jsonify({"error": "task already exists"}), 400
        else:
            new_task = {
                "user_id": user_id,
                "title": data["title"].strip(),
                "completed": False
            } 

            new_id = db.create_tasks(new_task)
            task = f"({new_id}).{new_task["title"]} was added."

            return jsonify({"status": task}), 201

    
    @app.route("/signup", methods=["POST"])
    def create_user():
        """Creates a new user with email and password.

        :return: JSON, verification that user was added successfully.
        """
        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({"error": "Request body must be valid JSON."}), 400
        elif not isinstance(data, dict):
            return jsonify({"error": "Request body must be a dictionary."}), 400
        elif "email" not in data or "password" not in data:
            return jsonify({"error": "Required fields are missing."}), 400
        elif not isinstance(data["email"], str) or not isinstance(data["password"], str):
            return jsonify({"error": "Fields contain unsupported datatypes."}), 400
        elif data["email"].strip() == "" or data["password"].strip() =="":
            return jsonify({"error": "Fields cannot be empty."}), 400
        elif len(data["password"]) < 8:
            return jsonify({"error": "Password has to be longer than 8 letters."}), 400
        elif not db.is_valid_email(data["email"]):
            return jsonify({"error": "Invalid email address."}), 400

        email = data.get("email")
        password = data.get("password")

        if email and password:
            if db.get_user_by_email(email):
                return jsonify({"error": "Email already exists."}), 409
        
            password_hash = generate_password_hash(password)
            db.create_user(email=email, password_hash=password_hash)
            status = "user successfully created."
            return jsonify({"status": status}), 201
        else:
            return jsonify({"error": "Invalid request."}), 400
    

    @app.route("/login", methods=["POST"])
    def login():
        """User login by username and password.

        :return: JSON, access token for jwt access.
        """
        data = request.get_json(silent=True) or {}
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Incorrect credentials"}), 400

        user = db.get_user_by_email(email)
        if user and check_password_hash(user["password_hash"], password):
            token = create_access_token(identity=str(user["id"]))
            return jsonify({"access_token": token})

        return jsonify({"error": "Unauthorized access"}), 401
        
        
    # -- PUT --
    @app.route("/tasks/<int:task_id>", methods=["PUT"])
    @jwt_required()
    def update_task(task_id: int):
        """Updates tasks according to id where tasks are scoped to the user
            that's logged in.

        :param task_id: int, id associated with existing task.
        :return: JSON, full contents of task associated with the id.
        """
        user_id = int(get_jwt_identity())
        data = request.get_json(silent=True)

        if data is None:
            return jsonify({"error": "Request body must be valid JSON."}), 400
        elif not isinstance(data, dict):
            return jsonify({"error": "Request body must be valid dictionary."}), 400
        elif "completed" not in data:
            return jsonify({"error": "Required fields are missing."}), 400
        elif not isinstance(data["completed"], bool):
            return jsonify({"error": "completed must be a boolean value."}), 400

        parse_task = {
            "user_id": user_id,
            "id": task_id,
            "completed": data["completed"]
        }
        
        valid = db.update_completion(parse_task)
        if valid:
            return jsonify(parse_task)
        return jsonify({"error": "Task not found"}), 404


    # -- DELETE --
    @app.route("/tasks/<int:task_id>", methods=["DELETE"])
    @jwt_required()
    def remove_task(task_id: int):
        """Removes a task owned by a user.

        :param task_id: int, id associate with existing task.
        :return: JSON, verification that the task was sucessfully removed.
        """
        user_id = int(get_jwt_identity())
        if db.remove_tasks(task_id=task_id, user_id=user_id):
            return "", 204
        return jsonify({"error": "Task not found"}), 404
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
