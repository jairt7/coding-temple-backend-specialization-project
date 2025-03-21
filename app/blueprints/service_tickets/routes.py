from marshmallow import ValidationError
from flask import request, jsonify
from . import service_ticket_bp
from .schemas import service_ticket_schema, service_tickets_schema, edit_service_ticket_schema, add_inventory_item_schema, remove_inventory_item_schema
from app.models import db, ServiceTicket, Mechanic, Customer, Inventory, ServiceInventory
from sqlalchemy import select, delete


@service_ticket_bp.route('/', methods=['POST'])
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer = db.session.get(Customer, service_ticket_data['customer_id'])
    if not customer:
        return jsonify({'message': 'Invalid customer ID'}), 400

    new_service_ticket = ServiceTicket(VIN=service_ticket_data['VIN'], service_date=service_ticket_data['service_date'], \
    service_desc=service_ticket_data['service_desc'], customer_id=service_ticket_data['customer_id'])

    mechanic_ids = service_ticket_data.get('mechanic_ids', [])

    if mechanic_ids:
        mechanics = db.session.scalars(select(Mechanic).where(Mechanic.id.in_(mechanic_ids))).all()
        new_service_ticket.mechanics.extend(mechanics)

    db.session.add(new_service_ticket)
    db.session.commit()
    
    return service_ticket_schema.jsonify(new_service_ticket)

@service_ticket_bp.route('/', methods=['GET'])
def get_service_tickets():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(ServiceTicket)
        tickets = db.session.scalars(query).paginate(page=page, per_page=per_page)
        return service_tickets_schema.jsonify(tickets), 200
    
    except:
        query = select(ServiceTicket)
        result = db.session.execute(query).scalars().all()
        return service_tickets_schema.jsonify(result), 200

@service_ticket_bp.route('/<int:ticket_id>', methods=['PUT'])
def edit_service_ticket(ticket_id):
    
    try:
        service_ticket_edits = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    query = select(ServiceTicket).where(ServiceTicket.id == ticket_id)
    service_ticket = db.session.execute(query).scalars().first()
    
    if not service_ticket:
        return jsonify({'message': 'Service ticket not found'}), 404

    for mechanic_id in service_ticket_edits['add_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)

    for mechanic_id in service_ticket_edits['remove_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)


    db.session.commit()
    
    return service_ticket_schema.jsonify(service_ticket), 200


@service_ticket_bp.route('/<int:ticket_id>', methods=['DELETE'])
def delete_service_ticket(ticket_id):
    query = delete(ServiceTicket).where(ServiceTicket.id == ticket_id)
    db.session.execute(query)

    db.session.commit()

    return jsonify({'message': f'Successfully deleted service ticket'}), 200

@service_ticket_bp.route('/<int:ticket_id>/add-item/<int:item_id>', methods=['POST'])
def add_inventory_item(ticket_id, item_id):

    ticket = db.session.get(ServiceTicket, ticket_id)
    item = db.session.get(Inventory, item_id)
    if not ticket or not item:
        return jsonify({'message': 'Ticket or item not found'})
    
    added_item = db.session.execute(select(ServiceInventory).where((ServiceInventory.service_id == ticket_id) & \
    (ServiceInventory.item_id == item_id))).scalars().first()

    if added_item:
        added_item.quantity += 1
    else:
        added_item = ServiceInventory(service_id=ticket_id, item_id=item_id, quantity=1)
        db.session.add(added_item)
    
    db.session.commit()

    return jsonify({'message': 'Item added:', 'ticket_id': ticket_id, 'item_id': item_id, 'quantity': added_item.quantity}), 200

@service_ticket_bp.route('/<int:ticket_id>/remove-item/<item_id>', methods=['POST'])
def remove_inventory_item(ticket_id, item_id):

    ticket = db.session.get(ServiceTicket, ticket_id)
    item = db.session.get(Inventory, item_id)

    if not ticket or not item:
        return jsonify({'message': 'Ticket or item not found'})
    
    removed_item = db.session.execute(select(ServiceInventory).where((ServiceInventory.service_id == ticket_id) & 
    (ServiceInventory.item_id == item_id))).scalars().first()

    if not removed_item:
        return jsonify({'message': 'Item not found'})
    if removed_item.quantity > 1:
        removed_item.quantity -= 1
    elif removed_item.quantity == 1:
        db.session.delete(removed_item)
    else:
        return jsonify({'message': "I don't know how you got this error"})

    db.session.commit()

    return jsonify({'message': 'Item removed', 'ticket_id': ticket_id, 'item_id': item_id, 'quantity': removed_item.quantity if removed_item.quantity > 0 else 0}), 200


'''
I know this isn't required, but I think it's a good idea to have a reference for how to do this.

@service_ticket_bp.route('/search', methods=['GET'])
def search_tickets():
    ticket_detail = request.args.get("ticket-detail")
    query = select(ServiceTicket).where(ServiceTicket.service_desc.like(f'%{ticket_detail}%'))
    tickets = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(tickets)

'''