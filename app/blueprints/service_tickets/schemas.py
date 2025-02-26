from app.models import ServiceTicket
from app.extensions import ma
from marshmallow import fields

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    customer = fields.Nested("CustomerSchema")
    mechanics = fields.Nested("MechanicSchema", many=True)
    class Meta:
        model = ServiceTicket
        fields = ('id', 'VIN', 'service_date', 'service_desc', 'customer_id', 'mechanic_ids', 'mechanics', 'customer')
    
    id = ma.auto_field()
    VIN = ma.auto_field()
    service_date = ma.auto_field()
    service_desc = ma.auto_field()
    customer_id = ma.auto_field()

class EditServiceTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)
    class Meta:
        fields = ("add_mechanic_ids", "remove_mechanic_ids")
    

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_service_ticket_schema = EditServiceTicketSchema()