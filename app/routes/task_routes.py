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


@tasks_bp.route("/<task_id>", methods=["GET"])
def read_one_task(task_id):
    task = get_task_or_abort(task_id)
    return jsonify(task.to_JSON_response), 200


@tasks_bp.route("", methods=["POST"])
def create_task():
    title = request.json.get("title", None)
    description = request.json.get("description", None)
    if not title or not description:
        return jsonify({"details": "Invalid data"}), 400

    new_task = Task(title=title,
                    description=description)

    db.session.add(new_task)
    db.session.commit()

    return jsonify(new_task.to_JSON_response), 201


@ tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = get_task_or_abort(task_id)

    title = request.json.get("title", None)
    description = request.json.get("description", None)
    if not title or not description:
        return jsonify({"details": "Invalid data"}), 400

    task.title = title
    task.description = description

    db.session.commit()

    return jsonify(task.to_JSON_response), 200


@ tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = get_task_or_abort(task_id)

    db.session.delete(task)
    db.session.commit()

    return jsonify({"details": f'Task {task_id} "{task.title}" successfully deleted'}), 200


def get_task_or_abort(task_id):
    try:
        task_id = int(task_id)
    except:
        abort(make_response({"message": f"Task {task_id} invalid."}, 400))

    task = Task.query.get(task_id)

    if not task:
        abort(make_response({"message": f"Task {task_id} not found."}, 404))

    return task
