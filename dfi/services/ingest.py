"""
Manages ingest of data via the Import API service.  

Note: we use the name "ingest" instead of using the API name of "import" because it's a 
reserved name in Python.
"""
import json
from typing import List, Optional

import boto3
import natsort
from botocore.client import Config
from tqdm import tqdm

from dfi.connect import Connect


class AWSCredentials:
    """A constructor class for building an AWSCreedentials document.
    Parameters which point to an AWS role that the importer will assume to scan and download files.
    These parameters are a subset of the aws AssumeRoleCommand
    https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/clients/client-account/classes/assumerolecommand.html

    :example:
    ```python
    from dfi.services.ingest import AWSCredentials

    role_arn = "arn:aws:s3:::example_bucket/example_key"
    AWSCredentials(role_arn).build()
    ```
    ```python
    {"RoleArn": "arn:aws:s3:::example_bucket/example_key"}
    ```
    """

    def __init__(self, role_arn: str, policy: Optional[dict] = None, policy_arns: Optional[List[str]] = None) -> None:
        """
        :role_arn: The Amazon Resource Name (ARN) of the AWS role for us to assume.
        :policy: a JSON policy that we should use when assuming the role.
        :policy_arns: a list of Policy ARNs to use as managed session policies.
        """
        self.role_arn = role_arn
        self.policy = policy
        self.policy_arns = policy_arns

    def build(self) -> dict:
        """Builds an AWSCredentials document from given inputs.
        :returns: An AWSCredentials document.
        """
        aws_credentials = {"RoleArn": self.role_arn}
        if self.policy:
            aws_credentials.update({"Policy": self.policy})
        if self.policy_arns:
            aws_credentials.update({"PolicyArns": self.policy_arns})

        return aws_credentials


