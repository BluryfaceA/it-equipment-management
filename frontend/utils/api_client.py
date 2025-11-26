import requests
import streamlit as st
import os

API_BASE_URL = os.getenv("API_GATEWAY_URL", "http://api-gateway:8000")

class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token = st.session_state.get('token', None)

    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self, username, password):
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password}
        )
        return response

    def get_current_user(self):
        response = requests.get(
            f"{self.base_url}/api/auth/me",
            headers=self._get_headers()
        )
        return response

    # Equipment endpoints
    def get_equipment(self, params=None):
        response = requests.get(
            f"{self.base_url}/api/equipment/equipment",
            headers=self._get_headers(),
            params=params or {}
        )
        return response

    def create_equipment(self, data):
        response = requests.post(
            f"{self.base_url}/api/equipment/equipment",
            headers=self._get_headers(),
            json=data
        )
        return response

    def update_equipment(self, equipment_id, data):
        response = requests.put(
            f"{self.base_url}/api/equipment/equipment/{equipment_id}",
            headers=self._get_headers(),
            json=data
        )
        return response

    def delete_equipment(self, equipment_id):
        response = requests.delete(
            f"{self.base_url}/api/equipment/equipment/{equipment_id}",
            headers=self._get_headers()
        )
        return response

    def get_categories(self):
        response = requests.get(
            f"{self.base_url}/api/equipment/categories",
            headers=self._get_headers()
        )
        return response

    def get_locations(self):
        response = requests.get(
            f"{self.base_url}/api/equipment/locations",
            headers=self._get_headers()
        )
        return response

    # Provider endpoints
    def get_providers(self, params=None):
        response = requests.get(
            f"{self.base_url}/api/providers/providers",
            headers=self._get_headers(),
            params=params or {}
        )
        return response

    def create_provider(self, data):
        response = requests.post(
            f"{self.base_url}/api/providers/providers",
            headers=self._get_headers(),
            json=data
        )
        return response

    def update_provider(self, provider_id, data):
        response = requests.put(
            f"{self.base_url}/api/providers/providers/{provider_id}",
            headers=self._get_headers(),
            json=data
        )
        return response

    # Maintenance endpoints
    def get_maintenance(self, params=None):
        response = requests.get(
            f"{self.base_url}/api/maintenance/maintenance",
            headers=self._get_headers(),
            params=params or {}
        )
        return response

    def create_maintenance(self, data):
        response = requests.post(
            f"{self.base_url}/api/maintenance/maintenance",
            headers=self._get_headers(),
            json=data
        )
        return response

    def get_upcoming_maintenance(self, days=30):
        response = requests.get(
            f"{self.base_url}/api/maintenance/upcoming-maintenance",
            headers=self._get_headers(),
            params={"days": days}
        )
        return response

    def get_overdue_maintenance(self):
        response = requests.get(
            f"{self.base_url}/api/maintenance/overdue-maintenance",
            headers=self._get_headers()
        )
        return response

    # Reports endpoints
    def get_dashboard_statistics(self):
        response = requests.get(
            f"{self.base_url}/api/reports/dashboard/statistics",
            headers=self._get_headers()
        )
        return response

    def download_equipment_excel(self, params=None):
        response = requests.get(
            f"{self.base_url}/api/reports/equipment/excel",
            headers=self._get_headers(),
            params=params or {}
        )
        return response

    def download_equipment_pdf(self, params=None):
        response = requests.get(
            f"{self.base_url}/api/reports/equipment/pdf",
            headers=self._get_headers(),
            params=params or {}
        )
        return response

    def download_maintenance_excel(self, params=None):
        response = requests.get(
            f"{self.base_url}/api/reports/maintenance/excel",
            headers=self._get_headers(),
            params=params or {}
        )
        return response
