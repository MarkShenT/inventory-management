"""
Tests for restocking API endpoints.
"""
import pytest


class TestRestockingRecommendations:
    """Test suite for GET /api/restocking/recommendations."""

    def test_get_recommendations_default_budget(self, client):
        """Test getting recommendations with default budget."""
        response = client.get("/api/restocking/recommendations")
        assert response.status_code == 200

        data = response.json()
        assert "budget" in data
        assert "total_cost" in data
        assert "items" in data
        assert isinstance(data["items"], list)
        assert data["budget"] == 100000.0

    def test_get_recommendations_custom_budget(self, client):
        """Test getting recommendations with a specific budget."""
        response = client.get("/api/restocking/recommendations?budget=50000")
        assert response.status_code == 200

        data = response.json()
        assert data["budget"] == 50000.0
        assert data["total_cost"] <= 50000.0

    def test_recommendations_total_cost_within_budget(self, client):
        """Test that total cost never exceeds the budget."""
        for budget in [10000, 50000, 100000, 250000, 500000]:
            response = client.get(f"/api/restocking/recommendations?budget={budget}")
            data = response.json()
            assert data["total_cost"] <= data["budget"], (
                f"Total cost {data['total_cost']} exceeds budget {data['budget']}"
            )

    def test_recommendations_item_structure(self, client):
        """Test that each recommendation item has required fields."""
        response = client.get("/api/restocking/recommendations?budget=500000")
        data = response.json()

        assert len(data["items"]) > 0
        for item in data["items"]:
            assert "sku" in item
            assert "name" in item
            assert "forecasted_demand" in item
            assert "current_stock" in item
            assert "restock_quantity" in item
            assert "unit_cost" in item
            assert "total_cost" in item
            assert "priority" in item
            assert "reason" in item
            assert item["priority"] in ("high", "medium", "low")
            assert item["restock_quantity"] > 0
            assert item["unit_cost"] > 0

    def test_recommendations_priority_ordering(self, client):
        """Test that items are sorted by priority (high before medium before low)."""
        response = client.get("/api/restocking/recommendations?budget=500000")
        data = response.json()

        priority_order = {"high": 0, "medium": 1, "low": 2}
        priorities = [priority_order[item["priority"]] for item in data["items"]]
        assert priorities == sorted(priorities), "Items not sorted by priority"

    def test_recommendations_small_budget(self, client):
        """Test that a very small budget returns fewer or partial items."""
        response = client.get("/api/restocking/recommendations?budget=1000")
        data = response.json()
        assert data["total_cost"] <= 1000.0

    def test_recommendations_item_total_cost_matches(self, client):
        """Test that each item's total_cost = restock_quantity * unit_cost."""
        response = client.get("/api/restocking/recommendations?budget=500000")
        data = response.json()

        for item in data["items"]:
            expected = round(item["restock_quantity"] * item["unit_cost"], 2)
            assert item["total_cost"] == expected, (
                f"Item {item['sku']}: expected total_cost {expected}, got {item['total_cost']}"
            )


class TestRestockingOrders:
    """Test suite for POST /api/restocking/orders."""

    def test_place_restocking_order(self, client):
        """Test placing a restocking order."""
        order_data = {
            "items": [
                {"sku": "FLT-405", "name": "Oil Filter Cartridge", "quantity": 100, "unit_cost": 22.5}
            ],
            "budget_used": 2250.0
        }
        response = client.post("/api/restocking/orders", json=order_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "Submitted"
        from datetime import datetime
        assert data["order_number"].startswith(f"RST-{datetime.now().year}-")
        assert data["customer"] == "Internal Restocking"
        assert data["total_value"] == 2250.0
        assert len(data["items"]) == 1
        assert data["items"][0]["sku"] == "FLT-405"
        assert data["actual_delivery"] is None

    def test_placed_order_has_delivery_date(self, client):
        """Test that placed order has expected delivery 14 days out."""
        from datetime import datetime, timedelta

        order_data = {
            "items": [
                {"sku": "WDG-001", "name": "Industrial Widget Type A", "quantity": 10, "unit_cost": 35.5}
            ],
            "budget_used": 355.0
        }
        response = client.post("/api/restocking/orders", json=order_data)
        data = response.json()

        order_date = datetime.fromisoformat(data["order_date"])
        delivery_date = datetime.fromisoformat(data["expected_delivery"])
        delta = (delivery_date - order_date).days
        assert delta == 14

    def test_placed_order_appears_in_orders_list(self, client):
        """Test that a placed restocking order shows up in GET /api/orders."""
        order_data = {
            "items": [
                {"sku": "GSK-203", "name": "High-Temperature Gasket", "quantity": 50, "unit_cost": 12.75}
            ],
            "budget_used": 637.5
        }
        client.post("/api/restocking/orders", json=order_data)

        response = client.get("/api/orders?status=Submitted")
        assert response.status_code == 200

        data = response.json()
        submitted = [o for o in data if o["status"] == "Submitted"]
        assert len(submitted) > 0

        order_numbers = [o["order_number"] for o in submitted]
        assert any(on.startswith("RST-") for on in order_numbers)

    def test_place_order_multiple_items(self, client):
        """Test placing an order with multiple items."""
        order_data = {
            "items": [
                {"sku": "FLT-405", "name": "Oil Filter Cartridge", "quantity": 100, "unit_cost": 22.5},
                {"sku": "WDG-001", "name": "Industrial Widget Type A", "quantity": 50, "unit_cost": 35.5}
            ],
            "budget_used": 4025.0
        }
        response = client.post("/api/restocking/orders", json=order_data)
        assert response.status_code == 200

        data = response.json()
        assert len(data["items"]) == 2
        assert data["total_value"] == 4025.0
