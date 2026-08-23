"""Tests for local support diagnostics and secret redaction."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from app.core.diagnostics import create_diagnostic_bundle
from app.core.logging import SensitiveDataRedactor


def test_sensitive_values_are_redacted(monkeypatch) -> None:
    monkeypatch.setenv("HUGGINGFACE_TOKEN", "hf_super_secret_value")
    text = "token=hf_super_secret_value Authorization: Bearer abc123 password=hunter2"

    redacted = SensitiveDataRedactor.redact(text)

    assert "hf_super_secret_value" not in redacted
    assert "hunter2" not in redacted
    assert "abc123" not in redacted
    assert "[REDACTED]" in redacted


def test_diagnostic_bundle_does_not_copy_raw_secrets(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HUGGINGFACE_TOKEN", "hf_bundle_secret")

    bundle = create_diagnostic_bundle(tmp_path)

    assert bundle.exists()
    assert bundle.suffix == ".zip"
    with zipfile.ZipFile(bundle) as archive:
        assert "diagnostic.json" in archive.namelist()
        report_text = archive.read("diagnostic.json").decode("utf-8")
        assert "hf_bundle_secret" not in report_text
        report = json.loads(report_text)
        assert report["environment"]["HUGGINGFACE_TOKEN"]["configured"] is True
        assert report["environment"]["HUGGINGFACE_TOKEN"]["value"] == "[REDACTED]"
