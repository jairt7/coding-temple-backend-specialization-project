from app.models import Inventory, db
from app.extensions import ma

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
    
    id = ma.auto_field()
    name = ma.auto_field()
    price = ma.auto_field()

inventory_schema = InventorySchema(many=True)