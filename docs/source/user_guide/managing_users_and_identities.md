(user-management)=

# Managing Users & Identities

:::{note}
Some methods require admin privileges. Refer to the documentation of individual methods.
:::

## I. Identity ID and User ID

A user has an identity. This identity is how we manage dataset access, administrative access, and other permissions across our API. In the future, there may be other types of identities separate from a User, eg: Services, IAM roles

- A `user_id` is a uuid, `12345678-1234-5678-1234-567812345678`.
- An `identity_id` has the form `<role>|<user_id>`. When a user is created, they have by default a user identity, e.g. `user|12345678-1234-5678-1234-567812345678`.

The `identity_id` and `user_id` can be retrieved via the `dfi.get_identities()` method. Here, we'll retrieve the `identity_id` and `user_id` for `name=iain.m.banks`.

### Retrieving a User ID

```python
dfi = Client(token, url)

name = "iain.m.banks"

users = dfi.users.get_users()
for user in users:
    if user["userName"] == name:
        user_id = user["id"]

print(user_id)
```

```text
User ID: 12345678-1234-5678-1234-567812345678
```

### Retrieving an Identity ID

```python
dfi = Client(token, url)

name = "iain.m.banks"

identities = dfi.identities.get_identities()
for identity in identities:
    if identity["name"] == name:
        identity_id = identity["id"]
        user_id = dfi.identities.get_user_id(identity_id)

print(identity_id)
```

```text
user|12345678-1234-5678-1234-567812345678
```

### Information about a User

```python
dfi = Client(token, url)

# identity for user "iain.m.banks"
identity_id = "user|12345678-1234-5678-1234-567812345678"

user_id = dfi.users.get_user_id(identity_id)
dfi.users.get_user(user_id)
```

```python
{
    "active": True,
    "id": "12345678-1234-5678-1234-567812345678",
    "userName": "iain.m.banks",
    "emails": [{"value": "iain.m.banks@organization.com", "primary": True}],
    "name": {"familyName": "Banks", "givenName": "Iain"},
    "meta": {
        "resourceType": "User",
        "lastModified": "2023-10-12T16:42:20.859Z",
        "created": "2023-10-12T16:42:20.859Z",
        "location": "https://api.dev.generalsystem.com/v1/users/12345678-1234-5678-1234-567812345678/12345678-1234-5678-1234-567812345678",
    },
    "defaultIdentity": {"admin": False, "appAccess": []},
}
```

(identities-information)=

### Information about an Identity

```python
dfi = Client(token, url)

# identity for user "iain.m.banks"
identity_id = "user|12345678-1234-5678-1234-567812345678"

dfi.users.get_identity(identity_id)
```

```text
{
    "id": "user|12345678-1234-5678-1234-567812345678",
    "name": "iain.m.banks",
    "createdAt": "2023-10-12T16:42:21.164Z",
    "updatedAt": "2023-10-12T16:42:21.164Z",
    "admin": False,
}
```

(current-identity-information)=

### Information about Current Identity

```python
dfi = Client(token, url)

identity = dfi.identities.get_my_identity()
```

## II. Creating a New User

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
    "defaultIdentity": {
        "admin": False,
        "appAccess": []
    }
}
created_user = dfi.users.create_user(user)
identity_id = created_user["id"]
```

Where:

- `userName` - Username to create. This is the name that will be searchable in the results from `dfi.get_identities()`.
- `emails` - Email address(es) to use for the newly created user.
- `admin` - If you want to create a tenant admin user, set to `True`. If you don't, then don't set this variable.
- `appAccess` - If you want to allow the user access to specific apps, add the name of the app to the list, e.g. `[insight]`. If you don't, then don't set this variable.

:::{note}
If creating a non-admin user without special access to apps, the `defaultIdentity` key may be omitted from the user definition. The default is:

```python
"defaultIdentity": {
    "admin": False,
    "appAccess": []
}
```

:::

## III. Tokens

### Create a New Token

Creating a new token for the current identity will return a packet of information about the token. The `token` key holds the token.

:::{attention}
Once you create a token, make sure to save it somewhere safe. Tokens cannot be retrieved again for security reasons. Information about the token may be retrieved. If a token is lost, you can delete it and create another one.
:::

```python
dfi = Client(token, url)

name = "test-token"
validity = "P1Y"
dfi.identities.create_token(name, validity)
```

```text
{
    "token": "gs1de38197314eb17d75bb48c452b25903f48a8b20464f30e7d5fce1c4f3922ebc",
    "data": {
        "id": "b89c9857-1d71-4b62-a320-488ebc295979",
        "identityId": "user|83d35335-e372-419a-80e8-e7c19e22427d",
        "name": "test-token",
        "expired": False,
        "createdAt": "2023-10-12T16:49:30.295Z",
        "expireAt": "2024-10-11T16:49:30.295Z",
    },
}
```

Where:

- `name` - name for the token.
- `validity` - how long the token is valid for. Period of token validity in ISO8601 format. Default is 1 year.
  - pattern: `^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d{1,3})?)S)?)?$`
  - example: `"P1Y"`

### Expire a Token

Tokens may be expired, meaning information about the token is still available but the token will no longer work. It's previous existence can still be found with `dfi.get_tokens(include_expired=True)`.

Here, we want to expire the token named `test-token`. To do so, we retrieve all tokens that are still valid and find the one named `test-token`. We then use the associated token id in the `id` key to expire the token.

```python
dfi = Client(token, url)

tokens = dfi.identities.get_tokens(include_expired=False)
for token in tokens:
    if token["name"] == "test-token":
        token_id = token["id"]
        dfi.identities.expire_token(token_id)
```
