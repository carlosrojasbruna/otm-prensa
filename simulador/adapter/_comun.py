"""Rutas y carga del módulo `sim` (repo externo del simulador) sin modificarlo."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

CONFIG = RAIZ / "pipeline" / "config.yaml"


def config_sim() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["simulador"]


def repo_simulador() -> Path:
    """Ruta del repo del simulador (`simulador.repo` de config.yaml, relativa a la raíz de este repo)."""
    return (RAIZ / config_sim()["repo"]).resolve()


def insumos_simulador() -> Path:
    """Carpeta `insumos/` del proyecto del simulador (INS02, INS08, INS09)."""
    return repo_simulador().parent / "insumos"


def simulador_disponible() -> bool:
    return (repo_simulador() / "sim.py").exists()


_SIM = None


def cargar_sim():
    """Importa `sim.py` desde la ruta de config bajo el nombre `sim_externo`.

    No escribe bytecode en el repo del simulador. Se cachea: las rutas y `llamar` se parchean en
    tiempo de ejecución (ver lanzador.parchear_sim), nunca en disco."""
    global _SIM
    if _SIM is not None:
        return _SIM
    ruta = repo_simulador() / "sim.py"
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró sim.py en {ruta} (config simulador.repo)")
    previo = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("sim_externo", ruta)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = previo
    _SIM = mod
    return mod


def fecha_hora_utc() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
