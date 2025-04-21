from typing import Any


def test_get_all_restaurants(
    mock_authorized_client: Any,
) -> None:

    response = mock_authorized_client.get(
        "/restaurant/mobile/get_all_restaurants",
        headers={"Authorization": "Bearer valid-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
