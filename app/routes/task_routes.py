from app import db
from app.models.task import Task
from app.services import slack_bot
from app.services.task_service import TaskService
from flask import Blueprint, jsonify, abort, make_response, request
from datetime import datetime


tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
task_service = TaskService()


@tasks_bp.route("", methods=["GET"])
def read_all_tasks():

    title_query = request.args.get("sort")
    if title_query == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    elif title_query == "asc":
        tasks = Task.query.order_by(Task.title.asc())
    else:
        tasks_response = task_service.get_all_tasks()

    return jsonify(tasks_response), 200


@tasks_bp.route("/<task_id>", methods=["GET"])
def read_one_task(task_id):
    task = task_service.get_task_by_id(task_id)
    return jsonify(task_service.create_a_task_payload(task)), 200


@tasks_bp.route("", methods=["POST"])
def create_task():

    new_task = task_service.create_task_from_JSON(request)

    db.session.add(new_task)
    db.session.commit()

    return jsonify(task_service.create_a_task_payload(new_task)), 201


@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):

    task = task_service.get_task_by_id(task_id)

    title = request.json.get("title", None)
    description = request.json.get("description", None)
    completed_at = request.json.get("completed_at", None)
    if not title or not description:
        return jsonify({"details": "Invalid data"}), 400

    task.title = title
    task.description = description
    task.completed_at = completed_at

    db.session.commit()

    return jsonify(task_service.create_a_task_payload(task)), 200


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_as_complete(task_id):

    task = task_service.get_task_by_id(task_id)

    task.completed_at = datetime.utcnow()

    db.session.commit()

    notification_text = f"Someone just completed the task {task.title}"
    slack_bot.send_notification(notification_text)

    return jsonify(task_service.create_a_task_payload(task)), 200


@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_as_incomplete(task_id):

    task = task_service.get_task_by_id(task_id)

    task.completed_at = None

    db.session.commit()

    return jsonify(task_service.create_a_task_payload(task)), 200


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):

    task = task_service.get_task_by_id(task_id)

    db.session.delete(task)
    db.session.commit()

    return jsonify({"details": f'Task {task_id} "{task.title}" successfully deleted'}), 200
