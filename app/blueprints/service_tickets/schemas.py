from app.models import ServiceTicket
from app.extensions import ma
from marshmallow import fields

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    customer = fields.Nested("CustomerSchema")
    mechanics = fields.Nested("MechanicSchema", many=True)
    inventory = fields.Nested("ServiceInventorySchema", many=True)

    class Meta:
        model = ServiceTicket
        fields = ('id', 'VIN', 'service_date', 'service_desc', 'customer_id', 'mechanic_ids', 'mechanics', 'customer', 'inventory', 'inventory_ids')
        include_fk = True

    id = ma.auto_field()
    VIN = ma.auto_field()
    service_date = ma.auto_field()
    service_desc = ma.auto_field()
    customer_id = ma.auto_field()

class EditServiceTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int())
    remove_mechanic_ids = fields.List(fields.Int())
    class Meta:
        fields = ("add_mechanic_ids", "remove_mechanic_ids")

class AddInventoryItemSchema(ma.Schema):
    add_inventory_items = fields.List(fields.Int())

class RemoveInventoryItemSchema(ma.Schema):
    remove_inventory_items = fields.List(fields.Int())
    

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_service_ticket_schema = EditServiceTicketSchema()
add_inventory_item_schema = AddInventoryItemSchema()
remove_inventory_item_schema = RemoveInventoryItemSchema()