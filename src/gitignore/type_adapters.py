from datetime import datetime
from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, TypeAdapter

TemplateName: TypeAlias = str
TemplateSource: TypeAlias = str

GitignoreListTypeAdapter = TypeAdapter(
    list[TemplateName],
    config=ConfigDict(title="A type adapter for list[TemplateName]"),
)


class GitignoreFile(BaseModel):
    name: TemplateName
    source: TemplateSource


class GitignoreConfig(BaseModel):
    templates: dict[str, datetime] = {}
