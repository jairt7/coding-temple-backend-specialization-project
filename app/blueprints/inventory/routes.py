from . import inventory_bp
from marshmallow import ValidationError
from flask import request, jsonify
from app.models import Inventory, db
from .schemas import inventory_schema, inventory_multi_schema
from sqlalchemy import select, delete
from app.extensions import limiter, cache

@inventory_bp.route('/', methods=['POST'])
@limiter.limit('50 per hour')
def add_item():
    try:
        item_data = inventory_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400

    new_item = Inventory(name=item_data['name'], price=item_data['price'])

    db.session.add(new_item)
    db.session.commit()

    return inventory_schema.jsonify(new_item), 201

    
@inventory_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_inventory():
    page = request.args.get('page')
    per_page = request.args.get('per_page')
    if page == None or per_page == None:
        query = select(Inventory)
        result = db.session.execute(query).scalars().all()
        print(result)
        return inventory_multi_schema.jsonify(result), 200
    else:
        page = int(page)
        per_page = int(per_page)
        query = select(Inventory)
        inventory = db.paginate(query, page=page, per_page=per_page)
        return inventory_multi_schema.jsonify(inventory), 200


@inventory_bp.route('/<int:item_id>', methods=['PUT'])
def update_inventory(item_id):
    query = select(Inventory).where(Inventory.id == item_id)
    item = db.session.execute(query).scalars().first()
    print(item)

    if item == None:
        return jsonify({'message': 'Invalid item ID'}), 400

    try:
        item_data = inventory_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in item_data.items():
        setattr(item, field, value)

    db.session.commit()
    
    return inventory_schema.jsonify(item), 200


@inventory_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    query = select(Inventory).where(Inventory.id == item_id)
    item = db.session.execute(query).scalars().first()

    if not item:
        return jsonify({'message': 'Item not found'}), 400
    
    query = delete(Inventory).where(Inventory.id == item_id)
    db.session.execute(query)
    db.session.commit()

    return jsonify({'message': f'Successfully deleted item'})