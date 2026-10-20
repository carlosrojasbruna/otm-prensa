# GOB01 – Gobernanza del pipeline (v1.1, 2026-10-20)

v1.1: topes definitivos (35 USD/semana en construcción; 75 USD/mes en operación), regla de una tarea por noticia, `publicada` tras el merge, tarea centinela por ciclo (decisiones de CP2).

Decisiones de Carlos del 2026-10-20 incorporadas; lo que sigue marcado **[D]** no bloquea CP1 y se decide en CP2 o CP3.

## 1. Umbrales

| Regla | Valor |
|---|---|
| Filtro de modelabilidad (RUB01 corta) | ≥ 7/10 |
| Publicación de tarea (RUB01) | ≥ 20/24 y ningún criterio en 0. Verificado contra tareas-oro v0.4: publican las 8 positivas (20–24), quedan fuera población belga (16, un 0) y Clear Day (7) |
| Iteraciones diseñador ↔ evaluador | máx. 3; si no alcanza, la noticia se archiva con su diagnóstico |
| Calibración del evaluador (CP1) | kappa ≥ 0,7 contra `puntajes_v0.4` (9 tareas). **Provisional**: 5 de los 9 puntajes son de Claude; recalibrar con doble codificación humana antes de reportar |
| Corridas del simulador por tarea | 6 (SIM01 §1); 12 si CP2 lo pide |
| Escenarios en la guía | 3–4, cada uno con `id` de corrida; marcados *observado* o *a priori* |
| Tareas por noticia | 1 por ciclo |
| Tarea centinela | 1 tarea-oro al azar evaluada a ciegas por ciclo; descalibración si Clear Day > 10 o población belga > 18 |

## 2. Aprobaciones

| Punto | Quién | Qué mira |
|---|---|---|
| Revisión humana 1 (tarea) | Carlos (piloto); rotación con el equipo después **[D]** | Enunciado, recursos, nivel declarado, RUB01 con justificaciones |
| Revisión humana 2 (guía) | Carlos (piloto) | Escenarios vs. trazas, cifras vs. noticia, secciones C1–C9 |
| PR semanal | Quien revisó la guía | Aprueba el merge; `publicada` se escribe tras el merge; a las 8 semanas se evalúa auto-merge si rechazo < 10 % |

## 3. Costo y ejecución

| Regla | Valor |
|---|---|
| API | **API key de Carlos** (Anthropic Console), guardada como secret `ANTHROPIC_API_KEY` en el repo. Nunca en el código ni en los insumos |
| Tope de gasto | Construcción: 35 USD/semana. Operación: 75 USD/mes (límite en la Console) y el orquestador se detiene al 90 % del tope semanal de `pipeline/config.yaml` |
| Simulador | Corre **vía API** (no `claude -p`), para que funcione en GitHub Actions. Único cambio en `sim.py`: la función `llamar()` se reemplaza por un cliente API con el mismo contrato (system, user, model, schema). Se conserva la versión `claude -p` como opción local |
| Frecuencia | Semanal, lunes 06:00 Chile; 2–3 tareas por ciclo |
| Modelos por agente | Según `evals/resultados` (plan §5); punto de partida: Haiku 5.5 explorador/filtro/bibliotecario, Sonnet 5.5 diseñador/simulador/redactor/ilustrador, Opus 5.5 evaluador/verificador |

## 4. Repositorio y licencia

| Regla | Valor |
|---|---|
| Repo | **GitHub de Carlos**, repo `otm-prensa` (privado hasta CP3; público al publicar el sitio) |
| Token | GitHub App o token fino con `contents`, `pull_requests`, `actions`, `pages`; secret `GH_TOKEN` |
| Licencia productos | CC BY-NC-SA 4.0 |
| Licencia código | MIT |
| Noticias | Solo resumen propio (≤ 80 palabras) + enlace + cifras con localizador; hook bloquea > 25 palabras consecutivas literales |
| Versionado de tareas | Una tarea publicada no se edita: se crea v2 (nuevo commit, misma carpeta) y se conserva la v1 |
| Nombres de archivo | `nombre_vX.Y_AAAA-MM-DD` como en los insumos del proyecto |

## 5. Sitio docente y datos

| Regla | Valor |
|---|---|
| Cuenta | Requerida para valorar y comentar; lectura y descarga libres |
| Perfil docente (piloto) | nivel que enseña (P/S/U), tipo de establecimiento, región, años de experiencia — **opcional** |
| Perfil docente (versión final) | los mismos campos, **requeridos**; se agrega país **[D]** |
| Uso de datos | Aviso en el formulario: valoraciones, comentarios y perfil se usan anonimizados con fines de investigación; moderación previa; derecho a editar o retirar |
| Ética | Producciones de estudiantes: protocolo CEC UC (revisión expedita) ya existente. Sitio docente: consultar si requiere enmienda **[D, antes de CP3]** |

## 6. Reproducibilidad (para los artículos)

Cada `evaluacion.json` registra: modelo y versión de cada agente, versión de prompt, versión de rúbrica (RUB01 4.0), versión de MAR03 (1.0), versión de MED01 (1.0), diseño del simulador, fecha, costo.

## 7. Secrets que debe cargar Carlos antes de lanzar el builder

| Secret | Para qué | Cuándo |
|---|---|---|
| `ANTHROPIC_API_KEY` (Actions) / `OTM_API_KEY` (máquina local) | Scripts del pipeline y simulador. La construcción misma corre con el plan Max de Carlos en Claude Code | Antes de CP1 (el builder la usa para calibrar el evaluador) |
| `GH_TOKEN` | Bibliotecario, Actions | Antes de CP1 |
| `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` | Sitio docente | Antes de CP3 |
| Claves de medios | Ninguna necesaria con MED01 v1.0 (RSS y Google News RSS no requieren clave) | — |
