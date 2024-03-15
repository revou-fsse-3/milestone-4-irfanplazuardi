from flask import Blueprint, render_template, request, jsonify
from sqlalchemy.orm import sessionmaker
from connectors.mysql_connector import engine
from models.transaction import Transaction
from sqlalchemy import select, or_
from flask_login import current_user, login_required

transaction_routes = Blueprint('transaction_routes', __name__)

@transaction_routes.route("/transactions", methods=['GET'])
@login_required
def get_transactions():
    response_data = dict()

    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()

    try:
        transactions = session.query(Transaction).all()
        response_data = {"transactions": [transaction.serialize() for transaction in transactions]}

    except Exception as e:
        print(e)
        return jsonify({"message": "Something went wrong when fetching transactions"}), 500
    finally:
        session.close()

    return jsonify(response_data)

@transaction_routes.route("/transactions/<id>", methods=['GET'])
@login_required
def get_transaction_by_id(id):
    response_data = dict()

    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()

    try:
        transaction = session.query(Transaction).filter(Transaction.id == id).first()
        if transaction is None:
            return jsonify({"message": "Transaction not found"}), 404
        response_data['transaction'] = transaction

    except Exception as e:
        print(e)
        return jsonify({"message": "Something went wrong when fetching transaction"}), 500

    return jsonify(response_data)

@transaction_routes.route("/transactions", methods=['POST'])
@login_required
def create_transaction():
    try:
        data = request.form
        if not all(key in data for key in ('from_account_id', 'to_account_id', 'type', 'amount', 'description')):
            return jsonify({"message": "Missing required fields"}), 400
        
        connection = engine.connect()
        Session = sessionmaker(connection)
        session = Session()

        new_transaction = Transaction(
            from_account_id=data['from_account_id'],
            to_account_id=data['to_account_id'],
            type=data['type'],
            amount=data['amount'],
            description=data['description']
        )

        session.add(new_transaction)
        session.commit()

        return jsonify({"message": "Transaction created successfully", "transaction_id": new_transaction.id}), 201

    except Exception as e:
        print(e)
        return jsonify({"message": "Failed to create transaction"}), 500
