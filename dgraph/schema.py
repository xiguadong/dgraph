"""Machine-readable JSON Schema for the versioned ViewSpec protocol."""

from copy import deepcopy

from .viewspec import (
    ALLOWED_FORMATS,
    KNOWN_EDGE_KINDS,
    MAX_ANNOTATIONS,
    MAX_COLLECTIONS,
    MAX_EDGES,
    MAX_GROUPS,
    MAX_LABEL_LENGTH,
    MAX_NODES,
    MAX_SOURCES,
    MAX_TEXT_LENGTH,
    SCHEMA_VERSION,
)


_DOMAIN_REQUIREMENTS = {
    "qfd": "qfd",
    "gantt": "gantt",
    "fta": "faultTree",
    "c4-container": "c4Container",
    "class": "umlClass",
    "sequence": "sequenceModel",
    "n2": "n2Model",
    "dfd": "dfdModel",
    "bpmn": "bpmnModel",
    "risk-matrix": "riskMatrix",
    "dmn": "dmnModel",
    "timing": "timingModel",
    "tradespace": "tradespaceModel",
    "pert": "pertModel",
}


def _string(maximum=MAX_TEXT_LENGTH):
    return {"type": "string", "minLength": 1, "maxLength": maximum}


def _number(minimum=None):
    value = {"type": "number"}
    if minimum is not None:
        value["minimum"] = minimum
    return value


def viewspec_schema(kind):
    """Return the public schema resource for one renderable diagram type."""
    node_required = ["id", "label", "kind", "x", "y", "w", "h", "sourceId"]
    edge_required = ["source", "target", "kind"]
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"dgraph://schema/diagram-view/v1/{kind}",
        "title": f"dgraph {kind} ViewSpec",
        "description": "Common JSON structure. Runtime validation additionally enforces graph-specific semantics and geometry.",
        "x-schemaVersion": SCHEMA_VERSION,
        "x-diagramType": kind,
        "type": "object",
        "additionalProperties": False,
        "required": ["schema", "type", "intent", "selection", "outputs"],
        "properties": {
            "schema": {"const": SCHEMA_VERSION},
            "type": {"const": kind},
            "intent": {
                "type": "object",
                "additionalProperties": False,
                "required": ["question"],
                "properties": {"question": _string()},
            },
            "sources": {
                "type": "array",
                "maxItems": MAX_SOURCES,
                "items": {
                    "type": "object",
                    "required": ["kind"],
                    "properties": {"kind": {"type": "string", "enum": ["semantic", "sysml"]}},
                },
            },
            "presentation": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "width": {"type": "number", "minimum": 320, "maximum": 10000},
                    "height": {"type": "number", "minimum": 240, "maximum": 10000},
                    "theme": _string(MAX_LABEL_LENGTH),
                    "title": _string(MAX_LABEL_LENGTH),
                    "subtitle": _string(MAX_LABEL_LENGTH),
                },
            },
            "selection": {
                "type": "object",
                "additionalProperties": False,
                "required": ["nodes"],
                "properties": {
                    "layout": _string(MAX_LABEL_LENGTH),
                    "nodes": {
                        "type": "array",
                        "minItems": 0,
                        "maxItems": MAX_NODES,
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": node_required,
                            "properties": {
                                "id": _string(256),
                                "label": {"type": "string", "maxLength": MAX_LABEL_LENGTH},
                                "kind": _string(MAX_LABEL_LENGTH),
                                "x": _number(0),
                                "y": _number(0),
                                "w": _number(0),
                                "h": _number(0),
                                "sourceId": _string(256),
                                "color": _string(),
                                "compartment": _string(MAX_TEXT_LENGTH),
                                "stereotype": _string(MAX_TEXT_LENGTH),
                                "details": _string(MAX_TEXT_LENGTH),
                                "fontSize": _number(),
                                "fontWeight": _number(),
                                "authority": {"type": "string", "enum": ["fact", "view", "inferred"]},
                                "sourceKind": {"type": "string", "enum": ["semantic", "sysml"]},
                            },
                        },
                    },
                    "edges": {
                        "type": "array",
                        "maxItems": MAX_EDGES,
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": edge_required,
                            "properties": {
                                "source": _string(256),
                                "target": _string(256),
                                "kind": {"type": "string", "enum": sorted(KNOWN_EDGE_KINDS)},
                                "label": _string(MAX_LABEL_LENGTH),
                                "color": _string(),
                                "points": {
                                    "type": "array",
                                    "minItems": 2,
                                    "maxItems": 100,
                                    "items": {
                                        "type": "array",
                                        "prefixItems": [_number(), _number()],
                                        "minItems": 2,
                                        "maxItems": 2,
                                    },
                                },
                                "labelPosition": {
                                    "type": "array",
                                    "prefixItems": [_number(), _number()],
                                    "minItems": 2,
                                    "maxItems": 2,
                                },
                                "fromSide": {"type": "string", "enum": ["left", "right", "top", "bottom"]},
                                "toSide": {"type": "string", "enum": ["left", "right", "top", "bottom"]},
                                "fontSize": _number(),
                                "authority": {"type": "string", "enum": ["fact", "view", "inferred"]},
                            },
                        },
                    },
                    "groups": {"type": "array", "maxItems": MAX_GROUPS, "items": {"type": "object"}},
                    "matrices": {"type": "array", "maxItems": MAX_COLLECTIONS, "items": {"type": "object"}},
                    "charts": {"type": "array", "maxItems": MAX_COLLECTIONS, "items": {"type": "object"}},
                    "timelines": {"type": "array", "maxItems": MAX_COLLECTIONS, "items": {"type": "object"}},
                    "annotations": {"type": "array", "maxItems": MAX_ANNOTATIONS, "items": {"type": "object"}},
                    "modelElementRefs": {"type": "array", "items": _string(256)},
                    "omissions": {"type": "array", "items": {"type": "object"}},
                },
            },
            "outputs": {
                "type": "object",
                "additionalProperties": False,
                "required": ["directory"],
                "properties": {
                    "directory": {"type": "string", "pattern": "^/", "maxLength": 4096},
                    "formats": {
                        "type": "array",
                        "minItems": 1,
                        "uniqueItems": True,
                        "items": {"type": "string", "enum": sorted(ALLOWED_FORMATS)},
                    },
                },
            },
        },
    }
    domain_field = _DOMAIN_REQUIREMENTS.get(kind)
    if domain_field:
        schema["properties"]["selection"]["required"].append(domain_field)
        schema["properties"]["selection"]["properties"][domain_field] = {"type": "object"}
    schema["x-semanticInvariants"] = [
        "Node and semantic-model IDs are unique.",
        "Every edge endpoint references a selected node.",
        "Inline geometry is finite and inside the presentation canvas.",
        "Diagram-specific rules are enforced at runtime before rendering.",
    ]
    return deepcopy(schema)


__all__ = ["viewspec_schema"]
