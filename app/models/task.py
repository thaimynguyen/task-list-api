from app import db


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    completed_at = db.Column(db.DateTime)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.goal_id'))

    def to_json(self):
        if self.completed_at:
            completed = True
        else:
            completed = False
        task_dict = {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "is_complete": completed,
        }

        if self.goal_id:
            task_dict["goal_id"] = self.goal_id

        return task_dict
