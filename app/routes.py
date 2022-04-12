from datetime import datetime
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import Response
from flask import make_response
from sqlalchemy.types import DateTime
from sqlalchemy.sql.functions import now
import requests
import os

from .models.task import Task
from .models.goal import Goal
from app import db

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")
root_bp = Blueprint("root_bp", __name__)

SLACK_API_URL = "https://slack.com/api/chat.postMessage"
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]


@root_bp.route("/", methods=["GET"])
def root():
    return {
        "name": "Chris Mc",
        "message": "Fun project",
    }


@tasks_bp.route("", methods=["GET"])
def index():
    sort_method = request.args.get('sort')

    if not sort_method:
        tasks = Task.query.all()
    elif sort_method == "asc":
        tasks = Task.query.order_by(Task.title.asc()).all()
    elif sort_method == "desc":
        tasks = Task.query.order_by(Task.title.desc()).all()
    else:
        tasks = Task.query.all()

    tasks_response = []
    for task in tasks:
        tasks_response.append(task.to_json())

    return jsonify(tasks_response)


@tasks_bp.route("", methods=["POST"])
def create():
    request_body = request.get_json()

    if not "title" in request_body or not "description" in request_body:  # or \
        # not "completed_at" in request_body:
        return jsonify({
            "details": "Invalid data"
        }), 400

    new_task = Task(title=request_body["title"],
                    description=request_body["description"]
                    )
    if "completed_at" in request_body:
        new_task.completed_at = request_body["completed_at"]

    db.session.add(new_task)
    db.session.commit()

    return {
        "task": new_task.to_json()
    }, 201


@tasks_bp.route("/<task_id>", methods=["GET"])
def show(task_id):
    task = Task.query.get(task_id)

    if task:
        return {
            "task": task.to_json()
        }
    else:
        return make_response(jsonify(None), 404)


@tasks_bp.route("/<task_id>", methods=["PUT"])
def update(task_id):
    task = Task.query.get(task_id)
    if not task:
        return "", 404

    request_body = request.get_json()
    task.title = request_body["title"]
    task.description = request_body["description"]
    # if request_body["completed_at"]:
    #     task.completed_at = datetime.utcnow

    db.session.add(task)
    db.session.commit()

    return {
        "task": task.to_json()
    }, 200


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return "", 404

    db.session.delete(task)
    db.session.commit()

    return {
        "details": f"Task {task_id} \"{task.title}\" successfully deleted"
    }, 200


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task = Task.query.get(task_id)
    if not task:
        return "", 404

    task.completed_at = now()

    db.session.add(task)
    db.session.commit()
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
    }
    if task.completed_at:
        data = {
            "channel": "instructors",
            "text": f"Task {task.title} has been marked complete",
        }
    else:
        data = {
            "channel": "general",
            "text": f"Task {task.title} has been marked incomplete",
        }
    # r = requests.post(SLACK_API_URL, headers=headers, data=data )

    return {
        "task": task.to_json()
    }, 200


@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task = Task.query.get(task_id)
    if not task:
        return "", 404

    task.completed_at = None

    db.session.add(task)
    db.session.commit()
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
    }

    return {
        "task": task.to_json()
    }, 200


@goals_bp.route("", methods=["GET"])
def goals_index():
    goals = Goal.query.all()
    goals_json = []

    for goal in goals:
        goals_json.append(goal.to_json())

    return jsonify(goals_json)


@goals_bp.route("/<goal_id>", methods=["GET"])
def goals_show(goal_id):
    goal = Goal.query.get(goal_id)

    if goal:
        return {
            "goal": goal.to_json()
        }
    else:
        return make_response(jsonify(None), 404)


@goals_bp.route("/<goal_id>", methods=["PUT"])
def goals_update(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return "", 404

    request_body = request.get_json()
    goal.title = request_body["title"]

    db.session.add(goal)
    db.session.commit()

    return {
        "goal": goal.to_json()
    }, 200


@goals_bp.route("", methods=["POST"])
def goals_create():
    request_body = request.get_json()

    if not "title" in request_body:
        return jsonify({
            "details": "Invalid data"
        }), 400

    new_goal = Goal(title=request_body["title"])

    db.session.add(new_goal)
    db.session.commit()

    return {
        "goal": new_goal.to_json()
    }, 201


@goals_bp.route("/<goal_id>", methods=["DELETE"])
def goals_delete(goal_id):
    goal = Goal.query.get(goal_id)
    if not goal:
        return "", 404

    db.session.delete(goal)
    db.session.commit()

    return {
        "details": f"Goal {goal_id} \"{goal.title}\" successfully deleted"
    }, 200


@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def goal_tasks(goal_id):
    goal = Goal.query.get(goal_id)

    if not goal:
        return "", 404

    answer = {
        "id": goal.goal_id,
        "title": goal.title,
        "tasks": [],
    }

    for task in goal.tasks:
        answer["tasks"].append(task.to_json())

    return answer, 200


@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def goal_tasks_post(goal_id):
    goal = Goal.query.get(goal_id)

    if not goal:
        return "", 404

    request_body = request.get_json()

    answer = {
        "id": goal.goal_id,
        "task_ids": request_body["task_ids"],
    }

    for task_id in request_body["task_ids"]:
        task = Task.query.get(task_id)
        if not task:
            return "", 404

        goal.tasks.append(task)

    db.session.commit()

    return answer, 200
