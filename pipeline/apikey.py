"""Clave de API para los scripts del pipeline.

Orden: OTM_API_KEY (máquina local, para no interferir con la autenticación de
Claude Code por plan) y luego ANTHROPIC_API_KEY (GitHub Actions).
Uso: `from pipeline.apikey import api_key` o `python3 pipeline/apikey.py` (imprime ok/falta).
"""
import os, sys

def api_key() -> str:
    k = os.environ.get("OTM_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not k:
        raise RuntimeError("Falta OTM_API_KEY (local) o ANTHROPIC_API_KEY (Actions)")
    return k

if __name__ == "__main__":
    try:
        api_key(); print("ok")
    except RuntimeError as e:
        print("falta:", e); sys.exit(1)
