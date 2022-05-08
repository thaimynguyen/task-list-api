from app.models.task import Task
from flask import Flask, abort, make_response


class TaskService:

    def create_task_from_JSON(self, request) -> Task:
        payload = self.get_JSON_from_request(request)
        title = payload.get("title", None)
        description = payload.get("description", None)
        completed_at = payload.get("completed_at", None)
        goal_id = payload.get("goal_id", None)

        if not title or not description:
            abort(make_response({"details": "Invalid data"}, 400))

        return Task(title=title,
                    description=description,
                    completed_at=completed_at,
                    goal_id=goal_id)

    def convert_task_to_dict(self, task: Task) -> dict:
        task_as_dict = {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at is not None
        }

        if task.goal_id:
            task_as_dict["goal_id"] = task.goal_id

        return task_as_dict

    def create_a_task_payload(self, task):
        return {"task": self.convert_task_to_dict(task)}

    def get_task_by_id(self, task_id) -> Task:
        try:
            task_id = int(task_id)
        except ValueError:
            abort(make_response({"message": f"Task {task_id} invalid."}, 400))

        task = Task.query.get(task_id)

        if not task:
            abort(make_response(
                {"message": f"Task {task_id} not found."}, 404))

        return task

    def get_all_tasks(self):
        return [self.convert_task_to_dict(task) for task in Task.query]

    def get_JSON_from_request(self, request):
        if not request.is_json:
            abort(make_response({"message": "Missing JSON request body"}, 400))

        return request.get_json()
