// Constantes y validaciones compartidas por el sitio y por todos los adaptadores.
// Reglas: GOB01 §5 (perfil docente opcional en el piloto; aviso de uso de datos).

/** Versión del aviso de uso de datos que se registra junto a cada dato aportado. */
export const AVISO_VERSION = 'GOB01-v1.1-s5-2026-10-20';

/** Texto del aviso (GOB01 §5). Es la única fuente: los formularios lo importan de aquí. */
export const AVISO_USO_DATOS =
  'Tus valoraciones, comentarios y datos de perfil se usan de forma anonimizada con fines de ' +
  'investigación. Los comentarios pasan por moderación antes de publicarse. ' +
  'Puedes editarlos o retirarlos cuando quieras.';

export const NIVELES = { P: 'P · primaria (10–12 años)', S: 'S · secundaria (13–18 años)', U: 'U · universitario (18–20 años)' };

export const TIPOS_ESTABLECIMIENTO = {
  municipal: 'Municipal',
  particular_subvencionado: 'Particular subvencionado',
  particular_pagado: 'Particular pagado',
  servicio_local: 'Servicio local de educación',
  universidad: 'Universidad o instituto',
  otro: 'Otro',
};

export const REGIONES = [
  'Arica y Parinacota', 'Tarapacá', 'Antofagasta', 'Atacama', 'Coquimbo', 'Valparaíso',
  'Metropolitana de Santiago', "O'Higgins", 'Maule', 'Ñuble', 'Biobío', 'La Araucanía',
  'Los Ríos', 'Los Lagos', 'Aysén', 'Magallanes y de la Antártica Chilena',
];

export const ESTADOS_COMENTARIO = ['pendiente', 'aprobado', 'rechazado'];
export const ETIQUETA_ESTADO = {
  pendiente: 'En moderación',
  aprobado: 'Publicado',
  rechazado: 'No publicado',
};

export const MAX_COMENTARIO = 2000;
const RE_TAREA_ID = /^[0-9]{4}-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*$/;

/** Error con código estable para que la interfaz decida el mensaje. */
export class ErrorOtm extends Error {
  constructor(codigo, mensaje) {
    super(mensaje || codigo);
    this.name = 'ErrorOtm';
    this.codigo = codigo;
  }
}

function exigir(cond, codigo, mensaje) {
  if (!cond) throw new ErrorOtm(codigo, mensaje);
}

export function validarTarea(tareaId, version) {
  exigir(typeof tareaId === 'string' && RE_TAREA_ID.test(tareaId), 'tarea_invalida', 'Identificador de tarea inválido.');
  exigir(Number.isInteger(version) && version >= 1, 'version_invalida', 'Versión de tarea inválida.');
}

export function validarPuntaje(puntaje) {
  exigir(Number.isInteger(puntaje) && puntaje >= 1 && puntaje <= 5, 'puntaje_invalido', 'La valoración va de 1 a 5.');
}

export function validarComentario({ texto, nivelImplementado }) {
  const t = typeof texto === 'string' ? texto.trim() : '';
  exigir(t.length >= 1, 'texto_vacio', 'Escribe un comentario.');
  exigir(t.length <= MAX_COMENTARIO, 'texto_largo', `El comentario admite hasta ${MAX_COMENTARIO} caracteres.`);
  exigir(nivelImplementado == null || nivelImplementado === '' || nivelImplementado in NIVELES, 'nivel_invalido', 'Nivel inválido.');
  return { texto: t, nivelImplementado: nivelImplementado || null };
}

/** Perfil docente del piloto: todo opcional (GOB01 §5). Devuelve el perfil normalizado. */
export function validarPerfil(p = {}) {
  const nivel = p.nivelEnsenanza || null;
  const tipo = p.tipoEstablecimiento || null;
  const region = p.region ? String(p.region).trim() : null;
  let anios = p.aniosExperiencia;
  anios = anios === '' || anios == null ? null : Number(anios);
  exigir(nivel === null || nivel in NIVELES, 'nivel_invalido', 'Nivel inválido.');
  exigir(tipo === null || tipo in TIPOS_ESTABLECIMIENTO, 'tipo_invalido', 'Tipo de establecimiento inválido.');
  exigir(region === null || (region.length >= 1 && region.length <= 80), 'region_invalida', 'Región inválida.');
  exigir(anios === null || (Number.isInteger(anios) && anios >= 0 && anios <= 60), 'anios_invalidos', 'Los años de experiencia van de 0 a 60.');
  return { nivelEnsenanza: nivel, tipoEstablecimiento: tipo, region, aniosExperiencia: anios };
}

export function exigirAviso(avisoAceptado) {
  exigir(avisoAceptado === true, 'aviso_no_aceptado', 'Debes aceptar el aviso de uso de datos.');
}

export function validarCredenciales({ email, password }) {
  exigir(typeof email === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim()), 'email_invalido', 'Correo inválido.');
  exigir(typeof password === 'string' && password.length >= 8, 'password_corta', 'La contraseña debe tener al menos 8 caracteres.');
  return { email: email.trim().toLowerCase(), password };
}

export function resumenVacio() {
  return { n: 0, promedio: null, distribucion: [0, 0, 0, 0, 0] };
}
