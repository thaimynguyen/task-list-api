from app import db
from app.models.goal import Goal
from app.models.task import Task
from app.services.task_service import TaskService
from app.routes.utils.helper import get_or_abort
from flask import Blueprint, jsonify, request


goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")
task_service = TaskService()


@goals_bp.route("", methods=["GET"])
def read_all_goals():

    title_query = request.args.get("sort")
    if title_query == "desc":
        goals = Goal.query.order_by(Goal.title.desc())
    elif title_query == "asc":
        goals = Goal.query.order_by(Goal.title.asc())
    else:
        goals = Goal.query

    goals_response = [goal.to_dict()["goal"] for goal in goals]

    return jsonify(goals_response), 200


@goals_bp.route("/<goal_id>", methods=["GET"])
def read_one_goal(goal_id):

    goal = get_or_abort(Goal, goal_id)

    return jsonify(goal.to_dict()), 200


@goals_bp.route("", methods=["POST"])
def create_goal():

    new_goal = Goal.from_JSON_or_abort()

    db.session.add(new_goal)
    db.session.commit()

    return jsonify(new_goal.to_dict()), 201


@goals_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):

    goal = get_or_abort(Goal, goal_id)

    title = request.json.get("title", None)

    if not title:
        return jsonify({"details": "Invalid data"}), 400

    goal.title = title

    db.session.commit()

    return jsonify(goal.to_dict()["goal"]), 200


@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):

    goal = get_or_abort(Goal, goal_id)

    db.session.delete(goal)
    db.session.commit()

    return jsonify({"details": f'Goal {goal_id} "{goal.title}" successfully deleted'}), 200


@goals_bp.route("/<goal_id>/tasks", methods=["POST"])
def post_task_ids_to_a_goal(goal_id):

    goal = get_or_abort(Goal, goal_id)

    task_ids = request.json.get("task_ids", None)
    if not task_ids:
        return jsonify({"details": "Invalid data"}), 400

    # update each task with goal.goal_id
    for task_id in task_ids:
        task = Task.query.get(task_id)
        task.goal_id = goal_id

    db.session.commit()

    rsp = {
        "id": goal.goal_id,
        "task_ids": task_ids
    }

    return jsonify(rsp), 200


@goals_bp.route("/<goal_id>/tasks", methods=["GET"])
def get_tasks_of_one_goal(goal_id):

    goal = get_or_abort(Goal, goal_id)

    payload = goal.to_dict()["goal"]
    payload["tasks"] = [task_service.convert_task_to_dict(
        task)["task"] for task in goal.tasks]

    return jsonify(payload), 200
