import json
from unittest.mock import MagicMock, patch

from sqlalchemy import Column, Integer, MetaData, String, Table

from backend.custom_skills import GetSQLDatabaseMetadata


@patch("backend.custom_skills.get_sql_database_metadata.UserVariableManager")
@patch("backend.custom_skills.get_sql_database_metadata.create_engine")
def test_get_sql_database_metadata_success(mock_create_engine, mock_user_variable_manager):
    # Mock the user variable manager to return database credentials
    mock_variable_storage = MagicMock()
    mock_variable_storage.get_by_key.side_effect = [
        "postgresql://username@host:5432/",  # DATABASE_URL_PREFIX
        "secret",  # DATABASE_PASSWORD
    ]
    mock_user_variable_manager.return_value = mock_variable_storage

    # Mock the SQLAlchemy engine and metadata reflection
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    metadata = MetaData()

    # Create mock tables
    users_table = Table(
        "users", metadata, Column("id", Integer, primary_key=True), Column("name", String), Column("email", String)
    )

    orders_table = Table(
        "orders",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("user_id", Integer),
        Column("amount", Integer),
    )

    metadata.tables = {"users": users_table, "orders": orders_table}

    mock_engine.connect.return_value.__enter__.return_value = MagicMock()
    metadata.reflect = MagicMock(return_value=None)

    tool = GetSQLDatabaseMetadata(database_name="testdb")
    response = tool.run()

    expected_output = (
        "Database Schema Information:\n\n"
        "Table: users\n"
        "  Column: id, Type: INTEGER\n"
        "  Column: name, Type: VARCHAR\n"
        "  Column: email, Type: VARCHAR\n\n"
        "Table: orders\n"
        "  Column: id, Type: INTEGER\n"
        "  Column: user_id, Type: INTEGER\n"
        "  Column: amount, Type: INTEGER\n"
    )

    assert response == expected_output
    metadata.reflect.assert_called_once_with(bind=mock_engine)


@patch("backend.custom_skills.get_sql_database_metadata.UserVariableManager")
@patch("backend.custom_skills.get_sql_database_metadata.create_engine")
def test_get_sql_database_metadata_failure(mock_create_engine, mock_user_variable_manager):
    mock_variable_storage = MagicMock()
    mock_variable_storage.get_by_key.side_effect = ["postgresql://username@host:5432/", "secret"]
    mock_user_variable_manager.return_value = mock_variable_storage

    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    metadata = MetaData()
    metadata.reflect.side_effect = Exception("Database connection error")

    tool = GetSQLDatabaseMetadata(database_name="testdb")
    response = tool.run()

    assert json.loads(response) == {"error": "An error occurred while processing the request"}
    metadata.reflect.assert_called_once_with(bind=mock_engine)
