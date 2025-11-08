"""Integration Tests for FastAPI Application Initialization"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import create_app
from app.config import Settings


class TestApplicationFactory:
    """Test cases for application factory pattern"""

    def test_create_app_with_default_config(self):
        """Test creating app with default configuration"""
        app = create_app()

        assert app is not None
        assert app.title == "AutoWeb Outreach AI API"
        assert app.version == "0.1.0"

    def test_create_app_with_custom_config(self, test_settings):
        """Test creating app with custom configuration override"""
        app = create_app(config_override=test_settings)

        assert app.title == "AutoWeb Outreach AI API (Test)"
        assert app.version == "0.1.0-test"
        assert app.state.settings.ENVIRONMENT == "test"

    def test_app_stores_settings_in_state(self, app, test_settings):
        """Test that app stores settings in state for route access"""
        assert hasattr(app.state, "settings")
        assert app.state.settings.ENVIRONMENT == "test"


class TestRootEndpoint:
    """Test cases for root endpoint"""

    def test_root_endpoint_returns_metadata(self, client):
        """Test root endpoint returns API metadata"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "version" in data
        assert "environment" in data
        assert "docs" in data
        assert "health" in data

    def test_root_endpoint_includes_version(self, client):
        """Test root endpoint includes version information"""
        response = client.get("/")
        data = response.json()

        assert data["version"] == "0.1.0-test"

    def test_root_endpoint_includes_environment(self, client):
        """Test root endpoint includes environment information"""
        response = client.get("/")
        data = response.json()

        assert data["environment"] == "test"


class TestHealthCheckEndpoint:
    """Test cases for enhanced health check endpoint"""

    def test_health_check_returns_200(self, client):
        """Test health check endpoint returns 200 OK"""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_check_includes_status(self, client):
        """Test health check includes status field"""
        response = client.get("/api/health")
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_check_includes_version(self, client):
        """Test health check includes version information"""
        response = client.get("/api/health")
        data = response.json()

        assert "version" in data
        assert data["version"] == "0.1.0-test"

    def test_health_check_includes_environment(self, client):
        """Test health check includes environment information"""
        response = client.get("/api/health")
        data = response.json()

        assert "environment" in data
        assert data["environment"] == "test"

    def test_health_check_includes_timestamp(self, client):
        """Test health check includes UTC timestamp"""
        response = client.get("/api/health")
        data = response.json()

        assert "timestamp" in data
        # Validate timestamp format (ISO 8601 with Z suffix)
        timestamp_str = data["timestamp"]
        assert timestamp_str.endswith("Z")
        # Parse to ensure valid datetime
        datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

    def test_health_check_includes_database_status(self, client):
        """Test health check includes database connectivity status"""
        response = client.get("/api/health")
        data = response.json()

        assert "database" in data
        assert data["database"] in ["connected", "unavailable"]

    def test_health_check_response_schema(self, client):
        """Test health check returns complete expected schema"""
        response = client.get("/api/health")
        data = response.json()

        expected_keys = {"status", "version", "environment", "timestamp", "database"}
        assert set(data.keys()) == expected_keys


class TestCORSConfiguration:
    """Test cases for CORS middleware configuration"""

    def test_cors_headers_present_in_response(self, client):
        """Test CORS headers are present in responses"""
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:3000"}
        )

        assert "access-control-allow-origin" in response.headers

    def test_cors_allows_configured_origin(self, client):
        """Test CORS allows origins from configuration"""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_cors_allows_credentials(self, client):
        """Test CORS allows credentials when configured"""
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:3000"}
        )

        # Check if credentials are allowed
        allow_credentials = response.headers.get("access-control-allow-credentials")
        assert allow_credentials == "true"

    def test_cors_allows_methods(self, client):
        """Test CORS allows configured HTTP methods"""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )

        assert response.status_code == 200


class TestDatabaseDependency:
    """Test cases for database session dependency injection"""

    def test_database_dependency_injects_session(self, client):
        """Test database dependency provides session to endpoints"""
        # Health check uses database dependency
        response = client.get("/api/health")

        assert response.status_code == 200
        # If we get a response, dependency injection worked
        data = response.json()
        assert "database" in data

    def test_database_dependency_handles_errors_gracefully(self, client):
        """Test database dependency handles connection errors without crashing"""
        # Even if database connection fails, health check should return 200
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        # Database status can be "connected" or "unavailable"
        assert data["database"] in ["connected", "unavailable"]


class TestConfigurationLoading:
    """Test cases for environment-based configuration"""

    def test_app_loads_settings_from_config(self, test_settings):
        """Test app loads settings from configuration"""
        app = create_app(config_override=test_settings)

        assert app.state.settings.ENVIRONMENT == "test"
        assert app.state.settings.DEBUG is True

    def test_cors_origins_loaded_from_settings(self, test_settings):
        """Test CORS origins are loaded from settings"""
        app = create_app(config_override=test_settings)

        # CORS middleware should use origins from settings
        assert app.state.settings.CORS_ORIGINS == ["http://localhost:3000", "http://testserver"]

    def test_app_metadata_loaded_from_settings(self, test_settings):
        """Test app metadata (title, version) loaded from settings"""
        app = create_app(config_override=test_settings)

        assert app.title == test_settings.APP_NAME
        assert app.version == test_settings.API_VERSION


class TestApplicationLifecycle:
    """Test cases for application startup and shutdown events"""

    def test_app_starts_successfully(self, client):
        """Test application starts without errors"""
        # If we can make a request, app started successfully
        response = client.get("/")
        assert response.status_code == 200

    def test_startup_event_executes(self, app):
        """Test startup event handler executes"""
        # Startup event should have executed during app creation
        # Verify by checking health endpoint works
        with TestClient(app) as client:
            response = client.get("/api/health")
            assert response.status_code == 200

    def test_app_responds_to_requests_after_startup(self, client):
        """Test app responds to requests after startup"""
        response = client.get("/api/health")
        assert response.status_code == 200

        response2 = client.get("/")
        assert response2.status_code == 200


class TestDocumentation:
    """Test cases for API documentation endpoints"""

    def test_docs_endpoint_available_in_debug_mode(self, client):
        """Test Swagger docs endpoint is available in debug mode"""
        # In test mode (debug=True), docs should be available
        response = client.get("/docs")
        # Should return HTML or redirect, not 404
        assert response.status_code in [200, 307]

    def test_redoc_endpoint_available_in_debug_mode(self, client):
        """Test ReDoc endpoint is available in debug mode"""
        # In test mode (debug=True), redoc should be available
        response = client.get("/redoc")
        # Should return HTML or redirect, not 404
        assert response.status_code in [200, 307]


class TestErrorHandling:
    """Test cases for error handling and validation"""

    def test_invalid_endpoint_returns_404(self, client):
        """Test requesting invalid endpoint returns 404"""
        response = client.get("/api/invalid-endpoint")
        assert response.status_code == 404

    def test_invalid_method_returns_405(self, client):
        """Test using invalid HTTP method returns 405"""
        # Health check is GET only
        response = client.delete("/api/health")
        assert response.status_code == 405
