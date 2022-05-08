from app import db
from flask import request, abort, make_response

class Goal(db.Model):

    goal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, unique=True, nullable=False)
    tasks = db.relationship("Task", back_populates="goal", lazy=True)

    def to_dict(self):
        return {
            "goal": {
                "id": self.goal_id,
                "title": self.title
            }
        }

    @staticmethod
    def from_JSON_or_abort():

        if not request.is_json:
            abort(make_response({"message": "Missing JSON request body"}, 400))

        request_body = request.get_json()

        title = request_body.get("title", None)

        if not title:
            abort(make_response({"details": "Invalid data"}, 400))

        return Goal(title=title)