class BatchURLFiles:
    """A constructor class for building an BatchURLFiles document.
    Indicates that this import batch should source files from a provided list of URLs.

    :example:
    In this example, we've generated presigned URLs for 4 files on S3.  These files can now be ingested without
    needing to share AWS credentials.
    ```python
    from dfi.services.ingest import BatchURLFiles

    urls = [
        "https://bucket-name.s3.eu-west-2.amazonaws.com/sample-data/file-1.csv?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEOX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJGMEQCICzap9Nfx0BY9IPhrWCPEWwiR4OYW%2BxxheB%2FeorchP6QAiB5lRoXq3cjr%2BTFMvjuvGoCTaMxw9T4SzbYoUzIDMtIwyqoBAiO%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAMaDDY2OTM1OTQ2MDU1NCIMAGNCpXF5mRRjsS7mKvwDcOy9VbRwNRJKZFkEdUtcXHRkKTFw1t%2FSYDaqE%2BrdEhV01bV7v5uuEJQye9zI24r%2FHJvS1dolfumoaDdjkkI6%2FtODeGo0WiZsrI8yOxCFL6WCDnEIS%2F9VJpN7MdXR9kdMhPu1crhOM52PmD0QUO6jckS1RoxXyDChrW6xB9dI7w6h%2F%2B674gHg8De%2BAvJFe45eGYqPNogwLPQN4oW4jSCHPJRwhUp9h2aAEniHQzpqnFvJbbG2CsQMdf99%2FHpGyxGaIfh%2B5fm2ZOEWjWrAFxLSd1ad4uJSRLfQK8IYtgZ6dSi6B%2FcxSNY3fNFqY3ATNAiMkDFfnF%2FAVzyoPH7t6VIgG9LKTpvx8kYQdR1aonq4LDotsKwjTwUhgiYmbTcr%2FE1cIHLdErbKjlQgI%2BRX%2FrXRjQGPsEOeIIlY4OT4S%2FZgr4ZR0PkqvgNxXDiJ3frnWUW%2F8eFa%2FS4iSF%2FWHbcVYPacZSw9udBJWMVfLGWw6kXpJwpblBJC05b4NPWhrQH%2BwcJOttApbVqP7P8sbRnWM6%2BABUOtXBjh1nfO4BsZ8JvZ7PVxjGF356bRvmv7B02QQ3NJ3jZdX6SmGJuOIbk2tqDOOOx09zanbcJu%2BcqI9O%2Fhiq4zAWiuyznWDvIud37Jh8MLvB0NFeyUCKIFAHNJ8PGBJeVa56TEsv%2B4PHazwDCZ1JStBjqVAjS07YXEoBoexua24awKZlieU%2F%2B2Bj%2FY9iT7Ufyb6W0uBhAxcEw1q1K728Bn3Kkygn8iD3AZjH%2BP6421sfksEovUDsZfXt7b6v0yCK0RzUhYlAiZnd0mqmFCggJnKgG4TGL8BQ5ZdqcZDWcMAAoKYzRU7MM5u8yQxblAC3exQbR01OOBFYSiDHhtikf0AjvVS%2BzCNAdyw9%2BbdPAk%2FvE6wmOxgHUZZ7pu4ofnCs1vEDmDNP8E5wYUbcahvb98P5IcinMQvQ%2FifQDo8sE3Xhq2sOXpVE3IkTdx%2FfDGI8cuMDzVzJmI1juN53tqkixUNmIzLoNSf%2F4hBU0DOb%2BZz5Gqeu1W0jxifqOPmMU932ItuY3Wy28L8cY%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240115T160635Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIAZXWHO2DFNXQNNMLW%2F20240115%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Signature=f79e998106566500767b3403304e323c8ce949a1a0d98bbf4224662e605b10db",
        "https://bucket-name.s3.eu-west-2.amazonaws.com/sample-data/file-2.csv?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEOX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJGMEQCICzap9Nfx0BY9IPhrWCPEWwiR4OYW%2BxxheB%2FeorchP6QAiB5lRoXq3cjr%2BTFMvjuvGoCTaMxw9T4SzbYoUzIDMtIwyqoBAiO%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAMaDDY2OTM1OTQ2MDU1NCIMAGNCpXF5mRRjsS7mKvwDcOy9VbRwNRJKZFkEdUtcXHRkKTFw1t%2FSYDaqE%2BrdEhV01bV7v5uuEJQye9zI24r%2FHJvS1dolfumoaDdjkkI6%2FtODeGo0WiZsrI8yOxCFL6WCDnEIS%2F9VJpN7MdXR9kdMhPu1crhOM52PmD0QUO6jckS1RoxXyDChrW6xB9dI7w6h%2F%2B674gHg8De%2BAvJFe45eGYqPNogwLPQN4oW4jSCHPJRwhUp9h2aAEniHQzpqnFvJbbG2CsQMdf99%2FHpGyxGaIfh%2B5fm2ZOEWjWrAFxLSd1ad4uJSRLfQK8IYtgZ6dSi6B%2FcxSNY3fNFqY3ATNAiMkDFfnF%2FAVzyoPH7t6VIgG9LKTpvx8kYQdR1aonq4LDotsKwjTwUhgiYmbTcr%2FE1cIHLdErbKjlQgI%2BRX%2FrXRjQGPsEOeIIlY4OT4S%2FZgr4ZR0PkqvgNxXDiJ3frnWUW%2F8eFa%2FS4iSF%2FWHbcVYPacZSw9udBJWMVfLGWw6kXpJwpblBJC05b4NPWhrQH%2BwcJOttApbVqP7P8sbRnWM6%2BABUOtXBjh1nfO4BsZ8JvZ7PVxjGF356bRvmv7B02QQ3NJ3jZdX6SmGJuOIbk2tqDOOOx09zanbcJu%2BcqI9O%2Fhiq4zAWiuyznWDvIud37Jh8MLvB0NFeyUCKIFAHNJ8PGBJeVa56TEsv%2B4PHazwDCZ1JStBjqVAjS07YXEoBoexua24awKZlieU%2F%2B2Bj%2FY9iT7Ufyb6W0uBhAxcEw1q1K728Bn3Kkygn8iD3AZjH%2BP6421sfksEovUDsZfXt7b6v0yCK0RzUhYlAiZnd0mqmFCggJnKgG4TGL8BQ5ZdqcZDWcMAAoKYzRU7MM5u8yQxblAC3exQbR01OOBFYSiDHhtikf0AjvVS%2BzCNAdyw9%2BbdPAk%2FvE6wmOxgHUZZ7pu4ofnCs1vEDmDNP8E5wYUbcahvb98P5IcinMQvQ%2FifQDo8sE3Xhq2sOXpVE3IkTdx%2FfDGI8cuMDzVzJmI1juN53tqkixUNmIzLoNSf%2F4hBU0DOb%2BZz5Gqeu1W0jxifqOPmMU932ItuY3Wy28L8cY%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240115T160658Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIAZXWHO2DFNXQNNMLW%2F20240115%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Signature=516f0a60a759b134e2dcd2fbdba1b48cf618b1e870ee9b462c6fd8facca39553",
        "https://bucket-name.s3.eu-west-2.amazonaws.com/sample-data/file-3.csv?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEOX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJGMEQCICzap9Nfx0BY9IPhrWCPEWwiR4OYW%2BxxheB%2FeorchP6QAiB5lRoXq3cjr%2BTFMvjuvGoCTaMxw9T4SzbYoUzIDMtIwyqoBAiO%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAMaDDY2OTM1OTQ2MDU1NCIMAGNCpXF5mRRjsS7mKvwDcOy9VbRwNRJKZFkEdUtcXHRkKTFw1t%2FSYDaqE%2BrdEhV01bV7v5uuEJQye9zI24r%2FHJvS1dolfumoaDdjkkI6%2FtODeGo0WiZsrI8yOxCFL6WCDnEIS%2F9VJpN7MdXR9kdMhPu1crhOM52PmD0QUO6jckS1RoxXyDChrW6xB9dI7w6h%2F%2B674gHg8De%2BAvJFe45eGYqPNogwLPQN4oW4jSCHPJRwhUp9h2aAEniHQzpqnFvJbbG2CsQMdf99%2FHpGyxGaIfh%2B5fm2ZOEWjWrAFxLSd1ad4uJSRLfQK8IYtgZ6dSi6B%2FcxSNY3fNFqY3ATNAiMkDFfnF%2FAVzyoPH7t6VIgG9LKTpvx8kYQdR1aonq4LDotsKwjTwUhgiYmbTcr%2FE1cIHLdErbKjlQgI%2BRX%2FrXRjQGPsEOeIIlY4OT4S%2FZgr4ZR0PkqvgNxXDiJ3frnWUW%2F8eFa%2FS4iSF%2FWHbcVYPacZSw9udBJWMVfLGWw6kXpJwpblBJC05b4NPWhrQH%2BwcJOttApbVqP7P8sbRnWM6%2BABUOtXBjh1nfO4BsZ8JvZ7PVxjGF356bRvmv7B02QQ3NJ3jZdX6SmGJuOIbk2tqDOOOx09zanbcJu%2BcqI9O%2Fhiq4zAWiuyznWDvIud37Jh8MLvB0NFeyUCKIFAHNJ8PGBJeVa56TEsv%2B4PHazwDCZ1JStBjqVAjS07YXEoBoexua24awKZlieU%2F%2B2Bj%2FY9iT7Ufyb6W0uBhAxcEw1q1K728Bn3Kkygn8iD3AZjH%2BP6421sfksEovUDsZfXt7b6v0yCK0RzUhYlAiZnd0mqmFCggJnKgG4TGL8BQ5ZdqcZDWcMAAoKYzRU7MM5u8yQxblAC3exQbR01OOBFYSiDHhtikf0AjvVS%2BzCNAdyw9%2BbdPAk%2FvE6wmOxgHUZZ7pu4ofnCs1vEDmDNP8E5wYUbcahvb98P5IcinMQvQ%2FifQDo8sE3Xhq2sOXpVE3IkTdx%2FfDGI8cuMDzVzJmI1juN53tqkixUNmIzLoNSf%2F4hBU0DOb%2BZz5Gqeu1W0jxifqOPmMU932ItuY3Wy28L8cY%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240115T160742Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIAZXWHO2DFNXQNNMLW%2F20240115%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Signature=18071e2d0cf194a27724bdd01e20ba00537d5bdeb81f43547c52cf7e654f4577",
        "https://bucket-name.s3.eu-west-2.amazonaws.com/sample-data/file-4.csv?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEOX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJGMEQCICzap9Nfx0BY9IPhrWCPEWwiR4OYW%2BxxheB%2FeorchP6QAiB5lRoXq3cjr%2BTFMvjuvGoCTaMxw9T4SzbYoUzIDMtIwyqoBAiO%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAMaDDY2OTM1OTQ2MDU1NCIMAGNCpXF5mRRjsS7mKvwDcOy9VbRwNRJKZFkEdUtcXHRkKTFw1t%2FSYDaqE%2BrdEhV01bV7v5uuEJQye9zI24r%2FHJvS1dolfumoaDdjkkI6%2FtODeGo0WiZsrI8yOxCFL6WCDnEIS%2F9VJpN7MdXR9kdMhPu1crhOM52PmD0QUO6jckS1RoxXyDChrW6xB9dI7w6h%2F%2B674gHg8De%2BAvJFe45eGYqPNogwLPQN4oW4jSCHPJRwhUp9h2aAEniHQzpqnFvJbbG2CsQMdf99%2FHpGyxGaIfh%2B5fm2ZOEWjWrAFxLSd1ad4uJSRLfQK8IYtgZ6dSi6B%2FcxSNY3fNFqY3ATNAiMkDFfnF%2FAVzyoPH7t6VIgG9LKTpvx8kYQdR1aonq4LDotsKwjTwUhgiYmbTcr%2FE1cIHLdErbKjlQgI%2BRX%2FrXRjQGPsEOeIIlY4OT4S%2FZgr4ZR0PkqvgNxXDiJ3frnWUW%2F8eFa%2FS4iSF%2FWHbcVYPacZSw9udBJWMVfLGWw6kXpJwpblBJC05b4NPWhrQH%2BwcJOttApbVqP7P8sbRnWM6%2BABUOtXBjh1nfO4BsZ8JvZ7PVxjGF356bRvmv7B02QQ3NJ3jZdX6SmGJuOIbk2tqDOOOx09zanbcJu%2BcqI9O%2Fhiq4zAWiuyznWDvIud37Jh8MLvB0NFeyUCKIFAHNJ8PGBJeVa56TEsv%2B4PHazwDCZ1JStBjqVAjS07YXEoBoexua24awKZlieU%2F%2B2Bj%2FY9iT7Ufyb6W0uBhAxcEw1q1K728Bn3Kkygn8iD3AZjH%2BP6421sfksEovUDsZfXt7b6v0yCK0RzUhYlAiZnd0mqmFCggJnKgG4TGL8BQ5ZdqcZDWcMAAoKYzRU7MM5u8yQxblAC3exQbR01OOBFYSiDHhtikf0AjvVS%2BzCNAdyw9%2BbdPAk%2FvE6wmOxgHUZZ7pu4ofnCs1vEDmDNP8E5wYUbcahvb98P5IcinMQvQ%2FifQDo8sE3Xhq2sOXpVE3IkTdx%2FfDGI8cuMDzVzJmI1juN53tqkixUNmIzLoNSf%2F4hBU0DOb%2BZz5Gqeu1W0jxifqOPmMU932ItuY3Wy28L8cY%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240115T160758Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIAZXWHO2DFNXQNNMLW%2F20240115%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Signature=71dbfc6d32ff820fdde98c1add38ce6ad153e450a919fe9f1368a75f8d5b3765",
    ]
    BatchURLFiles(urls).build()
    ```
    ```python
    {
        "urls":  [
            "https://bucket-name.s3.eu-west-2.amazonaws.com/sample-data/file-1.csv?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEOX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJGMEQCICzap9Nfx0BY9IPhrWCPEWwiR4OYW%2BxxheB%2FeorchP6QAiB5lRoXq3cjr%2BTFMvjuvGoCTaMxw9T4SzbYoUzIDMtIwyqoBAiO%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAMaDDY2OTM1OTQ2MDU1NCIMAGNCpXF5mRRjsS7mKvwDcOy9VbRwNRJKZFkEdUtcXHRkKTFw1t%2FSYDaqE%2BrdEhV01bV7v5uuEJQye9zI24r%2FHJvS1dolfumoaDdjkkI6%2FtODeGo0WiZsrI8yOxCFL6WCDnEIS%2F9VJpN7MdXR9kdMhPu1crhOM52PmD0QUO6jckS1RoxXyDChrW6xB9dI7w6h%2F%2B674gHg8De%2BAvJFe45eGYqPNogwLPQN4oW4jSCHPJRwhUp9h2aAEniHQzpqnFvJbbG2CsQMdf99%2FHpGyxGaIfh%2B5fm2ZOEWjWrAFxLSd1ad4uJSRLfQK8IYtgZ6dSi6B%2FcxSNY3fNFqY3ATNAiMkDFfnF%2FAVzyoPH7t6VIgG9LKTpvx8kYQdR1aonq4LDotsKwjTwUhgiYmbTcr%2FE1cIHLdErbKjlQgI%2BRX%2FrXRjQGPsEOeIIlY4OT4S%2FZgr4ZR0PkqvgNxXDiJ3frnWUW%2F8eFa%2FS4iSF%2FWHbcVYPacZSw9udBJWMVfLGWw6kXpJwpblBJC05b4NPWhrQH%2BwcJOttApbVqP7P8sbRnWM6%2BABUOtXBjh1nfO4BsZ8JvZ7PVxjGF356bRvmv7B02QQ3NJ3jZdX6SmGJuOIbk2tqDOOOx09zanbcJu%2BcqI9O%2Fhiq4zAWiuyznWDvIud37Jh8MLvB0NFeyUCKIFAHNJ8PGBJeVa56TEsv%2B4PHazwDCZ1JStBjqVAjS07YXEoBoexua24awKZlieU%2F%2B2Bj%2FY9iT7Ufyb6W0uBhAxcEw1q1K728Bn3Kkygn8iD3AZjH%2BP6421sfksEovUDsZfXt7b6v0yCK0RzUhYlAiZnd0mqmFCggJnKgG4TGL8BQ5ZdqcZDWcMAAoKYzRU7MM5u8yQxblAC3exQbR01OOBFYSiDHhtikf0AjvVS%2BzCNAdyw9%2BbdPAk%2FvE6wmOxgHUZZ7pu4ofnCs1vEDmDNP8E5wYUbcahvb98P5IcinMQvQ%2FifQDo8sE3Xhq2sOXpVE3IkTdx%2FfDGI8cuMDzVzJmI1juN53tqkixUNmIzLoNSf%2F4hBU0DOb%2BZz5Gqeu1W0jxifqOPmMU932ItuY3Wy28L8cY%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240115T160635Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIAZXWHO2DFNXQNNMLW%2F20240115%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Signature=f79e998106566500767b3403304e323c8ce949a1a0d98bbf4224662e605b10db",
            "https://bucket-name.s3.eu-west-2.amazonaws.com/sample-data/file-2.csv?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEOX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJGMEQCICzap9Nfx0BY9IPhrWCPEWwiR4OYW%2BxxheB%2FeorchP6QAiB5lRoXq3cjr%2BTFMvjuvGoCTaMxw9T4SzbYoUzIDMtIwyqoBAiO%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAMaDDY2OTM1OTQ2MDU1NCIMAGNCpXF5mRRjsS7mKvwDcOy9VbRwNRJKZFkEdUtcXHRkKTFw1t%2FSYDaqE%2BrdEhV01bV7v5uuEJQye9zI24r%2FHJvS1dolfumoaDdjkkI6%2FtODeGo0WiZsrI8yOxCFL6WCDnEIS%2F9VJpN7MdXR9kdMhPu1crhOM52PmD0QUO6jckS1RoxXyDChrW6xB9dI7w6h%2F%2B674gHg8De%2BAvJFe45eGYqPNogwLPQN4oW4jSCHPJRwhUp9h2aAEniHQzpqnFvJbbG2CsQMdf99%2FHpGyxGaIfh%2B5fm2ZOEWjWrAFxLSd1ad4uJSRLfQK8IYtgZ6dSi6B%2FcxSNY3fNFqY3ATNAiMkDFfnF%2FAVzyoPH7t6VIgG9LKTpvx8kYQdR1aonq4LDotsKwjTwUhgiYmbTcr%2FE1cIHLdErbKjlQgI%2BRX%2FrXRjQGPsEOeIIlY4OT4S%2FZgr4ZR0PkqvgNxXDiJ3frnWUW%2F8eFa%2FS4iSF%2FWHbcVYPacZSw9udBJWMVfLGWw6kXpJwpblBJC05b4NPWhrQH%2BwcJOttApbVqP7P8sbRnWM6%2BABUOtXBjh1nfO4BsZ8JvZ7PVxjGF356bRvmv7B02QQ3NJ3jZdX6SmGJuOIbk2tqDOOOx09zanbcJu%2BcqI9O%2Fhiq4zAWiuyznWDvIud37Jh8MLvB0NFeyUCKIFAHNJ8PGBJeVa56TEsv%2B4PHazwDCZ1JStBjqVAjS07YXEoBoexua24awKZlieU%2F%2B2Bj%2FY9iT7Ufyb6W0uBhAxcEw1q1K728Bn3Kkygn8iD3AZjH%2BP6421sfksEovUDsZfXt7b6v0yCK0RzUhYlAiZnd0mqmFCggJnKgG4TGL8BQ5ZdqcZDWcMAAoKYzRU7MM5u8yQxblAC3exQbR01OOBFYSiDHhtikf0AjvVS%2BzCNAdyw9%2BbdPAk%2FvE6wmOxgHUZZ7pu4ofnCs1vEDmDNP8E5wYUbcahvb98P5IcinMQvQ%2FifQDo8sE3Xhq2sOXpVE3IkTdx%2FfDGI8cuMDzVzJmI1juN53tqkixUNmIzLoNSf%2F4hBU0DOb%2BZz5Gqeu1W0jxifqOPmMU932ItuY3Wy28L8cY%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240115T160658Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIAZXWHO2DFNXQNNMLW%2F20240115%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Signature=516f0a60a759b134e2dcd2fbdba1b48cf618b1e870ee9b462c6fd8facca39553",
            "https://bucket-name.s3.eu-west-2.amazonaws.com/sample-data/file-3.csv?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEOX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJGMEQCICzap9Nfx0BY9IPhrWCPEWwiR4OYW%2BxxheB%2FeorchP6QAiB5lRoXq3cjr%2BTFMvjuvGoCTaMxw9T4SzbYoUzIDMtIwyqoBAiO%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAMaDDY2OTM1OTQ2MDU1NCIMAGNCpXF5mRRjsS7mKvwDcOy9VbRwNRJKZFkEdUtcXHRkKTFw1t%2FSYDaqE%2BrdEhV01bV7v5uuEJQye9zI24r%2FHJvS1dolfumoaDdjkkI6%2FtODeGo0WiZsrI8yOxCFL6WCDnEIS%2F9VJpN7MdXR9kdMhPu1crhOM52PmD0QUO6jckS1RoxXyDChrW6xB9dI7w6h%2F%2B674gHg8De%2BAvJFe45eGYqPNogwLPQN4oW4jSCHPJRwhUp9h2aAEniHQzpqnFvJbbG2CsQMdf99%2FHpGyxGaIfh%2B5fm2ZOEWjWrAFxLSd1ad4uJSRLfQK8IYtgZ6dSi6B%2FcxSNY3fNFqY3ATNAiMkDFfnF%2FAVzyoPH7t6VIgG9LKTpvx8kYQdR1aonq4LDotsKwjTwUhgiYmbTcr%2FE1cIHLdErbKjlQgI%2BRX%2FrXRjQGPsEOeIIlY4OT4S%2FZgr4ZR0PkqvgNxXDiJ3frnWUW%2F8eFa%2FS4iSF%2FWHbcVYPacZSw9udBJWMVfLGWw6kXpJwpblBJC05b4NPWhrQH%2BwcJOttApbVqP7P8sbRnWM6%2BABUOtXBjh1nfO4BsZ8JvZ7PVxjGF356bRvmv7B02QQ3NJ3jZdX6SmGJuOIbk2tqDOOOx09zanbcJu%2BcqI9O%2Fhiq4zAWiuyznWDvIud37Jh8MLvB0NFeyUCKIFAHNJ8PGBJeVa56TEsv%2B4PHazwDCZ1JStBjqVAjS07YXEoBoexua24awKZlieU%2F%2B2Bj%2FY9iT7Ufyb6W0uBhAxcEw1q1K728Bn3Kkygn8iD3AZjH%2BP6421sfksEovUDsZfXt7b6v0yCK0RzUhYlAiZnd0mqmFCggJnKgG4TGL8BQ5ZdqcZDWcMAAoKYzRU7MM5u8yQxblAC3exQbR01OOBFYSiDHhtikf0AjvVS%2BzCNAdyw9%2BbdPAk%2FvE6wmOxgHUZZ7pu4ofnCs1vEDmDNP8E5wYUbcahvb98P5IcinMQvQ%2FifQDo8sE3Xhq2sOXpVE3IkTdx%2FfDGI8cuMDzVzJmI1juN53tqkixUNmIzLoNSf%2F4hBU0DOb%2BZz5Gqeu1W0jxifqOPmMU932ItuY3Wy28L8cY%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240115T160742Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIAZXWHO2DFNXQNNMLW%2F20240115%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Signature=18071e2d0cf194a27724bdd01e20ba00537d5bdeb81f43547c52cf7e654f4577",
            "https://bucket-name.s3.eu-west-2.amazonaws.com/sample-data/file-4.csv?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEOX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJGMEQCICzap9Nfx0BY9IPhrWCPEWwiR4OYW%2BxxheB%2FeorchP6QAiB5lRoXq3cjr%2BTFMvjuvGoCTaMxw9T4SzbYoUzIDMtIwyqoBAiO%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAMaDDY2OTM1OTQ2MDU1NCIMAGNCpXF5mRRjsS7mKvwDcOy9VbRwNRJKZFkEdUtcXHRkKTFw1t%2FSYDaqE%2BrdEhV01bV7v5uuEJQye9zI24r%2FHJvS1dolfumoaDdjkkI6%2FtODeGo0WiZsrI8yOxCFL6WCDnEIS%2F9VJpN7MdXR9kdMhPu1crhOM52PmD0QUO6jckS1RoxXyDChrW6xB9dI7w6h%2F%2B674gHg8De%2BAvJFe45eGYqPNogwLPQN4oW4jSCHPJRwhUp9h2aAEniHQzpqnFvJbbG2CsQMdf99%2FHpGyxGaIfh%2B5fm2ZOEWjWrAFxLSd1ad4uJSRLfQK8IYtgZ6dSi6B%2FcxSNY3fNFqY3ATNAiMkDFfnF%2FAVzyoPH7t6VIgG9LKTpvx8kYQdR1aonq4LDotsKwjTwUhgiYmbTcr%2FE1cIHLdErbKjlQgI%2BRX%2FrXRjQGPsEOeIIlY4OT4S%2FZgr4ZR0PkqvgNxXDiJ3frnWUW%2F8eFa%2FS4iSF%2FWHbcVYPacZSw9udBJWMVfLGWw6kXpJwpblBJC05b4NPWhrQH%2BwcJOttApbVqP7P8sbRnWM6%2BABUOtXBjh1nfO4BsZ8JvZ7PVxjGF356bRvmv7B02QQ3NJ3jZdX6SmGJuOIbk2tqDOOOx09zanbcJu%2BcqI9O%2Fhiq4zAWiuyznWDvIud37Jh8MLvB0NFeyUCKIFAHNJ8PGBJeVa56TEsv%2B4PHazwDCZ1JStBjqVAjS07YXEoBoexua24awKZlieU%2F%2B2Bj%2FY9iT7Ufyb6W0uBhAxcEw1q1K728Bn3Kkygn8iD3AZjH%2BP6421sfksEovUDsZfXt7b6v0yCK0RzUhYlAiZnd0mqmFCggJnKgG4TGL8BQ5ZdqcZDWcMAAoKYzRU7MM5u8yQxblAC3exQbR01OOBFYSiDHhtikf0AjvVS%2BzCNAdyw9%2BbdPAk%2FvE6wmOxgHUZZ7pu4ofnCs1vEDmDNP8E5wYUbcahvb98P5IcinMQvQ%2FifQDo8sE3Xhq2sOXpVE3IkTdx%2FfDGI8cuMDzVzJmI1juN53tqkixUNmIzLoNSf%2F4hBU0DOb%2BZz5Gqeu1W0jxifqOPmMU932ItuY3Wy28L8cY%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240115T160758Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIAZXWHO2DFNXQNNMLW%2F20240115%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Signature=71dbfc6d32ff820fdde98c1add38ce6ad153e450a919fe9f1368a75f8d5b3765",
        ]
    }
    ```
    """

    def __init__(self, urls: List[str]) -> None:
        self.urls = urls

    def build(self) -> dict:
        """Builds a BatchURLFiles document from given inputs."""
        return {"urls": self.urls}


