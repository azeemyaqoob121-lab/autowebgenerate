"""
Business API Endpoint Tests

Comprehensive tests for business CRUD operations including:
- Create, Read, Update, Delete operations
- List with pagination, filtering, and sorting
- Validation and error handling
- Soft delete functionality
- Authorization checks
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import Business


# ============================================================================
# CREATE TESTS
# ============================================================================

@pytest.mark.business
@pytest.mark.integration
def test_create_business_success(client: TestClient, auth_headers: dict):
    """Test creating a new business with valid data."""
    business_data = {
        "name": "New Test Business",
        "email": "contact@newtestbusiness.co.uk",
        "phone": "020 9999 9999",
        "address": "999 Test Road, London, W1A 9ZZ",
        "website_url": "https://www.newtestbusiness.co.uk",
        "category": "Plumbing",
        "description": "A new test business for testing",
        "location": "London",
        "score": 88
    }

    response = client.post(
        "/api/businesses",
        json=business_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()

    # Verify response contains all fields
    assert data["name"] == business_data["name"]
    assert data["email"] == business_data["email"]
    assert data["phone"] == business_data["phone"]
    assert data["category"] == business_data["category"]
    assert data["location"] == business_data["location"]
    assert data["score"] == business_data["score"]

    # Verify generated fields
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["deleted_at"] is None


@pytest.mark.business
@pytest.mark.integration
def test_create_business_minimal_fields(client: TestClient, auth_headers: dict):
    """Test creating business with only required fields."""
    business_data = {
        "name": "Minimal Business",
        "email": "minimal@business.co.uk",
        "website_url": "https://www.minimal.co.uk",
        "category": "Construction",
        "location": "Manchester"
    }

    response = client.post(
        "/api/businesses",
        json=business_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == business_data["name"]


@pytest.mark.business
@pytest.mark.integration
def test_create_business_duplicate_website_url(client: TestClient, auth_headers: dict, test_business: Business):
    """Test creating business with duplicate website URL fails."""
    business_data = {
        "name": "Duplicate Business",
        "email": "duplicate@business.co.uk",
        "website_url": test_business.website_url,  # Duplicate!
        "category": "Plumbing",
        "location": "London"
    }

    response = client.post(
        "/api/businesses",
        json=business_data,
        headers=auth_headers
    )

    assert response.status_code == 409
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "DUPLICATE_RESOURCE"


@pytest.mark.business
@pytest.mark.integration
def test_create_business_invalid_email(client: TestClient, auth_headers: dict):
    """Test creating business with invalid email format fails."""
    business_data = {
        "name": "Invalid Email Business",
        "email": "invalid-email",  # Invalid!
        "website_url": "https://www.invalid.co.uk",
        "category": "Electrical",
        "location": "Birmingham"
    }

    response = client.post(
        "/api/businesses",
        json=business_data,
        headers=auth_headers
    )

    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.business
@pytest.mark.integration
def test_create_business_invalid_score(client: TestClient, auth_headers: dict):
    """Test creating business with score outside valid range fails."""
    business_data = {
        "name": "Invalid Score Business",
        "email": "invalid@score.co.uk",
        "website_url": "https://www.invalidscore.co.uk",
        "category": "Plumbing",
        "location": "Leeds",
        "score": 150  # Invalid! Must be 0-100
    }

    response = client.post(
        "/api/businesses",
        json=business_data,
        headers=auth_headers
    )

    assert response.status_code == 422


@pytest.mark.business
@pytest.mark.integration
def test_create_business_without_auth(client: TestClient):
    """Test creating business without authentication fails."""
    business_data = {
        "name": "Unauthorized Business",
        "email": "unauth@business.co.uk",
        "website_url": "https://www.unauth.co.uk",
        "category": "Plumbing",
        "location": "London"
    }

    response = client.post("/api/businesses", json=business_data)

    assert response.status_code == 403


# ============================================================================
# READ TESTS
# ============================================================================

@pytest.mark.business
@pytest.mark.integration
def test_get_business_by_id(client: TestClient, auth_headers: dict, test_business: Business):
    """Test retrieving a specific business by ID."""
    response = client.get(
        f"/api/businesses/{test_business.id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(test_business.id)
    assert data["name"] == test_business.name
    assert data["email"] == test_business.email
    assert data["category"] == test_business.category


@pytest.mark.business
@pytest.mark.integration
def test_get_business_nonexistent_id(client: TestClient, auth_headers: dict):
    """Test retrieving business with non-existent ID returns 404."""
    fake_id = uuid.uuid4()
    response = client.get(
        f"/api/businesses/{fake_id}",
        headers=auth_headers
    )

    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "BUSINESS_NOT_FOUND"


@pytest.mark.business
@pytest.mark.integration
def test_get_business_invalid_uuid(client: TestClient, auth_headers: dict):
    """Test retrieving business with invalid UUID format returns 422."""
    response = client.get(
        "/api/businesses/invalid-uuid",
        headers=auth_headers
    )

    assert response.status_code == 422


@pytest.mark.business
@pytest.mark.integration
def test_list_businesses_default_pagination(client: TestClient, auth_headers: dict, test_businesses):
    """Test listing businesses with default pagination."""
    response = client.get("/api/businesses", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data

    assert len(data["items"]) == 5  # We have 5 test businesses
    assert data["total"] == 5
    assert data["page"] == 1


@pytest.mark.business
@pytest.mark.integration
def test_list_businesses_custom_pagination(client: TestClient, auth_headers: dict, test_businesses):
    """Test listing businesses with custom page size."""
    response = client.get(
        "/api/businesses?page=1&page_size=2",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data["items"]) == 2
    assert data["page_size"] == 2
    assert data["total_pages"] == 3  # 5 businesses / 2 per page = 3 pages


@pytest.mark.business
@pytest.mark.integration
def test_list_businesses_filter_by_location(client: TestClient, auth_headers: dict, test_businesses):
    """Test filtering businesses by location."""
    response = client.get(
        "/api/businesses?location=London",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should only return London businesses
    assert all(b["location"] == "London" for b in data["items"])
    assert data["total"] == 2  # 2 London businesses in test data


@pytest.mark.business
@pytest.mark.integration
def test_list_businesses_filter_by_category(client: TestClient, auth_headers: dict, test_businesses):
    """Test filtering businesses by category."""
    response = client.get(
        "/api/businesses?category=Plumbing",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert all(b["category"] == "Plumbing" for b in data["items"])
    assert data["total"] == 2  # 2 Plumbing businesses in test data


@pytest.mark.business
@pytest.mark.integration
def test_list_businesses_filter_by_score_range(client: TestClient, auth_headers: dict, test_businesses):
    """Test filtering businesses by score range."""
    response = client.get(
        "/api/businesses?min_score=80",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert all(b["score"] >= 80 for b in data["items"])


@pytest.mark.business
@pytest.mark.integration
def test_list_businesses_multiple_filters(client: TestClient, auth_headers: dict, test_businesses):
    """Test combining multiple filters."""
    response = client.get(
        "/api/businesses?location=London&category=Plumbing",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should return businesses matching both filters
    for business in data["items"]:
        assert business["location"] == "London"
        assert business["category"] == "Plumbing"


@pytest.mark.business
@pytest.mark.integration
def test_list_businesses_sort_by_score_desc(client: TestClient, auth_headers: dict, test_businesses):
    """Test sorting businesses by score descending."""
    response = client.get(
        "/api/businesses?sort_by=score&sort_order=desc",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify scores are in descending order
    scores = [b["score"] for b in data["items"]]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.business
@pytest.mark.integration
def test_list_businesses_sort_by_created_at_desc(client: TestClient, auth_headers: dict, test_businesses):
    """Test sorting businesses by creation date descending."""
    response = client.get(
        "/api/businesses?sort_by=created_at&sort_order=desc",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify created_at timestamps are in descending order
    timestamps = [b["created_at"] for b in data["items"]]
    assert timestamps == sorted(timestamps, reverse=True)


# ============================================================================
# UPDATE TESTS
# ============================================================================

@pytest.mark.business
@pytest.mark.integration
def test_update_business_success(client: TestClient, auth_headers: dict, test_business: Business):
    """Test updating business with valid data."""
    update_data = {
        "name": "Updated Business Name",
        "score": 95
    }

    response = client.put(
        f"/api/businesses/{test_business.id}",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Updated Business Name"
    assert data["score"] == 95
    # Verify other fields unchanged
    assert data["email"] == test_business.email
    assert data["category"] == test_business.category


@pytest.mark.business
@pytest.mark.integration
def test_update_business_partial_update(client: TestClient, auth_headers: dict, test_business: Business):
    """Test partial update of business (PATCH-like behavior)."""
    update_data = {"description": "Updated description only"}

    response = client.put(
        f"/api/businesses/{test_business.id}",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["description"] == "Updated description only"
    # Verify other fields unchanged
    assert data["name"] == test_business.name


@pytest.mark.business
@pytest.mark.integration
def test_update_business_nonexistent_id(client: TestClient, auth_headers: dict):
    """Test updating non-existent business returns 404."""
    fake_id = uuid.uuid4()
    update_data = {"name": "Updated Name"}

    response = client.put(
        f"/api/businesses/{fake_id}",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == 404


@pytest.mark.business
@pytest.mark.integration
def test_update_business_invalid_data(client: TestClient, auth_headers: dict, test_business: Business):
    """Test updating business with invalid data fails."""
    update_data = {"score": 150}  # Invalid score

    response = client.put(
        f"/api/businesses/{test_business.id}",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == 422


@pytest.mark.business
@pytest.mark.integration
def test_update_business_without_auth(client: TestClient, test_business: Business):
    """Test updating business without authentication fails."""
    update_data = {"name": "Unauthorized Update"}

    response = client.put(
        f"/api/businesses/{test_business.id}",
        json=update_data
    )

    assert response.status_code == 403


# ============================================================================
# DELETE TESTS
# ============================================================================

@pytest.mark.business
@pytest.mark.integration
def test_delete_business_success(client: TestClient, auth_headers: dict, test_business: Business):
    """Test soft deleting a business."""
    response = client.delete(
        f"/api/businesses/{test_business.id}",
        headers=auth_headers
    )

    assert response.status_code == 204

    # Verify business is soft deleted (has deleted_at timestamp)
    get_response = client.get(
        f"/api/businesses/{test_business.id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404  # Should not be retrievable


@pytest.mark.business
@pytest.mark.integration
def test_delete_business_nonexistent_id(client: TestClient, auth_headers: dict):
    """Test deleting non-existent business returns 404."""
    fake_id = uuid.uuid4()
    response = client.delete(
        f"/api/businesses/{fake_id}",
        headers=auth_headers
    )

    assert response.status_code == 404


@pytest.mark.business
@pytest.mark.integration
def test_delete_business_twice(client: TestClient, auth_headers: dict, test_business: Business):
    """Test deleting already deleted business returns 404."""
    # Delete first time
    response1 = client.delete(
        f"/api/businesses/{test_business.id}",
        headers=auth_headers
    )
    assert response1.status_code == 204

    # Delete second time
    response2 = client.delete(
        f"/api/businesses/{test_business.id}",
        headers=auth_headers
    )
    assert response2.status_code == 404


@pytest.mark.business
@pytest.mark.integration
def test_delete_business_without_auth(client: TestClient, test_business: Business):
    """Test deleting business without authentication fails."""
    response = client.delete(f"/api/businesses/{test_business.id}")

    assert response.status_code == 403


@pytest.mark.business
@pytest.mark.integration
def test_deleted_business_not_in_list(client: TestClient, auth_headers: dict, test_businesses):
    """Test deleted businesses don't appear in list results."""
    # Get initial count
    response1 = client.get("/api/businesses", headers=auth_headers)
    initial_count = response1.json()["total"]

    # Delete one business
    business_to_delete = test_businesses[0]
    client.delete(
        f"/api/businesses/{business_to_delete.id}",
        headers=auth_headers
    )

    # Get count after deletion
    response2 = client.get("/api/businesses", headers=auth_headers)
    final_count = response2.json()["total"]

    # Count should decrease by 1
    assert final_count == initial_count - 1


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

