from app import db


class Task(db.Model):

    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.goal_id"), nullable=True)
    goal = db.relationship("Goal", back_populates="tasks", lazy=True)


    def to_dict(self):
        payload = {
            "task": {
                "id": self.task_id,
                "title": self.title,
                "description": self.description,
                "is_complete": False
            }
        }
        if self.completed_at:
            payload["task"]["is_complete"] = True
        if self.goal_id:
            payload["task"]["goal_id"] = self.goal_id
        return payload

