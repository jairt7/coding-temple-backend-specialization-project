from app.models import Mechanic, db
from app.extensions import ma

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
    
    id = ma.auto_field()
    name = ma.auto_field()
    email = ma.auto_field()
    phone = ma.auto_field()
    salary = ma.auto_field()

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)