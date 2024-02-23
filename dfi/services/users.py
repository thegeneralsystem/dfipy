"""
Manages user authentication via the User Management API service.
"""
from typing import List

from dfi.connect import Connect


class Users:
    """
    Class responsible handling users.
    """

    def __init__(self, conn: Connect) -> None:
        self.conn = conn

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""

    def create_user(self, user: dict) -> dict:
        """
        Create a new user.

        :::{hint}
        You need to be an admin for this request.
        :::

        :param user: a user specification to create.
        :return: the created user.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        user = {
            "userName": "iain.m.banks",
            "name": {
                "givenName": "Iain",
                "familyName": "Banks",
            },
            "emails": [
                {
                    "value": "iain.m.banks@organization.com",
                    "primary": True
                }
            ],
            "active": True,
        }
        created_user = dfi.users.create_user(user)
        ```
        """
        with self.conn.api_post("v1/users", payload=user, stream=False) as response:
            response.raise_for_status()
            created_user: dict = response.json()
            return created_user

    def get_users(self) -> List[dict]:
        """
        Retrieve the list of users in the realm. You need to be an admin for this request.

        :::{hint}
        You need to be an admin for this request.
        :::

        :param user_id: an id of a user.
        :return: the identity of the given id.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        users = dfi.users.get_users()
        ```
        """
        with self.conn.api_get("v1/users", stream=False) as response:
            response.raise_for_status()
            users: List[dict] = response.json()
            return users

    def get_user(self, user_id: str) -> dict:
        """
        Retrieve details about a user by id.

        :::{hint}
        You need to be an admin for this request.
        :::

        :param user_id: an id of a user.
        :return: the identity of the given id.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        identity = dfi.users.get_user("<user id>")
        ```
        """
        with self.conn.api_get(f"v1/users/{user_id}", stream=False) as response:
            response.raise_for_status()
            user: dict = response.json()
            return user

    def delete_user(self, user_id: str) -> None:
        """
        Removes a user from the system. This removes all identities and access tokens that exist for the user as well.

        :::{hint}
        You need to be an admin for this request.
        :::

        :param user_id: an id of a user.
        :return: the identity of the given id.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        identity = dfi.users.delete_user("<user id>")
        ```
        """
        with self.conn.api_delete(f"v1/users/{user_id}", stream=False) as response:
            response.raise_for_status()
            return None
