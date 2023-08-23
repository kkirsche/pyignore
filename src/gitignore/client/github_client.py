from json import JSONDecodeError
from logging import Logger, getLogger
from weakref import finalize

from httpx import Client, TimeoutException
from pydantic import ValidationError

from gitignore.type_adapters import GitignoreFile, GitignoreListTypeAdapter


def close_client(client: Client) -> None:
    if not client.is_closed:
        client.close()


class GithubClient:
    client: Client
    logger: Logger

    def __init__(self) -> None:
        self.client = Client(base_url="https://api.github.com/", http2=True)
        self.logger = getLogger(__name__)
        self.finalizer = finalize(self, close_client, self.client)

    def list_project_templates(self) -> list[str]:
        self.logger.info("retrieving gitignore templates")
        try:
            resp = self.client.get(url="/gitignore/templates")
        except TimeoutException:
            self.logger.exception("timed out retrieving gitignore templates")
            raise
        self.logger.info("retrieved with status_code=%d", resp.status_code)
        try:
            content = resp.json()
            # list of template names
            return GitignoreListTypeAdapter.validate_python(content)
        except JSONDecodeError:
            self.logger.exception("failed to parse content as JSON.")
            raise
        except ValidationError:
            self.logger.exception(
                "content was valid JSON but was not the expected shape"
            )
            raise

    def get_project_template(self, template_name: str) -> GitignoreFile:
        self.logger.info("retrieving %r gitignore template", template_name)
        try:
            resp = self.client.get(url=f"/gitignore/templates/{template_name}")
        except TimeoutException:
            self.logger.exception(
                "timed out retrieving %r gitignore template", template_name
            )
            raise
        self.logger.info("retrieved with status_code=%d", resp.status_code)
        try:
            content = resp.json()
            # return the GitIgnore template
            return GitignoreFile.model_validate(obj=content)
        except JSONDecodeError:
            self.logger.exception("failed to parse content as JSON.")
            raise
        except ValidationError:
            self.logger.exception(
                "content was valid JSON but was not the expected shape"
            )
            raise
