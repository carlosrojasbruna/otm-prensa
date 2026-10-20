---
description: Inicia o continúa la construcción de OTM-Prensa con build-lead
---
Actúa como el agente `build-lead` definido en `.claude/agents/build-lead.md`. Lee `pipeline/state/build.json` (créalo si no existe), toma la primera tarea pendiente desbloqueada y trabaja hasta cerrar la fase actual o hasta encontrar una decisión que requiera al humano. Al terminar, resume en cinco líneas qué se hizo, qué tests pasaron y qué queda.
