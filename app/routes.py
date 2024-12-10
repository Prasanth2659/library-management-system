from flask import Blueprint, request, jsonify
from app.models import db, User, Book, BorrowRequest
from flask_httpauth import HTTPBasicAuth

bp = Blueprint('routes', __name__)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return user
    return None

# Librarian APIs
@bp.route('/users', methods=['POST'])
@auth.login_required
def create_user():
    data = request.get_json()
    if not data or not 'email' in data or not 'password' in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'User already exists'}), 400
    
    user = User(email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@bp.route('/requests', methods=['GET'])
@auth.login_required
def view_all_requests():
    requests = BorrowRequest.query.all()
    return jsonify([req.to_dict() for req in requests]), 200

@bp.route('/requests/<int:request_id>', methods=['PUT'])
@auth.login_required
def approve_or_deny_request(request_id):
    data = request.get_json()
    if not data or not 'status' in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    request = BorrowRequest.query.get(request_id)
    if not request:
        return jsonify({'error': 'Request not found'}), 404

    request.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Request status updated successfully'}), 200

@bp.route('/users/<int:user_id>/history', methods=['GET'])
@auth.login_required
def user_borrow_history(user_id):
    requests = BorrowRequest.query.filter_by(user_id=user_id).all()
    return jsonify([req.to_dict() for req in requests]), 200

# Library User APIs
@bp.route('/books', methods=['GET'])
def list_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200

@bp.route('/requests', methods=['POST'])
@auth.login_required
def request_borrow():
    data = request.get_json()
    if not data or not 'book_id' in data or not 'start_date' in data or not 'end_date' in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Check for overlapping dates
    existing_requests = BorrowRequest.query.filter_by(book_id=data['book_id']).filter(
        (BorrowRequest.start_date <= data['end_date']) & (BorrowRequest.end_date >= data['start_date'])
    ).all()
    if existing_requests:
        return jsonify({'error': 'Book already borrowed for given dates'}), 400
    
    borrow_request = BorrowRequest(
        user_id=auth.current_user().id,
        book_id=data['book_id'],
        start_date=data['start_date'],
        end_date=data['end_date']
    )
    db.session.add(borrow_request)
    db.session.commit()
    return jsonify({'message': 'Borrow request submitted'}), 201

@bp.route('/users/me/history', methods=['GET'])
@auth.login_required
def personal_borrow_history():
    requests = BorrowRequest.query.filter_by(user_id=auth.current_user().id).all()
    return jsonify([req.to_dict() for req in requests]), 200
