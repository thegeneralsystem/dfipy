"""
Manages identity authentication via the Identity Management API service.
"""
from typing import List

from dfi.connect import Connect


class Identities:
    """
    Class responsible handling identities and tokens.
    """

    def __init__(self, conn: Connect) -> None:
        self.conn = conn

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""

    def get_tokens(self, include_expired: bool = False) -> List[dict]:
        """
        Retrieve details about API tokens

        :param include_expired: set to `True` to include expired tokens in the list.  Defaults to False.
        :return: a list of API tokens.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)
        tokens = dfi.identities.get_tokens(include_expired=False)
        ```
        """
        params = {"includeExpired": str(include_expired).lower()}
        with self.conn.api_get("v1/tokens", params=params, stream=False) as response:
            response.raise_for_status()
            tokens: List[dict] = response.json()
            return tokens

    def create_token(self, name: str, validity: str) -> dict:
        """
        Generate a new API token for the current user.

        :param name: name for token.
        :param validity: how long the token is valid for.  Period of token validity in ISO8601 format. Default is 1 year.

            pattern: `^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d{1,3})?)S)?)?$`
            example: `"P1Y"`


        :return: information about the new token.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        name = "token_1"
        validity = "P1Y"
        token_info = dfi.identities.create_token(name, validity)
        token = token_info["token]
        ```
        """
        payload = {"name": name, "validity": validity}
        with self.conn.api_post("v1/tokens", payload=payload, stream=False) as response:
            response.raise_for_status()
            token_info: dict = response.json()
            return token_info

    def expire_token(self, token_id: str) -> None:
        """
        Expires the given api token.

        :::{note}
        It's previous existence can still be found with `dfi.get_tokens(include_expired=True)`
        :::

        :param token_id: id of token to expire.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        dfi.identities.expire_token("<token id>")
        ```
        """
        with self.conn.api_delete(f"v1/tokens/{token_id}", stream=False) as response:
            response.raise_for_status()
            return None

    def get_identities(self) -> List[dict]:
        """
        Retrieve a list of identities.

        :::{hint}
        You need to be an admin for this request.
        :::

        :return: None
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        identities = dfi.identities.get_identities()
        ```
        """
        with self.conn.api_get("v1/identities", stream=False) as response:
            response.raise_for_status()
            identities: List[dict] = response.json()
            return identities

    def get_my_identity(self) -> dict:
        """
        Retrieve data about the identity who made this request

        :return: None
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        identity = dfi.identities.get_my_identity()
        ```
        """
        with self.conn.api_get("v1/identities/me", stream=False) as response:
            response.raise_for_status()
            identity: dict = response.json()
            return identity

    def get_identity(self, identity_id: str) -> dict:
        """
        Retrieve data about a specific identity.

        :::{hint}
        You need to be an admin for this request.
        :::

        :param identity_id: an id of an identity.
        :return: the identity of the given id.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        identity = dfi.identities.get_identity("<identity id>")
        ```
        """
        with self.conn.api_get(f"v1/identities/{identity_id}", stream=False) as response:
            response.raise_for_status()
            identity: dict = response.json()
            return identity

    def _delete_identity(self, identity_id: str) -> None:
        """
        Remove an identity and all opaque tokens.

        :::{attention}
        This should be done in conjunction with removing the user.
        :::

        :::{hint}
        You need to be an admin for this request.
        :::

        :::{warning}
        Deleting the sole identity for a user makes the user unsearchable,
        which makes finding the id to then delete the user impossible.
        :::

        :param identity_id: an id of an identity.
        :return: None
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        identity = dfi.identities.delete_identity("<identity id>")
        ```
        """
        with self.conn.api_delete(f"v1/identities/{identity_id}", stream=False) as response:
            response.raise_for_status()
            return None

    def get_user_id(self, identity_id: str) -> str:
        """
        Returns the user_id for the identity_id.

        :param identity_id: an id of an identity.
        :return: user_id
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        user_id = dfi.identities.get_user_id("<identity id>")
        ```
        """
        return identity_id.split("|")[1]
