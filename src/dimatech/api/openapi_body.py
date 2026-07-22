from __future__ import annotations

from copy import deepcopy
from typing import Any, get_args, get_origin

from pydantic import BaseModel


def json_content(
    model: type[BaseModel] | Any,
    *,
    example: Any | None = None,
) -> dict[str, Any]:
    """Build ``{"application/json": ...}`` from a pydantic model (or ``list[Model]``).

    Uses ``model_json_schema(mode="serialization")`` so types like ``Decimal``
    appear as JSON strings, instead of sanic-ext's ``Schema.make`` which
    introspects ``Decimal`` methods as object properties.
    """
    media: dict[str, Any] = {"schema": pydantic_schema(model)}
    if example is not None:
        media["example"] = example
    return {"application/json": media}


def json_body(
    model: type[BaseModel],
    *,
    example: dict[str, Any],
) -> dict[str, Any]:
    return json_content(model, example=example)


def pydantic_schema(model: type[BaseModel] | Any) -> dict[str, Any]:
    origin = get_origin(model)
    if origin is list:
        (item,) = get_args(model)
        return {"type": "array", "items": pydantic_schema(item)}

    if not isinstance(model, type) or not issubclass(model, BaseModel):
        raise TypeError(f"expected pydantic BaseModel or list[Model], got {model!r}")

    schema = model.model_json_schema(mode="serialization")
    return _inline_defs(schema)


def _inline_defs(schema: dict[str, Any]) -> dict[str, Any]:
    defs = schema.pop("$defs", None) or schema.pop("definitions", None) or {}
    return _expand_refs(schema, defs)


def _expand_refs(node: Any, defs: dict[str, Any]) -> Any:
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/$defs/"):
            name = ref.rsplit("/", 1)[-1]
            return _expand_refs(deepcopy(defs[name]), defs)
        return {key: _expand_refs(value, defs) for key, value in node.items()}
    if isinstance(node, list):
        return [_expand_refs(item, defs) for item in node]
    return node
