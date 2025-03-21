from app import create_app
from app.models import db, ServiceTicket, Customer, Mechanic
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

    def test_update_ticket(self):
        ticket_payload = {
            "id": 1,
            "service_date": "2025-03-21",
            "service_desc": "Working on this later than originally planned"
        }
        response = self.client.put(f"/service-tickets/{ticket_payload['id']}/", json=ticket_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['service_date'], '2025-03-21')

    def test_invalid_update_ticket(self):
        pass

    def test_delete_ticket(self):
        pass

    def test_invalid_delete_ticket(self):
        pass

    def test_add_item(self):
        pass

    def test_remove_item(self):
        pass

    def test_invalid_remove_item(self):
        pass