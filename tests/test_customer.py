from app import create_app
from app.models import db, Customer
from app.utils.util import encode_token
import unittest

# Command to run tests: python -m unittest discover tests

class TestCustomer(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.customer = Customer(name='Test Zest', email='testzest@email.com', phone='1800-000-0000', password='TryChef123')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()
    
    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
            db.session.remove()
        super().tearDown()
    
    def test_create_customer(self):
        customer_payload = {
            "name": "John Cena",
            "email": "superslam@wwe.com",
            "phone": "1-800-384-5749",
            "password": "ANDHISNAMEISJOHNCENA!!!"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'John Cena')
    
    def test_invalid_creation(self):
        customer_payload = {
            "name": "Juan Cinnamon",
            "email": "idonthavveaphonenum@email.com"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['phone'], ['Missing data for required field.'])

    def test_login_customer(self):
        credentials = {
            "email": "testzest@email.com",
            "password": "TryChef123"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        
    
    def test_invalid_login(self):
        credentials = {
            "email": "spaceytracey@email.com",
            "password": "2outerTr@ce"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Invalid email or password.')
    
    def test_update_customer(self):
        credentials = {
            "email": "testzest@email.com",
            "password": "TryChef123"
        }

        response = self.client.post('/customers/login', json=credentials)
        
        update_payload = {
            "name": "Muffin Man",
            "email": "doyouknow@email.com",
            "phone": "333-333-1234",
            "password": "123DruryLane",
        }

        headers = {'Authorization': f'Bearer {self.token}'}

        response = self.client.put('/customers/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Muffin Man')
        self.assertEqual(response.json['email'], 'doyouknow@email.com')

    def invalid_update_customer(self):
        credentials = {
            "email": "testzest@email.com",
            "password": "TryChef123"
        }

        response = self.client.post('/customers/login', json=credentials)

        update_payload = {
            "name": "Muffin Man",
            "email": "doyouknow@email.com",
            "password": "N0Ph0neNum",
        }

        headers = {'Authorization': f'Bearer {self.token}'}

        response = self.client.put('/customers/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 400)


    def test_delete_customer(self):

        headers = {'Authorization': f'Bearer {self.token}'}

        response = self.client.delete('/customers/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Successfully deleted customer')