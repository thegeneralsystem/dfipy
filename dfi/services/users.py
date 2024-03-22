"""Manages user authentication via the User Management API service."""

from dfi.connect import Connect


class Users:
    """Class responsible handling users."""

    def __init__(self, conn: Connect) -> None:
        self.conn = conn

    def __repr__(self) -> str:
        """Class representation."""
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        """Class string formatting."""
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""

    def create_user(self, user: dict) -> dict:
        """Create a new user.

        ??? info "Endpoint"
            [POST /v1/users](https://api.prod.generalsystem.com/docs/api#/User%20Management%20(v1)/post_v1_users)

        ??? tip "Admin Request"
            You need to be an admin for this request.

        Parameters
        ----------
        user:
            a user specification to create.

        Returns
        -------
        user:
            the created user.

        Examples
        --------
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
                    "primary": True,
                }
            ],
            "active": True,
        }
        created_user = dfi.users.create_user(user)
        ```
        """
        with self.conn.api_post("v1/users", json=user, stream=False) as response:
            response.raise_for_status()
            created_user: dict = response.json()
            return created_user

    def get_users(self) -> list[dict]:
        """Retrieve the list of users in the realm.

        ??? info "Endpoint"
            [GET /v1/users](https://api.prod.generalsystem.com/docs/api#/User%20Management%20(v1)/get_v1_users)

        ??? tip "Admin Request"
            You need to be an admin for this request.

        Returns
        -------
        identity:
            the identity of the given id.

        Examples
        --------
        ```python
        from dfi import Client

        dfi = Client(token, url)

        users = dfi.users.get_users()
        ```
        """
        with self.conn.api_get("v1/users", stream=False) as response:
            response.raise_for_status()
            users: list[dict] = response.json()
            return users

    def get_user(self, user_id: str) -> dict:
        """Retrieve details about a user by id.

        ??? info "Endpoint"
            [GET /v1/users/{id}](https://api.prod.generalsystem.com/docs/api#/User%20Management%20(v1)/get_v1_users__id_)

        ??? tip "Admin Request"
            You need to be an admin for this request.

        Parameters
        ----------
        user_id:
            an id of a user.

        Returns
        -------
        identity:
            the identity of the given id.

        Examples
        --------
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
        """Remove a user from the system. This removes all identities and access tokens that exist for the user as well.

        ??? info "Endpoint"
            [DELETE /v1/users/{id}](https://api.prod.generalsystem.com/docs/api#/User%20Management%20(v1)/delete_v1_users__id_)

        ??? tip "Admin Request"
            You need to be an admin for this request.

        Parameters
        ----------
        user_id:
            an id of a user.

        Returns
        -------
        identity:
            the identity of the given id.

        Examples
        --------
        ```python
        from dfi import Client

        dfi = Client(token, url)

        identity = dfi.users.delete_user("<user id>")
        ```
        """
        with self.conn.api_delete(f"v1/users/{user_id}", stream=False) as response:
            response.raise_for_status()
            return None
