from functools import wraps

from flask import Blueprint, current_app, g, jsonify, request

from domain.rules import BusinessError, cents_to_money

api = Blueprint("api", __name__, url_prefix="/api/v1")


def service():
    return current_app.extensions["rachai_service"]


def body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise BusinessError("Envie um objeto JSON valido.")
    return data


def auth_required(route):
    @wraps(route)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        token = header.removeprefix("Bearer ").strip() if header.startswith("Bearer ") else ""
        g.user = service().current_user(token)
        return route(*args, **kwargs)
    return wrapper


def user_json(user):
    return {"id": user.id, "name": user.name, "email": user.email}


def group_json(group):
    return {"id": group.id, "name": group.name, "category": group.category,
            "owner_id": group.owner_id, "invite_code": group.invite_code}


def expense_json(expense, splits):
    return {"id": expense.id, "group_id": expense.group_id,
            "description": expense.description, "amount": cents_to_money(expense.amount_cents),
            "paid_by": expense.paid_by, "category": expense.category,
            "occurred_on": expense.occurred_on,
            "splits": [{"user_id": split.user_id, "amount": cents_to_money(split.amount_cents)}
                       for split in splits]}


@api.post("/auth/register")
def register():
    data = body()
    user = service().register_user(data.get("name"), data.get("email"), data.get("password"))
    return jsonify(user_json(user)), 201


@api.post("/auth/login")
def login():
    data = body()
    token, user = service().login(data.get("email"), data.get("password"))
    return jsonify({"token": token, "token_type": "Bearer", "user": user_json(user)})


@api.get("/auth/me")
@auth_required
def me():
    return jsonify(user_json(g.user))


@api.post("/groups")
@auth_required
def create_group():
    data = body()
    group = service().create_group(g.user.id, data.get("name"), data.get("category", "Outros"))
    return jsonify(group_json(group)), 201


@api.get("/groups")
@auth_required
def list_groups():
    return jsonify({"groups": [group_json(group) for group in service().list_groups(g.user.id)]})


@api.post("/groups/join")
@auth_required
def join_group():
    group = service().join_group(g.user.id, body().get("invite_code"))
    return jsonify(group_json(group))


@api.get("/groups/<group_id>")
@auth_required
def get_group(group_id):
    group, members = service().get_group(g.user.id, group_id)
    return jsonify({**group_json(group), "members": [user_json(user) for user in members]})


@api.post("/groups/<group_id>/expenses")
@auth_required
def create_expense(group_id):
    data = body()
    expense, splits = service().create_expense(
        g.user.id, group_id, data.get("description"), data.get("amount"),
        data.get("paid_by"), data.get("participant_ids"),
        data.get("category", "Outros"), data.get("occurred_on"))
    return jsonify(expense_json(expense, splits)), 201


@api.get("/groups/<group_id>/expenses")
@auth_required
def list_expenses(group_id):
    items = service().list_expenses(g.user.id, group_id)
    return jsonify({"expenses": [expense_json(expense, splits) for expense, splits in items]})


@api.get("/groups/<group_id>/balances")
@auth_required
def balances(group_id):
    items = service().balances(g.user.id, group_id)
    return jsonify({"balances": [
        {"user_id": item["user_id"], "name": item["name"],
         "balance": cents_to_money(item["balance_cents"])} for item in items]})
