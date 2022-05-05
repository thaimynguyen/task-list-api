from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, abort, make_response, request

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")


@ tasks_bp.route("", methods=["GET"])
def read_all_tasks():
    tasks_response = []
    for task in Task.query:
        tasks_response.append(task.to_JSON_response["task"])
    return jsonify(tasks_response), 200
