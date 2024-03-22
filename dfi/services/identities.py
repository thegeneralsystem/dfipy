"""Manages identity authentication via the Identity Management API service."""

from typing import Any

from dfi.connect import Connect


class Identities:
    """Class responsible handling identities and tokens."""

    def __init__(self, conn: Connect) -> None:
        self.conn = conn

    def __repr__(self) -> str:
        """Class representation."""
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        """Class string formatting."""
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""

    def get_tokens(self, include_expired: bool = False) -> list[dict]:
        """Retrieve details about API tokens.

        ??? info "Endpoint"
            [GET /v1/tokens](https://api.prod.generalsystem.com/docs/api#/Identity%20Management%20(v1)/get_v1_tokens)

        Parameters
        ----------
        include_expired:
            set to `True` to include expired tokens in the list.  Defaults to False.

        Returns
        -------
        tokens:
            a list of API tokens.

        Examples
        --------
        ```python
        from dfi import Client

        dfi = Client(token, url)
        tokens = dfi.identities.get_tokens(include_expired=False)
        ```
        """
        params = {"includeExpired": str(include_expired).lower()}
        with self.conn.api_get("v1/tokens", params=params, stream=False) as response:
            response.raise_for_status()
            tokens: list[dict] = response.json()
            return tokens

    def create_token(self, name: str, validity: str) -> dict:
        r"""Generate a new API token for the current user.

        ??? info "Endpoint"
            [POST /v1/tokens](https://api.prod.generalsystem.com/docs/api#/Identity%20Management%20(v1)/post_v1_tokens)

        Parameters
        ----------
        name:
            name for token.
        validity:
            how long the token is valid for.  Period of token validity in ISO8601 format. Default is 1 year.

            - pattern: `^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d{1,3})?)S)?)?$`
            - example: `"P1Y"`

        Returns
        -------
        token info:
            information about the new token.

        Examples
        --------
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
        with self.conn.api_post("v1/tokens", json=payload, stream=False) as response:
            response.raise_for_status()
            token_info: dict = response.json()
            return token_info

    def expire_token(self, token_id: str) -> None:
        """Expires the given api token.

        ??? info "Endpoint"
            [DELETE /v1/tokens/{id}](https://api.prod.generalsystem.com/docs/api#/Identity%20Management%20(v1)/delete_v1_identities__id_)

        ??? question "Finding an expired token"
            It's previous existence can still be found with `dfi.get_tokens(include_expired=True)`

        Parameters
        ----------
        token_id:
            the Token ID to expire.

        Examples
        --------
        ```python
        from dfi import Client

        dfi = Client(token, url)

        dfi.identities.expire_token("<token id>")
        ```
        """
        with self.conn.api_delete(f"v1/tokens/{token_id}", stream=False) as response:
            response.raise_for_status()
            return None

    def get_identities(self) -> list[dict[str, Any]]:
        """Retrieve a list of identities.

        ??? info "Endpoint"
            [GET /v1/identities](https://api.prod.generalsystem.com/docs/api#/Identity%20Management%20(v1)/get_v1_identities)

        ??? tip "Admin Request"
            You need to be an admin for this request.

        Returns
        -------
        identities:
            a list of identities

        Examples
        --------
        ```python
        from dfi import Client

        dfi = Client(token, url)

        identities = dfi.identities.get_identities()
        ```
        """
        with self.conn.api_get("v1/identities", stream=False) as response:
            response.raise_for_status()
            identities: list[dict[str, Any]] = response.json()
            return identities

    def get_my_identity(self) -> dict[str, Any]:
        """Retrieve data about the identity who made this request.

        ??? info "Endpoint"
            [GET /v1/identities/me](https://api.prod.generalsystem.com/docs/api#/Identity%20Management%20(v1)/get_v1_identities_me)

        Returns
        -------
        identity:
            the caller's identity

        Examples
        --------
        ```python
        from dfi import Client

        dfi = Client(token, url)

        identity = dfi.identities.get_my_identity()
        ```
        """
        with self.conn.api_get("v1/identities/me", stream=False) as response:
            response.raise_for_status()
            identity: dict[str, Any] = response.json()
            return identity

    def get_identity(self, identity_id: str) -> dict[str, Any]:
        """Retrieve data about a specific identity.

        ??? info "Endpoint"
            [GET /v1/identities/{id}](https://api.prod.generalsystem.com/docs/api#/Identity%20Management%20(v1)/get_v1_identities__id_)

        ??? tip "Admin Request"
            You need to be an admin for this request.

        Parameters
        ----------
        identity_id:
            an id of an identity.

        Returns
        -------
        identity:
            the identity of the given id.

        Examples
        --------
        ```python
        from dfi import Client

        dfi = Client(token, url)

        identity = dfi.identities.get_identity("<identity id>")
        ```
        """
        with self.conn.api_get(
            f"v1/identities/{identity_id}", stream=False
        ) as response:
            response.raise_for_status()
            identity: dict[str, Any] = response.json()
            return identity

    def _delete_identity(self, identity_id: str) -> None:
        """Remove an identity and all opaque tokens.

        ??? info "Endpoint"
            [DELETE /v1/identities/{id}](https://api.prod.generalsystem.com/docs/api#/Identity%20Management%20(v1)/delete_v1_identities__id_)

        ??? attention
            This should be done in conjunction with removing the user.

        ??? warning
            Deleting the sole identity for a user makes the user unsearchable,
            which makes finding the id to then delete the user impossible.

        ??? tip "Admin Request"
            You need to be an admin for this request.

        Parameters
        ----------
        identity_id:
            the identity id to be deleted.

        Examples
        --------
        ```python
        from dfi import Client

        dfi = Client(token, url)

        identity = dfi.identities.delete_identity("<identity id>")
        ```
        """
        with self.conn.api_delete(
            f"v1/identities/{identity_id}", stream=False
        ) as response:
            response.raise_for_status()
            return None

    def get_user_id(self, identity_id: str) -> str:
        """Extract the User ID from an Identity ID.

        Parameters
        ----------
        identity_id:
            the Identity ID to extract the matching User ID from.

        Returns
        -------
        user_id:
            the User ID associated to the given Identity ID

        Examples
        --------
        ```python
        from dfi import Client

        dfi = Client(token, url)

        user_id = dfi.identities.get_user_id("<identity id>")
        ```
        """
        return identity_id.split("|")[1]
