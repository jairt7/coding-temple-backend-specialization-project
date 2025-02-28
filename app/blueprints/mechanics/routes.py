from . import mechanics_bp
from marshmallow import ValidationError
from flask import request, jsonify
from app.models import Mechanic, db
from .schemas import mechanic_schema, mechanics_schema
from sqlalchemy import select, delete
from app.extensions import limiter, cache


@mechanics_bp.route('/', methods=['POST'])
@limiter.limit('3 per hour')
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400

    new_mechanic = Mechanic(name=mechanic_data['name'], email=mechanic_data['email'], phone=mechanic_data['phone'], salary=mechanic_data['salary'])

    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201

    
@mechanics_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_mechanics():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Mechanic)
        mechanics = db.paginate(query, page=page, per_page=per_page)
        return mechanics_schema.jsonify(mechanics), 200
    
    except:
        query = select(Mechanic)
        result = db.session.execute(query).scalars().all()
        return mechanics_schema.jsonify(result), 200

@mechanics_bp.route('/<int:mechanic_id>', methods=['PUT'])
def update_mechanic(mechanic_id):
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(query).scalars().first()
    print(mechanic)

    if mechanic == None:
        return jsonify({'message': 'Invalid mechanic ID'}), 400

    try:
        mechanic_data = mechanic_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in mechanic_data.items():
        setattr(mechanic, field, value)

    db.session.commit()
    
    return mechanic_schema.jsonify(mechanic), 200


@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
def delete_mechanic(mechanic_id):
    query = delete(Mechanic).where(Mechanic.id == mechanic_id)
    db.session.execute(query)

    db.session.commit()

    return jsonify({'message': f'Successfully deleted mechanic'})

@mechanics_bp.route('/hardest-workers', methods=['GET'])
def hardest_workers():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    mechanics.sort(key=lambda mechanic: len(mechanic.service_tickets), reverse=True)
    return mechanics_schema.jsonify(mechanics)