from app import create_app
from app.models import db, ServiceTicket, Customer, Mechanic, Inventory
from datetime import date
import unittest

# Command to run tests: python -m unittest discover tests

class TestServiceTicket(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            customer = Customer(name="John Johnson", email="john@example.com", phone="123-456-7890", password="password")
            db.session.add(customer)
            db.session.commit()
            mechanic1 = Mechanic(name="Jared", email="thisisnotmy@email.com", phone="720-555-5555", salary=10)
            mechanic2 = Mechanic(name="Daemon", email="miigunner@email.com", phone="801-555-1332", salary=6000)
            db.session.add_all([mechanic1, mechanic2])
            db.session.commit()
            item = Inventory(name="Windshield wiper fluid", price="4.49")
            db.session.add(item)
            db.session.commit()
            self.ticket = ServiceTicket(
                VIN="12345678909876543", service_date=date(2025, 3, 20),
                service_desc="Car tried to out-pizza the Hut", customer_id=customer.id)
            self.ticket.mechanics.extend([mechanic1, mechanic2])
            db.session.add(self.ticket)
            db.session.commit()

        self.client = self.app.test_client()



    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
            db.session.remove()
        super().tearDown()

    def test_create_service_ticket(self):
        ticket_payload = {
            "VIN": "10293847565748392",
            "service_date": "2025-03-19",
            "service_desc": "Regular maintenance",
            "customer_id": 1,
            "mechanic_ids": [1, 2]
        }
        response = self.client.post('/service-tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['VIN'], "10293847565748392")
    
    def test_invalid_creation(self):
        ticket_payload = {
            "service_desc": "How did we get here?"
        }

        response = self.client.post('/service-tickets/', json=ticket_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['VIN'], ['Missing data for required field.'])
    
    def test_get_tickets(self):
        response = self.client.get('/service-tickets/')
        self.assertIsNotNone(response.json)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(ticket['VIN'] == '12345678909876543' for ticket in response.json))

    def test_add_remove_mechanic_ticket(self):
        ticket_payload = {
            "remove_mechanic_ids": [2]
        }
        response = self.client.put("/service-tickets/1", json=ticket_payload)
        self.assertEqual(response.status_code, 200)
        for mechanic in response.json['mechanics']:
            self.assertNotEqual(mechanic.get("id"), 2)

    def test_invalid_add_remove_mechanic_ticket(self):
        ticket_payload = {
            "add_mechanic_ids": [420] # invalid ID
        }
        response = self.client.put("/service-tickets/1", json=ticket_payload)
        self.assertEqual(response.status_code, 400)

    def test_delete_ticket(self):
        response = self.client.delete('/service-tickets/1')
        self.assertEqual(response.status_code, 200)

    def test_invalid_delete_ticket(self):
        response = self.client.delete('/service-tickets/420')
        self.assertEqual(response.status_code, 200)

    def test_add_item(self):
        response = self.client.post('/service-tickets/1/add-item/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['quantity'], 1)
        response = self.client.post('/service-tickets/1/add-item/1')
        self.assertEqual(response.json['quantity'], 2)

    def test_invalid_add_item(self):
        response = self.client.post('/service-tickets/1/add-item/420')
        self.assertEqual(response.status_code, 400)

    def test_remove_item(self):
        self.client.post('/service-tickets/1/add-item/1')
        response = self.client.post('/service-tickets/1/remove-item/1')
        self.assertEqual(response.status_code, 200)

    def test_invalid_remove_item(self):
        self.client.post('/service-tickets/1/add-item/1')
        response = self.client.post('/service-tickets/1/remove-item/0')
        self.assertEqual(response.status_code, 400)