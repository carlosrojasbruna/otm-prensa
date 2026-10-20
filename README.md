# OTM-Prensa

Observatorio de Tareas de Modelamiento desde la Prensa: un pipeline de agentes que, cada semana, toma noticias de medios reputados, construye tareas de modelamiento matemático evaluadas con rúbrica, las somete a un simulador multiagente de estudiantes y produce una guía docente con escenarios anticipados. Todo queda versionado aquí y publicado en un sitio para docentes que valoran y comentan cada tarea.

Proyecto de Carlos Rojas Bruna, Facultad de Matemáticas, Pontificia Universidad Católica de Chile.

- Reglas y arquitectura: `CLAUDE.md`
- Plan de construcción: `plan/PLAN-CONSTRUCCION.md`
- Insumos (rúbricas, marcos, plantillas, tareas-oro, medios, gobernanza): `insumos/`
- Estado de la construcción: `pipeline/state/build.json`

Para construir: en Claude Code, dentro del repo, `/otm-build`. Para ver el estado, `/otm-status`. Para aprobar un checkpoint, `/otm-approve CP1`.

Licencias: código MIT; tareas y materiales CC BY-NC-SA 4.0 (`tareas/LICENSE.md`).
