import pytest
import os
import decimal
import json
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from botocore.exceptions import ClientError

# Assume modern_app.py is in the same directory for import
from modern_app import CustomerManagement, CustomerRecord, Customer, Base, Session

# --- Fixtures for common setup and mocking ---

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Sets up default environment variables for AWS region and DB secret name."""
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("DB_SECRET_NAME", "my/db/secret")
    # Clear other potential DB env vars to ensure secrets manager takes precedence or falls back correctly
    monkeypatch.delenv("DB_HOST", raising=False)
    monkeypatch.delenv("DB_PORT", raising=False)
    monkeypatch.delenv("DB_NAME", raising=False)

@pytest.fixture
def customer_management_app():
    """Provides a fresh instance of CustomerManagement for each test."""
    return CustomerManagement()

@pytest.fixture
def mock_boto3_client(mocker):
    """Mocks boto3.client and its get_secret_value method."""
    mock_client = mocker.MagicMock()
    mocker.patch("modern_app.boto3.session.Session.client", return_value=mock_client)
    yield mock_client

@pytest.fixture
def mock_secrets_manager_success(mock_boto3_client):
    """Configures mock_boto3_client to return a successful secret string."""
    mock_boto3_client.get_secret_value.return_value = {
        "SecretString": json.dumps({
            "username": "testuser",
            "password": "testpassword",
            "host": "testdbhost",
            "port": "5432",
            "dbname": "testdbname"
        })
    }
    return mock_boto3_client

@pytest.fixture
def mock_sqlalchemy(mocker):
    """Mocks SQLAlchemy engine, sessionmaker, and Base.metadata.create_all."""
    mocker.patch("modern_app.create_engine")
    mocker.patch("modern_app.Base.metadata.create_all")
    
    mock_session_instance = mocker.MagicMock(spec=Session)
    mock_sessionmaker = mocker.patch("modern_app.sessionmaker")
    mock_sessionmaker.return_value.return_value = mock_session_instance
    
    yield {
        "engine": mocker.patch("modern_app.create_engine"),
        "create_all": mocker.patch("modern_app.Base.metadata.create_all"),
        "sessionmaker": mock_sessionmaker,
        "session_instance": mock_session_instance,
    }

@pytest.fixture
def mock_customer_data():
    """Provides mock customer data for database queries."""
    return Customer(id=10045, name="John Doe", balance=decimal.Decimal("12345.67"))

# --- Test Cases ---

class TestCustomerRecord:
    def test_customer_record_defaults(self):
        record = CustomerRecord()
        assert record.cust_id == 0
        assert record.cust_name == ""
        assert record.cust_bal == decimal.Decimal("0.00")

    def test_customer_record_initialization(self):
        record = CustomerRecord(cust_id=123, cust_name="Jane Doe", cust_bal=decimal.Decimal("99.99"))
        assert record.cust_id == 123
        assert record.cust_name == "Jane Doe"
        assert record.cust_bal == decimal.Decimal("99.99")

class TestCustomerManagementGetSecret:
    def test_get_secret_success(self, customer_management_app, mock_secrets_manager_success):
        secret = customer_management_app._get_secret("test-secret")
        assert secret == {
            "username": "testuser",
            "password": "testpassword",
            "host": "testdbhost",
            "port": "5432",
            "dbname": "testdbname"
        }
        mock_secrets_manager_success.get_secret_value.assert_called_once_with(SecretId="test-secret")

    def test_get_secret_no_aws_region(self, customer_management_app, monkeypatch):
        monkeypatch.delenv("AWS_REGION")
        with pytest.raises(ValueError, match="Environment variable 'AWS_REGION' must be set"):
            customer_management_app._get_secret("test-secret")

    @pytest.mark.parametrize("error_code, expected_error_message", [
        ("DecryptionFailureException", "Secrets Manager: Could not decrypt the secret."),
        ("InternalServiceErrorException", "Secrets Manager: Internal service error encountered."),
        ("InvalidParameterException", "Secrets Manager: Invalid parameter in request to fetch secret."),
        ("InvalidRequestException", "Secrets Manager: Invalid request while trying to fetch secret."),
        ("ResourceNotFoundException", "Secrets Manager: Secret 'test-secret' not found in region 'us-east-1'.")
    ])
    def test_get_secret_client_error_handling(self, customer_management_app, mock_boto3_client, error_code, expected_error_message):
        mock_boto3_client.get_secret_value.side_effect = ClientError(
            {"Error": {"Code": error_code, "Message": "Test Error"}},
            "get_secret_value"
        )
        with pytest.raises(ConnectionError, match=expected_error_message):
            customer_management_app._get_secret("test-secret")

    def test_get_secret_json_decode_error(self, customer_management_app, mock_boto3_client):
        mock_boto3_client.get_secret_value.return_value = {"SecretString": "not a valid json"}
        with pytest.raises(ValueError, match="Secrets Manager: Secret 'test-secret' is not a valid JSON string."):
            customer_management_app._get_secret("test-secret")

    def test_get_secret_binary_format(self, customer_management_app, mock_boto3_client):
        mock_boto3_client.get_secret_value.return_value = {"SecretBinary": b"binarydata"}
        with pytest.raises(ValueError, match="Secrets Manager secret 'test-secret' is in binary format, expected string"):
            customer_management_app._get_secret("test-secret")

    def test_get_secret_other_exception(self, customer_management_app, mock_boto3_client):
        mock_boto3_client.get_secret_value.side_effect = Exception("Network down")
        with pytest.raises(ConnectionError, match="Secrets Manager: An unexpected error occurred while fetching secret"):
            customer_management_app._get_secret("test-secret")

class TestCustomerManagementConnectDb:
    def test_connect_db_success(self, customer_management_app, mock_secrets_manager_success, mock_sqlalchemy):
        customer_management_app._connect_db()
        
        assert customer_management_app.session is mock_sqlalchemy["session_instance"]
        mock_secrets_manager_success.get_secret_value.assert_called_once()
        mock_sqlalchemy["engine"].assert_called_once_with("postgresql+psycopg2://testuser:testpassword@testdbhost:5432/testdbname")
        mock_sqlalchemy["create_all"].assert_called_once()
        mock_sqlalchemy["sessionmaker"].assert_called_once()

    def test_connect_db_no_db_secret_name(self, customer_management_app, monkeypatch):
        monkeypatch.delenv("DB_SECRET_NAME")
        with pytest.raises(ValueError, match="Environment variable 'DB_SECRET_NAME' must be set"):
            customer_management_app._connect_db()

    def test_connect_db_secrets_retrieval_failure(self, customer_management_app, mock_boto3_client):
        mock_boto3_client.get_secret_value.side_effect = ConnectionError("Failed to fetch secret")
        with pytest.raises(ConnectionError, match="Failed to fetch secret"):
            customer_management_app._connect_db()

    @pytest.mark.parametrize("missing_key", ["username", "password"])
    def test_connect_db_missing_credentials_in_secret(self, customer_management_app, mock_boto3_client, missing_key):
        secret_data = {
            "username": "testuser",
            "password": "testpassword",
            "host": "testdbhost",
            "port": "5432",
            "dbname": "testdbname"
        }
        del secret_data[missing_key]
        mock_boto3_client.get_secret_value.return_value = {"SecretString": json.dumps(secret_data)}
        
        with pytest.raises(ValueError, match="Database 'username' or 'password' missing"):
            customer_management_app._connect_db()

    @pytest.mark.parametrize("missing_param, env_var", [
        ("host", "DB_HOST"), ("port", "DB_PORT"), ("dbname", "DB_NAME")
    ])
    def test_connect_db_missing_conn_params_no_env(self, customer_management_app, mock_boto3_client, missing_param, env_var, monkeypatch):
        secret_data = {
            "username": "testuser",
            "password": "testpassword",
            "host": "testdbhost",
            "port": "5432",
            "dbname": "testdbname"
        }
        del secret_data[missing_param] # Remove from secret
        monkeypatch.delenv(env_var, raising=False) # Ensure not set in env
        mock_boto3_client.get_secret_value.return_value = {"SecretString": json.dumps(secret_data)}
        
        with pytest.raises(ValueError, match=f"Missing one or more critical database connection parameters: {missing_param}"):
            customer_management_app._connect_db()

    def test_connect_db_sqlalchemy_error(self, customer_management_app, mock_secrets_manager_success, mock_sqlalchemy):
        mock_sqlalchemy["engine"].side_effect = SQLAlchemyError("DB connection failed")
        with pytest.raises(ConnectionError, match="Failed to connect to the database."):
            customer_management_app._connect_db()

class TestCustomerManagementFetchCustomer:
    @pytest.fixture
    def setup_connected_app(self, customer_management_app, mock_secrets_manager_success, mock_sqlalchemy):
        """Fixture to ensure the app is in a connected state."""
        customer_management_app._connect_db()
        return customer_management_app, mock_sqlalchemy["session_instance"]

    def test_fetch_customer_success(self, setup_connected_app, mock_customer_data):
        app, mock_session = setup_connected_app
        app.customer_record.cust_id = 10045

        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_customer_data
        
        app._fetch_customer()

        assert app.customer_record.cust_name == "John Doe"
        assert app.customer_record.cust_bal == decimal.Decimal("12345.67")
        mock_session.query.assert_called_once_with(Customer)
        mock_session.query.return_value.filter_by.assert_called_once_with(id=10045)
        mock_session.query.return_value.filter_by.return_value.first.assert_called_once()

    def test_fetch_customer_not_found(self, setup_connected_app):
        app, mock_session = setup_connected_app
        app.customer_record.cust_id = 99999

        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        app._fetch_customer()

        assert app.customer_record.cust_name == "" # Should remain default or be explicitly cleared
        assert app.customer_record.cust_bal == decimal.Decimal("0.00") # Should remain default
        mock_session.query.assert_called_once_with(Customer)
        mock_session.query.return_value.filter_by.assert_called_once_with(id=99999)

    def test_fetch_customer_no_session(self, customer_management_app):
        # Ensure session is None
        customer_management_app.session = None 
        with pytest.raises(ConnectionError, match="Database session not established. Call _connect_db first."):
            customer_management_app._fetch_customer()

    def test_fetch_customer_sqlalchemy_error(self, setup_connected_app):
        app, mock_session = setup_connected_app
        app.customer_record.cust_id = 10045

        mock_session.query.side_effect = SQLAlchemyError("Query failed")
        
        with pytest.raises(SQLAlchemyError, match="Query failed"):
            app._fetch_customer()

class TestCustomerManagementCallExternalSvc:
    def test_call_external_svc(self, customer_management_app):
        customer_management_app.customer_record.cust_id = 12345
        # This method is a placeholder, so we just ensure it executes without error.
        # If it were to call an actual external service, we'd mock that external call.
        customer_management_app._call_external_svc()
        # No assertions on state change, as it's a placeholder.
        # We could capture print output if desired, but that's not testing core logic.

class TestCustomerManagementMainParagraph:
    def test_main_paragraph_success(self, customer_management_app, mock_secrets_manager_success, mock_sqlalchemy, mock_customer_data, mocker):
        mock_sqlalchemy["session_instance"].query.return_value.filter_by.return_value.first.return_value = mock_customer_data
        
        # Mock _call_external_svc as it's a placeholder
        mocker.patch.object(customer_management_app, "_call_external_svc")

        customer_management_app.main_paragraph()

        assert customer_management_app.customer_record.cust_id == 10045
        assert customer_management_app.customer_record.cust_name == "John Doe"
        assert customer_management_app.customer_record.cust_bal == decimal.Decimal("12345.67")

        mock_secrets_manager_success.get_secret_value.assert_called_once()
        mock_sqlalchemy["engine"].assert_called_once()
        mock_sqlalchemy["session_instance"].query.assert_called_once_with(Customer)
        customer_management_app._call_external_svc.assert_called_once()
        mock_sqlalchemy["session_instance"].close.assert_called_once()
        assert customer_management_app.session is None # Should be closed

    def test_main_paragraph_connect_db_failure(self, customer_management_app, mock_boto3_client, mock_sqlalchemy, mocker):
        mock_boto3_client.get_secret_value.side_effect = ConnectionError("Secrets manager down")
        mocker.patch.object(customer_management_app, "_fetch_customer")
        mocker.patch.object(customer_management_app, "_call_external_svc")

        customer_management_app.main_paragraph()

        customer_management_app._fetch_customer.assert_not_called()
        customer_management_app._call_external_svc.assert_not_called()
        mock_sqlalchemy["session_instance"].close.assert_called_once() # Session should still attempt to close, even if not fully formed
        assert customer_management_app.session is None # Should be closed

    def test_main_paragraph_fetch_customer_failure(self, customer_management_app, mock_secrets_manager_success, mock_sqlalchemy, mocker):
        mock_sqlalchemy["session_instance"].query.side_effect = SQLAlchemyError("DB query failed")
        mocker.patch.object(customer_management_app, "_call_external_svc")

        customer_management_app.main_paragraph()

        customer_management_app._call_external_svc.assert_not_called()
        mock_sqlalchemy["session_instance"].close.assert_called_once()
        assert customer_management_app.session is None # Should be closed

    def test_main_paragraph_call_external_svc_failure(self, customer_management_app, mock_secrets_manager_success, mock_sqlalchemy, mock_customer_data, mocker):
        mock_sqlalchemy["session_instance"].query.return_value.filter_by.return_value.first.return_value = mock_customer_data
        
        # If _call_external_svc were to raise an error
        mocker.patch.object(customer_management_app, "_call_external_svc", side_effect=ValueError("External service error"))

        customer_management_app.main_paragraph()

        # All previous steps should have been called
        mock_secrets_manager_success.get_secret_value.assert_called_once()
        mock_sqlalchemy["engine"].assert_called_once()
        mock_sqlalchemy["session_instance"].query.assert_called_once_with(Customer)
        customer_management_app._call_external_svc.assert_called_once()
        
        # Ensure session is still closed in finally block
        mock_sqlalchemy["session_instance"].close.assert_called_once()
        assert customer_management_app.session is None # Should be closed