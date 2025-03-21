from app import create_app
from app.models import db, Mechanic
import unittest

# Command to run tests: python -m unittest discover tests

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.mechanic = Mechanic(name="Jared", email="thisisnotmy@email.com", phone="720-123-4567", salary="1.25")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
            db.session.remove()
        super().tearDown()

    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "Jane Doe",
            "email": "janedoe@email.com",
            "phone": "000-555-5555",
            "salary": "12.50"
        }
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'Jane Doe')

    def test_invalid_creation(self):
        mechanic_payload = {
            "name": "MissingNo.",
            "email": "missingphoneandsalary@email.com"
        }
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)

    def test_get_mechanics(self):
        response = self.client.get('/mechanics/')
        self.assertIsNotNone(response.json)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(mechanic['name'] == 'Jared' for mechanic in response.json))

    def test_get_hardest_workers(self):
        response = self.client.get('/mechanics/hardest-workers')
        self.assertIsNotNone(response.json)
        self.assertEqual(response.status_code, 200)

    def test_update_mechanic(self):
        mechanic_payload = {
            'id': 1,
            'name': 'Dane Joe',
            'email': 'danejoe@email.com',
            'phone': '555-555-0000',
            'salary': '50.12'
        }
        response = self.client.put(f'/mechanics/{mechanic_payload['id']}', json=mechanic_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Dane Joe')

    def test_invalid_update_mechanic(self):
        mechanic_payload = {
            'id': 69,
            'name': 'Missingno.',
            'email': 'nonexistentid@email.com',
            'phone': '555-555-0000',
            'salary': '2.10'
        }
        response = self.client.put(f'/mechanics/{mechanic_payload['id']}', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)

    def test_delete_mechanic(self):
        response = self.client.delete('/mechanics/1')
        self.assertEqual(response.status_code, 200)

    def test_invalid_delete(self):
        response = self.client.delete('/mechanics/69')
        self.assertEqual(response.status_code, 400)