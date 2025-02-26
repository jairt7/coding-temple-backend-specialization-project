from marshmallow import ValidationError
from flask import request, jsonify
from . import service_ticket_bp
from .schemas import service_ticket_schema, service_tickets_schema, edit_service_ticket_schema  
from app.models import ServiceTicket, db, Mechanic, Customer
from sqlalchemy import select, delete
from datetime import date


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

    mechanic_ids = service_ticket_data.get('mechanics', [])

    for mechanic_id in mechanic_ids:
        query = select(Mechanic).where(Mechanic.id==mechanic_id)
        mechanic = db.session.execute(query).scalars().first()
        if mechanic:
            new_service_ticket.mechanics.append(mechanic)
        else:
            return jsonify({'message': 'invalid mechanic id'}), 400
    
    db.session.add(new_service_ticket)
    db.session.commit()
    
    return service_ticket_schema.jsonify(new_service_ticket)

@service_ticket_bp.route('/', methods=['GET'])
def get_service_tickets():
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
    
    for mechanic_id in service_ticket_edits['add_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic not in service_ticket:
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