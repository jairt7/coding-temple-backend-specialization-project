from app import create_app
from app.models import db, Inventory
import unittest

# Command to run tests: python -m unittest discover tests

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.inventory = Inventory(name="Tire", price="49.99")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.inventory)
            db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
            db.session.remove()
        super().tearDown()
    
    def test_create_inventory_item(self):
        item_payload = {
            "name": "Oil",
            "price": "19.99"
        }

        response = self.client.post('/inventory/', json=item_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'Oil')
    
    def test_invalid_creation(self):
        item_payload = {
            "name": "Priceless car part"
        }

        response = self.client.post('/inventory/', json=item_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['price'], ['Missing data for required field.'])
    
    def test_get(self):
        response = self.client.get('/inventory/')
        self.assertIsNotNone(response.json)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(item['name'] == 'Tire' for item in response.json))
    
    def test_update_inventory(self):
        inventory_payload = {
            'id': 1,
            'name': 'Wheel',
            'price': '59.99'
        }
        response = self.client.put(f"/inventory/{inventory_payload['id']}", json=inventory_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Wheel')
    
    def test_invalid_update_inventory(self):
        inventory_payload = {
            'id': 420,
            'name': 'Invalid ID',
            'price': '113.70'
        }
        response = self.client.put(f'/inventory/{inventory_payload['id']}', json=inventory_payload)
        self.assertEqual(response.status_code, 400)

        inventory_payload = {
            'id': 1,
            'name': 'No price!'
        }
        response = self.client.put(f'/inventory/{inventory_payload['id']}', json=inventory_payload)
        self.assertEqual(response.status_code, 400)


    def test_delete_inventory(self):
        response = self.client.delete('/inventory/1')
        self.assertEqual(response.status_code, 200)

    def test_invalid_delete(self):
        response = self.client.delete('/inventory/420')
        self.assertEqual(response.status_code, 400)