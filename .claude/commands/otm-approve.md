---
description: Registra la aprobación humana de un checkpoint (uso: /otm-approve CP1)
---
El humano aprueba el checkpoint indicado en $ARGUMENTS. Verifica que exista `pipeline/state/<CP>_informe.md`, escribe `aprobado: true` y la fecha de hoy en `build.json` para ese checkpoint, marca la fase como `aprobada` y desbloquea la siguiente. Commit con mensaje `pipeline: <CP> aprobado`.