class BatchS3Files:
    """A constructor class for building an BatchS3Files document.
    Indicates that this import batch should source files from S3.
    :example:
    ```python
    from dfi.services.ingest import AWSCredentials, BatchS3Files

    role_arn = "arn:aws:s3:::example_bucket/example_key"
    credentials = AWSCredentials(role_arn)
    bucket = "s3://bucket-name"
    glob = "*.csv"
    prefix = "sample-data"

    BatchS3Files(bucket, credentials, glob, prefix).build()
    ```
    ```python
    {
        "s3": {
            "bucket": "s3://bucket-name",
            "credentials": {
                "RoleArn": "arn:aws:s3:::example_bucket/example_key"
            },
            "glob": "*.csv",
            "prefix": "sample-data"
        }
    }
    ```
    """

    def __init__(self, bucket: str, credentials: AWSCredentials, glob: str, prefix: Optional[str]) -> None:
        """
        :bucket: The S3 bucket to download files from. This can be an s3:// format url, or a full URL.
        :credentials: Parameters which point to an AWS role that the importer will assume to scan and download files.
            The `AWSCredentials` builder can help construct this document.
        :glob: A filename descriptor which indicates what format files to download.  example: `**/*.csv`
        :prefix: only download files in the S3 bucket which start with this prefix.
        """
        self.bucket = bucket
        self.credentials = credentials
        self.glob = glob
        self.prefix = prefix

    def build(self) -> dict:
        """Builds a BatchS3Files document from given inputs."""
        s3_source_descriptor = {"bucket": self.bucket, "credentials": self.credentials.build(), "glob": self.glob}

        if self.prefix:
            s3_source_descriptor.update({"prefix": self.prefix})

        return {"s3": s3_source_descriptor}


