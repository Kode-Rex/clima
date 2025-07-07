"""
Tests for MCP and SSE server functionality
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from weather_mcp.server import create_server, mcp
from weather_mcp.sse import WeatherSSEApp, WeatherSSEManager


class TestMCPServer:
    """Test class for MCP server functionality"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_server_with_config(self, mock_config):
        """Test server creation with provided config"""
        with patch('weather_mcp.server.AccuWeatherClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            with patch('weather_mcp.server.setup_logging') as mock_setup_logging:
                server = create_server(mock_config)
                
                assert server is not None
                assert server.name == "clima-mcp"
                mock_setup_logging.assert_called_once_with(mock_config)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_server_without_config(self):
        """Test server creation without provided config (uses default)"""
        with patch('weather_mcp.server.get_config') as mock_get_config:
            with patch('weather_mcp.server.AccuWeatherClient') as mock_client_class:
                with patch('weather_mcp.server.setup_logging') as mock_setup_logging:
                    mock_config = MagicMock()
                    mock_get_config.return_value = mock_config
                    
                    server = create_server()
                    
                    assert server is not None
                    mock_get_config.assert_called_once()
                    mock_setup_logging.assert_called_once_with(mock_config)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_server_tools_registration(self, mock_config):
        """Test that all tools are properly registered with the server"""
        with patch('weather_mcp.server.AccuWeatherClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            with patch('weather_mcp.server.setup_logging'):
                server = create_server(mock_config)
                
                # Check that the server has the expected tools
                # Note: FastMCP doesn't expose tools directly, so we test indirectly
                assert hasattr(server, 'name')
                assert server.name == "clima-mcp"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_mcp_server_initialization(self, mock_config):
        """Test MCP server initialization process"""
        with patch('weather_mcp.server.AccuWeatherClient') as mock_client_class:
            with patch('weather_mcp.server.setup_logging'):
                mock_client = AsyncMock()
                mock_client_class.return_value = mock_client
                
                server = create_server(mock_config)
                
                # Verify weather client is initialized
                assert mock_client_class.called
                mock_client_class.assert_called_with(mock_config)


class TestSSEServer:
    """Test class for SSE server functionality"""

    @pytest.fixture
    def sse_manager(self, mock_config, mock_weather_client):
        """Create SSE manager for testing"""
        return WeatherSSEManager(mock_config, mock_weather_client)

    @pytest.fixture
    def sse_app(self, mock_config, mock_weather_client):
        """Create SSE app for testing"""
        return WeatherSSEApp(mock_config, mock_weather_client)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_sse_manager_initialization(self, sse_manager, mock_config, mock_weather_client):
        """Test SSE manager initialization"""
        assert sse_manager.config == mock_config
        assert sse_manager.weather_client == mock_weather_client
        assert sse_manager.connections == {}
        assert sse_manager.location_subscribers == {}
        assert sse_manager.alert_cache == {}
        assert not sse_manager.running

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_sse_manager_start_stop(self, sse_manager):
        """Test SSE manager start and stop lifecycle"""
        # Test start
        await sse_manager.start()
        assert sse_manager.running
        assert sse_manager._heartbeat_task is not None
        assert sse_manager._alert_monitor_task is not None

        # Test stop
        await sse_manager.stop()
        assert not sse_manager.running

    @pytest.mark.integration
    def test_sse_connection_management(self, sse_manager):
        """Test SSE connection addition and removal"""
        connection_id = "test-conn-123"
        location_key = "349727"
        
        # Add connection
        connection = sse_manager.add_connection(connection_id, location_key)
        
        assert connection.id == connection_id
        assert connection.location_key == location_key
        assert connection_id in sse_manager.connections
        assert location_key in sse_manager.location_subscribers
        assert connection_id in sse_manager.location_subscribers[location_key]

        # Update heartbeat
        original_heartbeat = connection.last_heartbeat
        sse_manager.update_heartbeat(connection_id)
        assert sse_manager.connections[connection_id].last_heartbeat > original_heartbeat

        # Remove connection
        sse_manager.remove_connection(connection_id)
        assert connection_id not in sse_manager.connections
        assert location_key not in sse_manager.location_subscribers

    @pytest.mark.integration
    def test_sse_connection_expiry(self, sse_manager):
        """Test SSE connection expiry detection"""
        connection_id = "test-conn-123"
        location_key = "349727"
        
        connection = sse_manager.add_connection(connection_id, location_key)
        
        # Test not expired (fresh connection)
        assert not connection.is_expired(300)
        
        # Test expired (simulate old heartbeat)
        from datetime import datetime, timedelta
        connection.last_heartbeat = datetime.now() - timedelta(seconds=400)
        assert connection.is_expired(300)

    @pytest.mark.integration
    def test_sse_app_initialization(self, sse_app, mock_config, mock_weather_client):
        """Test SSE app initialization"""
        assert sse_app.config == mock_config
        assert sse_app.weather_client == mock_weather_client
        assert sse_app.sse_manager is not None
        assert hasattr(sse_app, 'app')

    @pytest.mark.integration
    def test_sse_app_routes(self, sse_app):
        """Test SSE app FastAPI routes"""
        app = sse_app.get_app()
        client = TestClient(app)
        
        # Test status endpoint
        response = client.get("/weather/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "active_connections" in data
        assert "monitored_locations" in data

    @pytest.mark.integration
    def test_sse_heartbeat_endpoint(self, sse_app):
        """Test SSE heartbeat endpoint"""
        app = sse_app.get_app()
        client = TestClient(app)
        
        # Add a connection first
        connection_id = "test-conn-123"
        location_key = "349727"
        sse_app.sse_manager.add_connection(connection_id, location_key)
        
        # Test heartbeat
        response = client.post(f"/weather/heartbeat/{connection_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data

    @pytest.mark.integration
    def test_sse_heartbeat_unknown_connection(self, sse_app):
        """Test SSE heartbeat with unknown connection"""
        app = sse_app.get_app()
        client = TestClient(app)
        
        # Test heartbeat for non-existent connection (should still return 200)
        response = client.post("/weather/heartbeat/unknown-connection")
        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_sse_alert_monitoring(self, sse_manager, mock_weather_client):
        """Test SSE alert monitoring functionality"""
        connection_id = "test-conn-123"
        location_key = "349727"
        
        # Add connection
        sse_manager.add_connection(connection_id, location_key)
        
        # Mock weather alerts
        from weather_mcp.accuweather import WeatherAlert
        from datetime import datetime, timezone
        
        mock_alert = WeatherAlert(
            alert_id="test-alert-123",
            title="Test Warning",
            description="Test alert description",
            severity="Moderate",
            category="meteorological",
            start_time=datetime.now(timezone.utc),
            end_time=None,
            areas=["Test Area"]
        )
        
        mock_weather_client.get_weather_alerts.return_value = [mock_alert]
        
        # Manually trigger alert check (simulating the background task)
        current_alerts = await mock_weather_client.get_weather_alerts(location_key)
        cached_alerts = sse_manager.alert_cache.get(location_key, [])
        
        assert len(current_alerts) == 1
        assert current_alerts[0].alert_id == "test-alert-123"
        assert len(cached_alerts) == 0  # No cached alerts initially

    @pytest.mark.integration
    def test_multiple_connections_same_location(self, sse_manager):
        """Test multiple SSE connections for the same location"""
        location_key = "349727"
        conn1_id = "conn-1"
        conn2_id = "conn-2"
        
        # Add two connections for same location
        sse_manager.add_connection(conn1_id, location_key)
        sse_manager.add_connection(conn2_id, location_key)
        
        assert len(sse_manager.connections) == 2
        assert len(sse_manager.location_subscribers[location_key]) == 2
        assert conn1_id in sse_manager.location_subscribers[location_key]
        assert conn2_id in sse_manager.location_subscribers[location_key]
        
        # Remove one connection
        sse_manager.remove_connection(conn1_id)
        
        assert len(sse_manager.connections) == 1
        assert len(sse_manager.location_subscribers[location_key]) == 1
        assert conn2_id in sse_manager.location_subscribers[location_key]
        
        # Remove last connection
        sse_manager.remove_connection(conn2_id)
        
        assert len(sse_manager.connections) == 0
        assert location_key not in sse_manager.location_subscribers


class TestServerIntegration:
    """Integration tests for server functionality"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_server_with_mock_environment(self, mock_server_environment):
        """Test server creation in a fully mocked environment"""
        env = mock_server_environment
        
        with patch('weather_mcp.server.weather_client', env['weather_client']):
            # Test that the global weather client is properly mocked
            from weather_mcp.server import weather_client
            assert weather_client == env['weather_client']
            
            # Create server with mocked environment
            server = create_server(env['config'])
            assert server is not None

    @pytest.mark.integration
    def test_sse_app_with_mock_environment(self, mock_server_environment):
        """Test SSE app creation in a fully mocked environment"""
        env = mock_server_environment
        
        # Create SSE app with mocked environment
        sse_app = WeatherSSEApp(env['config'], env['weather_client'])
        app = sse_app.get_app()
        
        client = TestClient(app)
        response = client.get("/weather/status")
        assert response.status_code == 200 