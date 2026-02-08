import pytest
from unittest.mock import MagicMock, patch
from app.api.cases import list_visa_cases

@pytest.mark.asyncio
async def test_list_visa_cases_query_count():
    # Mock result for data query
    mock_result_data = MagicMock()
    # Minimal data to satisfy VisaCaseResponse
    mock_result_data.data = [{
        "id": "1",
        "user_id": "user123",
        "nationality": "US",
        "visa_type": "F-1",
        "consulate": "London",
        "submission_date": "2023-01-01",
        "sponsor_type": "employer",
        "current_status": "pending",
        "created_at": "2023-01-01T00:00:00"
    }]
    mock_result_data.count = 1 # Data query now fetches count

    # Mock supabase client
    with patch("app.api.cases.supabase") as mock_supabase:
        # Create a mock query object that supports chaining
        mock_query = MagicMock()

        # Setup chaining structure
        mock_supabase.table.return_value = mock_query
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.range.return_value = mock_query
        mock_query.order.return_value = mock_query

        # Configure return value for execute
        mock_query.execute.return_value = mock_result_data

        # Call the function with a mocked user_id
        with patch("app.api.cases.get_user_id_from_token", return_value="user123"):
            response = await list_visa_cases(page=1, per_page=10, authorization="Bearer token")

        # Verify the response is correct (sanity check)
        assert response.total == 1
        assert len(response.items) == 1

        # Assert execute() was called ONLY ONCE (The Optimization)
        assert mock_query.execute.call_count == 1

        # Verify specific calls to ensure we are mocking the right thing
        # First select call
        # mock_supabase.table.assert_any_call("visa_cases")