class CSVFormat:
    """A constructor class for building an CSVFormat document.
    An object indicating how to map columns in a CSV file into points to be imported to the Data Flow Index
    :example:
    ```python
    from dfi.services.ingest import CSVFormat

    # required fields
    entity_id = 0
    timestamp = 1
    longitude = 2
    latitude = 3

    # extra fields
    ipv4 = 4
    age = 5
    home_ipv4 = 6
    route_id = 7
    credit_card_provider = 8
    transportation_mode = 9

    CSVFormat(
        entity_id=entity_id,
        timestamp=timestamp,
        longitude=longitude,
        latitude=latitude,
        ipv4=ipv4,
        age=age,
        home_ipv4=home_ipv4,
        route_id=route_id,
        credit_card_provider=credit_card_provider,
        transportation_mode=transportation_mode
    ).build()
    ```
    ```python
    {
        "csv": {
            "entityId": 0,
            "timestamp": 1,
            "longitude": 2,
            "latitude": 3,
            "ipv4": 4,
            "age": 5,
            "home_ipv4": 6,
            "route_id": 7,
            "credit_card_provider": 8,
            "transportation_mode": 9
        }
    }
    ```
    """

    def __init__(
        self,
        entity_id: int,
        timestamp: int,
        longitude: int,
        latitude: int,
        altitude: Optional[int] = None,
        metadata_id: Optional[int] = None,
        **kwargs: int,
    ) -> None:
        """
        :entity_id: The column number to use as the `entityId`.
        :timestamp: The column number to use as the `timestamp`.
        :longitude: The column number to use as the `longitude`.
        :latitude: The column number to use as the `latitude`.
        :kwargs: The column number to use for the given keyword argument.
        """
        self.entity_id = entity_id
        self.timestamp = timestamp
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude
        self.metadata_id = metadata_id
        self.kwargs = kwargs

    def build(self) -> dict:
        """Builds a CSVFormat document from given inputs."""
        csv_format = {
            "entityId": self.entity_id,
            "timestamp": self.timestamp,
            "longitude": self.longitude,
            "latitude": self.latitude,
        }
        if self.altitude:
            csv_format.update({"altitude": self.altitude})
        if self.altitude:
            csv_format.update({"metadataId": self.metadata_id})
        csv_format.update(self.kwargs)

        return {"csv": csv_format}


