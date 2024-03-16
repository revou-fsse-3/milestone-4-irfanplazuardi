from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from connectors.mysql_connector import engine
from sqlalchemy.orm import sessionmaker
from models.account import Account
from models.user import User
from sqlalchemy.exc import IntegrityError
from flask_login import current_user, login_required

from cerberus import Validator

account_routes = Blueprint('account_routes', __name__)

Session = sessionmaker(bind=engine)

@account_routes.route("/accounts", methods=['GET'])
@login_required
def get_accounts():

    response_data = dict()

    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()
    try:
        accounts = session.query(Account).filter(Account.user_id == current_user.id).all()
        response_data = {"accounts": [account.serialize() for account in accounts]}
        return jsonify(response_data)
    except Exception as e:
        print(e)
        return jsonify({"error": "Error Processing Data"}), 500
    finally:
        session.close()

@account_routes.route("/accounts/<int:id>", methods=['GET'])
@login_required
def get_account_by_id(id):
    try:
        session = Session()
        account = session.query(Account).filter(Account.id == id, Account.user_id == current_user.id).first()
        if not account:
            return jsonify({"message": "Account not found"}), 404
        return jsonify({"account": account.serialize()})
    except Exception as e:
        print("An error occurred:", e)
        return jsonify({"error": "Error Processing Data"}), 500
    finally:
        session.close()

@account_routes.route("/accounts", methods=['POST'])
@login_required
def create_account():

    user_id = current_user.id
    account_type = request.form['account_type']
    account_number = request.form['account_number']
    balance = request.form['balance']

    print(user_id)
    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()

    new_account = Account()

    new_account.user_id = user_id
    new_account.account_type = account_type
    new_account.account_number = account_number
    new_account.balance = balance

    try:
        session.add(new_account)
        session.commit()
        return jsonify({"message": "Success insert data"}), 201
    
    except IntegrityError as e:
        session.rollback()
        print(e)
        return jsonify({"message": "Duplicate account number"}), 409

    except Exception as e:
        session.rollback()
        print(e)
        return jsonify({"message": "Fail to insert data"}), 500
    finally:
        session.close()

@account_routes.route("/accounts/<int:id>", methods=['PUT'])
@login_required
def update_account(id):
    account_type = request.form['account_type']
    account_number = request.form['account_number']
    balance = request.form['balance']

    connection = engine.connect()
    Session = sessionmaker(connection)
    session = Session()

    match_account = session.query(Account).filter(Account.id == id).first()

    try:
        match_account.account_type = account_type
        match_account.account_number = account_number
        match_account.balance = balance

        session.add(match_account)
        session.commit()
        return jsonify({"message": "Success updating data"}), 201
    
    except Exception as e:
        session.rollback()
        print(e)
        return jsonify({"message": "Fail to update data"}), 500
    finally:
        session.close()

@account_routes.route("/accounts/<int:id>", methods=['DELETE'])
@login_required
def delete_account(id):
    try:
        session = Session()
        account = session.query(Account).filter(Account.id == id).first()
        if not account:
            return jsonify({"message": "Account not found"}), 404

        session.delete(account)
        session.commit()
        return jsonify({"message": "Success delete data"})
    except Exception as e:
        session.rollback()
        print(e)
        return jsonify({"message": "Fail to delete data"}), 500
    finally:
        session.close()
