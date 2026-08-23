"""Create a sanitized AMIP diagnostic ZIP for support."""

from app.core.diagnostics import create_diagnostic_bundle


if __name__ == "__main__":
    bundle = create_diagnostic_bundle()
    print("✓ Diagnóstico concluído")
    print(f"→ Arquivo gerado: {bundle}")
    print("→ Envie este ZIP para análise. Segredos conhecidos são removidos automaticamente.")
