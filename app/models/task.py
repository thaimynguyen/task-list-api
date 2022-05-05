from app import db


class Task(db.Model):

    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime, nullable=True)

    @property
    def to_JSON_response(self):
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
        return payload