@pytest.mark.business
@pytest.mark.integration
def test_list_businesses_empty_result(client: TestClient, auth_headers: dict):
    """Test listing businesses with filters that match nothing."""
    response = client.get(
        "/api/businesses?location=NonexistentCity",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.business
@pytest.mark.integration
def test_list_businesses_page_beyond_total(client: TestClient, auth_headers: dict, test_businesses):
    """Test requesting page number beyond available pages."""
    response = client.get(
        "/api/businesses?page=999",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["items"] == []
    assert data["page"] == 999


@pytest.mark.business
@pytest.mark.integration
def test_create_business_with_special_characters(client: TestClient, auth_headers: dict):
    """Test creating business with special characters in name."""
    business_data = {
        "name": "O'Brien's Plumbing & Heating",
        "email": "contact@obriens.co.uk",
        "website_url": "https://www.obriens-plumbing.co.uk",
        "category": "Plumbing",
        "location": "Dublin"
    }

    response = client.post(
        "/api/businesses",
        json=business_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == business_data["name"]


@pytest.mark.business
@pytest.mark.integration
def test_list_businesses_performance_with_large_page_size(client: TestClient, auth_headers: dict, test_businesses):
    """Test listing with large page size completes quickly."""
    import time

    start_time = time.time()
    response = client.get(
        "/api/businesses?page_size=100",
        headers=auth_headers
    )
    end_time = time.time()

    assert response.status_code == 200
    assert (end_time - start_time) < 1.0  # Should complete in < 1 second