class S3URLPresigner:
    """For creating presigned URLs to objects in AWS S3"""

    def __init__(self, bucket: str, region: str, profile: Optional[str]) -> None:
        """
        :param bucket: S3 bucket
        :param region: S3 bucket region
        :param profile: S3 profile to use when accessing resources.
        """
        self.bucket = bucket
        self.region = region
        self.profile = profile

        boto3.setup_default_session(profile_name=self.profile)
        config = Config(region_name=self.region, signature_version="s3v4")

        self.s3_client = boto3.client("s3", config=config)
        self.s3_resource = boto3.resource("s3", config=config)

    def find_files(self, prefix: str, suffix: str, sort: bool = True, verbose: bool = False) -> List[str]:
        """Globs for files in S3 Bucket/Prefix ending with suffix.  Will naturalsort files.
        :param prefix: S3 prefix to search in.
        :param suffix: Will search for files ending with `suffix`.  Example: suffix=".csv" will find files inding in ".csv".
        :param sort: Whether to sort the files.  Sort is done via natural sort.
        :param verbose: If `True`, will show a progress bar.
        :return: A List of files found in the S3 bucket.
        :example:  The example below will find all CSV files (files ending with ".csv") in `"s3://datasets/dataset-1"`.
        ```python
        from dfi.services.ingest import S3URLPresigner

        bucket = "datasets"
        region = "eu-west-2"
        profile= "default"

        s3_presigner = S3URLPresigner(bucket, region, profile)

        files = s3_presigner.list_files(object_key, expiration=720)
        ```
        """
        bucket = self.s3_resource.Bucket(self.bucket)

        files = []
        for s3_object in tqdm(
            bucket.objects.filter(Prefix=prefix),
            desc=f"Globbing files ending with '{suffix}' in '{self.bucket}/{prefix}'",
            disable=not verbose,
        ):
            if s3_object.key.endswith(suffix):
                files.append(s3_object.key)

        if sort:
            files = natsort.natsorted(files)
        return files

    def generate_presigned_url(
        self,
        object_key: str,
        expiration: int,
    ) -> str:
        """Creates a presigned URL for the key.

        :param object_key: S3 object key.
        :param expiration: Time in minutes for the presigned URL to remain valid.  min=1, max=720
        :return: A presigned URL.

        :example:  The example below will generate a presigned URL for `"s3://datasets/dataset-1/file-1.csv"`.
        ```python
        from dfi.services.ingest import S3URLPresigner

        bucket = "datasets"
        region = "eu-west-2"
        profile= "default"
        s3_presigner = S3URLPresigner(bucket, region, profile)

        object_key = "dataset-1/file-1.csv"
        presigned_url = s3_presigner.generate_presigned_url(object_key, expiration=720)
        ```
        """
        return self.s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": self.bucket, "Key": object_key}, ExpiresIn=expiration
        )

    def generate_presigned_urls(
        self, prefix: str, suffix: str, expiration: int, sort: bool = True, verbose: bool = False
    ) -> List[str]:
        """Creates presigned URLs matching the glob pattern in the bucket

        :param bucket: S3 bucket
        :param prefix: S3 object prefix
        :param region: S3 bucket region
        :param suffix: Suffix patten to search during glob
        :param expiration: Time in minutes for the presigned URL to remain valid.  min=1, max=720
        :param sort: Whether to sort the files.  Sort is done via natural sort.
        :param verbose: If true, will show a progress bar.
        :return: A list of presigned URLs. If error, returns None.

        :example:  The example below will generate presigned URLs for all CSV files (files ending with ".csv")
            in `s3://datasets/dataset-1`.
        ```python
        from dfi.services.ingest import S3URLPresigner

        bucket = "datasets"
        region = "eu-west-2"
        profile= "default"
        prefix = "dataset-1"

        s3_presigner = S3URLPresigner(bucket, region, profile)
        presigned_urls = s3_presigner.generate_presigned_urls(prefix, ".csv", expiration=720, sort=True, verbose=False)
        ```
        """
        files = self.find_files(prefix, suffix, sort=sort, verbose=verbose)

        presigned_urls = []
        for file in tqdm(files, desc="Presigning URLs", disable=not verbose):
            url = self.s3_client.generate_presigned_url(
                "get_object", Params={"Bucket": self.bucket, "Key": file}, ExpiresIn=expiration
            )
            presigned_urls.append(url)

        return presigned_urls


