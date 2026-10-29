"""Stable, structured errors exposed through the MCP boundary."""

from __future__ import annotations


_PHASE_BY_CODE = {
    "invalid-spec": "input",
    "invalid-schema": "input",
    "unsupported-type": "input",
    "invalid-intent": "input",
    "invalid-selection": "input",
    "invalid-node": "input",
    "invalid-edge": "input",
    "dangling-edge": "input",
    "invalid-output": "input",
    "unsupported-format": "input",
    "unknown-field": "input",
    "input-limit": "input",
    "invalid-sysml-input": "input",
    "sysml-input-limit": "input",
    "compiler-missing": "compilation",
    "compiler-integrity": "compilation",
    "compiler-unavailable": "compilation",
    "compiler-timeout": "compilation",
    "compiler-launch": "compilation",
    "compiler-output-invalid": "compilation",
    "compiler-output-limit": "compilation",
    "visual-inspection": "inspection",
    "output-commit": "write",
    "output-io": "write",
    "resource-not-found": "resource",
    "unknown-tool": "dispatch",
    "internal-error": "execution",
}


class DgraphError(ValueError):
    """A tool error with a stable code and actionable context."""

    def __init__(
        self,
        code,
        message,
        *,
        phase=None,
        field=None,
        path=None,
        related=None,
        suggestion=None,
        retryable=False,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.phase = phase or _PHASE_BY_CODE.get(code, "semantic")
        self.field = field
        self.path = str(path) if path is not None else None
        self.related = list(related or [])
        self.suggestion = suggestion
        self.retryable = bool(retryable)

    def to_dict(self):
        result = {
            "ok": False,
            "code": self.code,
            "message": self.message,
            "phase": self.phase,
            "retryable": self.retryable,
        }
        if self.field is not None:
            result["field"] = self.field
        if self.path is not None:
            result["path"] = self.path
        if self.related:
            result["relatedIds"] = self.related
        if self.suggestion is not None:
            result["suggestion"] = self.suggestion
        return result
