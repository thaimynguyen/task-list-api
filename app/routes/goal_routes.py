from app import db
from app.models.goal import Goal
from flask import Blueprint, jsonify, abort, make_response, request


goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")


@goals_bp.route("", methods=["GET"])
def read_all_goals():

    title_query = request.args.get("sort")
    if title_query == "desc":
        goals = Goal.query.order_by(goal.title.desc())
    elif title_query == "asc":
        goals = Goal.query.order_by(goal.title.asc())
    else:
        goals = Goal.query

    goals_response = []

    for goal in goals:
        goals_response.append(goal.to_dict()["goal"])

    return jsonify(goals_response), 200


@goals_bp.route("/<goal_id>", methods=["GET"])
def read_one_goal(goal_id):
    goal = get_goal_or_abort(goal_id)
    return jsonify(goal.to_dict()), 200


@goals_bp.route("", methods=["POST"])
def create_goal():

    title = request.json.get("title", None)
    if not title:
        return jsonify({"details": "Invalid data"}), 400

    new_goal = Goal(title=title)

    db.session.add(new_goal)
    db.session.commit()

    return jsonify(new_goal.to_dict()), 201


@goals_bp.route("/<goal_id>", methods=["PUT"])
def update_goal(goal_id):

    goal = get_goal_or_abort(goal_id)

    title = request.json.get("title", None)

    if not title:
        return jsonify({"details": "Invalid data"}), 400

    goal.title = title

    db.session.commit()

    return jsonify(goal.to_dict()["goal"]), 200


def get_goal_or_abort(goal_id):

    try:
        goal_id = int(goal_id)
    except:
        abort(make_response({"message": f"Goal {goal_id} invalid."}, 400))

    goal = Goal.query.get(goal_id)

    if not goal:
        abort(make_response({"message": f"Goal {goal_id} not found."}, 404))

    return goal