class Ingest:
    """
    Class responsible for handling data ingests.
    """

    def __init__(self, conn: Connect) -> None:
        self.conn = conn

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.conn!r})"

    def __str__(self) -> str:
        return f"""Instance of dfi.{self.__class__.__name__} composed with: {self.conn!s}"""

    def get_aws_trust_policy(self) -> dict:
        """When importing data from S3, we need to assume a role in your AWS account to be able to scan and
            download data. This requires adding a trust policy to be added to your role. You can get a copy
            of this trust policy here.

        :returns: An AWS Trust Policy for the General System API.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)
        dfi.ingest.get_aws_trust_policy()
        ```
        """
        with self.conn.api_get("v1/import/awsTrustPolicy", stream=False) as response:
            response.raise_for_status()
            return response.json()

    def put_batch(
        self,
        dataset_id: str,
        source: BatchURLFiles | BatchS3Files,
        file_format: CSVFormat,
        dry_run: bool | int = False,
    ) -> dict:
        """
        Ingest files of data to a dataset from either:
        1. a list of URLs - these can be pre-signed AWS S3 URLs, or any URL with open access to a CSV behind it
        2. an AWS S3 bucket the user has obtained access through an AWS Trust Policy

        :param dataset_id: the dataset to ingest data into.
        :param source: This can be either a batch of URLs pointing to files or an S3 bucket + prefix with files
            to be ingested.  Refer to `BatchURLFiles` or `BatchS3Files` for building the dictionary.
        :param file_format: A dictionary indicating how to map columns in a CSV file into points to be imported to
            the Data Flow Index.  Refer to `CSVFormat` for building the dictionary.
        :param dry_run: [default `False`] Set to `True` to perform a dry run that checks the first 100 rows of each file.
            Set to an integer (e.g. `1_000`) to perform a dry run that checks the first 1,000 rows of each file.
            No data will be imported into the Data Flow Index.
        :return: information about the ingest.
            - if `dry_run=True` a report of the run will be returned

        :::{hint}
        See the Ingest User Guide for full examples.
        :::
        """
        if isinstance(source, BatchS3Files):
            raise NotImplementedError(
                "'BatchS3Files` stubs are present but not yet implemented.  Instead use `BatchURLFiles`."
            )

        payload = {
            "datasetId": dataset_id,
            "source": source.build(),
            "format": file_format.build(),
        }

        # requests will seriali True / False into "True" / "False", which is not a JSON boolean
        params = {"dryRun": json.dumps(dry_run)}

        with self.conn.api_put("v1/import/batch", params=params, json=payload, stream=False) as response:
            response.raise_for_status()
            return response.json()

    def get_batch_info(
        self,
        import_batch_id: str,
    ) -> dict:
        """Retrieves information about a previously created import batch.

        :param import_batch_id: the batch id of the import.
        :returns:
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)
        dfi.ingest.get_batch_info(<import_batch_id>)
        ```
        """
        with self.conn.api_get(f"v1/import/batch/{import_batch_id}") as response:
            response.raise_for_status()
            return response.json()

    def update_batch_status(self, import_batch_id: str, status: str) -> dict:
        """Updates information about a previously created import batch.

        :::{note}
        This route can be used to abort an in-progress batch by setting the `status` field to `aborted`.
        :::

        :param import_batch_id: the batch id of the import.
        :status: the status to update the import to.  One of [`aborted`]
        :returns:
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)

        status = "aborted"
        dfi.ingest.update_batch_status(<import_batch_id>, status)
        ```
        """
        body = {"status": status}
        with self.conn.api_patch(f"v1/import/batch/{import_batch_id}", payload=body) as response:
            response.raise_for_status()
            return response.json()

    def get_batch_status(self, import_batch_id: str) -> dict:
        """
        Retrieves a chronological series of status updates about an import batch.

        :param import_batch_id: the batch id of the import.
        :return: dict with a status message and the count of entities inserted.
        :example:
        ```python
        from dfi import Client

        dfi = Client(token, url)
        dfi.ingest.get_batch_status(<import_batch_id>)
        ```
        """
        with self.conn.api_get(f"v1/import/batch/{import_batch_id}/status") as response:
            response.raise_for_status()
            return response.json()
