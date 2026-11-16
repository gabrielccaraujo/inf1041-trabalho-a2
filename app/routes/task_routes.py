from flask import Blueprint, jsonify, request

from domain.task import InvalidTaskError
from use_cases.task_use_case import TaskNotFoundError, TaskUseCase


def create_task_blueprint(use_case: TaskUseCase) -> Blueprint:
    bp = Blueprint("tasks", __name__, url_prefix="/tasks")

    @bp.errorhandler(InvalidTaskError)
    def handle_invalid(error):
        return jsonify({"error": str(error)}), 400

    @bp.errorhandler(TaskNotFoundError)
    def handle_not_found(error):
        return jsonify({"error": str(error)}), 404

    @bp.get("")
    def list_tasks():
        return jsonify([task.to_dict() for task in use_case.list()])

    @bp.post("")
    def create_task():
        data = request.get_json(silent=True) or {}
        task = use_case.create(data.get("title", ""))
        return jsonify(task.to_dict()), 201

    @bp.get("/<int:task_id>")
    def get_task(task_id: int):
        return jsonify(use_case.get(task_id).to_dict())

    @bp.patch("/<int:task_id>")
    def update_task(task_id: int):
        data = request.get_json(silent=True) or {}
        task = use_case.update(task_id, title=data.get("title"), done=data.get("done"))
        return jsonify(task.to_dict())

    @bp.delete("/<int:task_id>")
    def delete_task(task_id: int):
        use_case.delete(task_id)
        return "", 204

    return bp
