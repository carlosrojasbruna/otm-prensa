// Backend local SIMULADO de OTM-Prensa (solo desarrollo y pruebas; no es para producción).
// Reproduce la semántica de sitio/db: cuenta requerida, una valoración por docente y tarea,
// comentarios que nacen "pendiente", visibles solo si "aprobado", edición que vuelve a moderación,
// moderación solo para moderadores, retiro de datos propios. Guarda en un JSON local.
//
// Uso:  node server.mjs [--puerto 8787] [--datos ruta.json] [--static carpeta]
// Variables: OTM_LOCAL_PORT, OTM_LOCAL_DATA, OTM_LOCAL_STATIC, OTM_LOCAL_MODERADORES (correos separados por coma).
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import {
  AVISO_VERSION, ErrorOtm, exigirAviso, validarComentario, validarCredenciales, validarPerfil,
  validarPuntaje, validarTarea,
} from '../comun.js';

const HTTP = { sin_sesion: 401, sin_permiso: 403, no_existe: 404, credenciales: 401, correo_en_uso: 409 };

export function crearServidorLocal({ datos = null, estatico = null, moderadores = [] } = {}) {
  const mods = new Set(moderadores.map((m) => m.trim().toLowerCase()).filter(Boolean));
  let db = { usuarios: [], valoraciones: [], comentarios: [], perfiles: [] };
  if (datos && fs.existsSync(datos)) db = { ...db, ...JSON.parse(fs.readFileSync(datos, 'utf8')) };
  const sesiones = new Map(); // token -> userId (en memoria)
  const guardar = () => {
    if (!datos) return;
    fs.mkdirSync(path.dirname(datos), { recursive: true });
    fs.writeFileSync(datos, JSON.stringify(db, null, 2));
  };
  const ahora = () => new Date().toISOString();

  const hash = (pw, sal) => crypto.scryptSync(pw, sal, 32).toString('hex');
  const usuarioPublico = (u) => ({ id: u.id, email: u.email, esModerador: mods.has(u.email) });

  function usuarioDe(req) {
    const m = /^Bearer (.+)$/.exec(req.headers.authorization || '');
    const id = m && sesiones.get(m[1]);
    const u = id && db.usuarios.find((x) => x.id === id);
    if (!u) throw new ErrorOtm('sin_sesion', 'Inicia sesión.');
    return u;
  }
  function moderador(req) {
    const u = usuarioDe(req);
    if (!mods.has(u.email)) throw new ErrorOtm('sin_permiso', 'Solo moderadores.');
    return u;
  }

  function resumenes() {
    const out = {};
    for (const v of db.valoraciones) {
      const r = (out[v.tareaId] ??= { n: 0, suma: 0, distribucion: [0, 0, 0, 0, 0] });
      r.n += 1; r.suma += v.puntaje; r.distribucion[v.puntaje - 1] += 1;
    }
    for (const r of Object.values(out)) { r.promedio = Math.round((r.suma / r.n) * 100) / 100; delete r.suma; }
    return out;
  }
  function rotulo(userId) {
    const p = db.perfiles.find((x) => x.userId === userId);
    return p?.nivelEnsenanza ? `Docente · nivel ${p.nivelEnsenanza}` : 'Docente';
  }

  // ---------------------------------------------------------------- rutas
  async function api(req, url, cuerpo) {
    const ruta = url.pathname.slice(4); // sin "/api"
    const m = req.method;
    let r;

    if (m === 'POST' && ruta === '/auth/registro') {
      const { email, password } = validarCredenciales(cuerpo);
      if (db.usuarios.some((u) => u.email === email)) throw new ErrorOtm('correo_en_uso', 'Ese correo ya tiene cuenta.');
      const sal = crypto.randomBytes(16).toString('hex');
      const u = { id: crypto.randomUUID(), email, sal, clave: hash(password, sal), creado: ahora() };
      db.usuarios.push(u); guardar();
      const token = crypto.randomBytes(24).toString('hex'); sesiones.set(token, u.id);
      return [201, { token, usuario: usuarioPublico(u) }];
    }
    if (m === 'POST' && ruta === '/auth/login') {
      const { email, password } = validarCredenciales(cuerpo);
      const u = db.usuarios.find((x) => x.email === email);
      if (!u || !crypto.timingSafeEqual(Buffer.from(u.clave, 'hex'), Buffer.from(hash(password, u.sal), 'hex'))) {
        throw new ErrorOtm('credenciales', 'Correo o contraseña incorrectos.');
      }
      const token = crypto.randomBytes(24).toString('hex'); sesiones.set(token, u.id);
      return [200, { token, usuario: usuarioPublico(u) }];
    }
    if (m === 'POST' && ruta === '/auth/logout') {
      const t = /^Bearer (.+)$/.exec(req.headers.authorization || '')?.[1];
      if (t) sesiones.delete(t);
      return [204, null];
    }
    if (m === 'GET' && ruta === '/sesion') return [200, { usuario: usuarioPublico(usuarioDe(req)) }];

    // lectura pública
    if (m === 'GET' && ruta === '/resumenes') return [200, resumenes()];
    if ((r = /^\/tareas\/([^/]+)\/comentarios$/.exec(ruta)) && m === 'GET') {
      const id = decodeURIComponent(r[1]);
      return [200, db.comentarios
        .filter((c) => c.tareaId === id && c.estado === 'aprobado')
        .sort((a, b) => b.creado.localeCompare(a.creado))
        .map((c) => ({ id: c.id, tareaVersion: c.tareaVersion, texto: c.texto, nivelImplementado: c.nivelImplementado, rotulo: rotulo(c.userId), creado: c.creado }))];
    }

    // datos propios
    if (m === 'GET' && ruta === '/mis-datos') {
      const u = usuarioDe(req);
      const p = db.perfiles.find((x) => x.userId === u.id);
      return [200, {
        valoraciones: db.valoraciones.filter((v) => v.userId === u.id).map(({ tareaId, tareaVersion, puntaje }) => ({ tareaId, tareaVersion, puntaje })),
        comentarios: db.comentarios.filter((c) => c.userId === u.id).sort((a, b) => b.creado.localeCompare(a.creado))
          .map(({ id, tareaId, tareaVersion, texto, nivelImplementado, estado, motivo, creado }) => ({ id, tareaId, tareaVersion, texto, nivelImplementado, estado, motivo: motivo ?? null, creado })),
        perfil: p ? { nivelEnsenanza: p.nivelEnsenanza, tipoEstablecimiento: p.tipoEstablecimiento, region: p.region, aniosExperiencia: p.aniosExperiencia } : null,
      }];
    }
    if (m === 'DELETE' && ruta === '/mis-datos') {
      const u = usuarioDe(req);
      for (const k of ['valoraciones', 'comentarios']) db[k] = db[k].filter((x) => x.userId !== u.id);
      db.perfiles = db.perfiles.filter((x) => x.userId !== u.id); guardar();
      return [204, null];
    }

    // valoraciones
    if ((r = /^\/valoraciones\/([^/]+)$/.exec(ruta))) {
      const u = usuarioDe(req); const tareaId = decodeURIComponent(r[1]);
      if (m === 'PUT') {
        validarTarea(tareaId, cuerpo?.version); validarPuntaje(cuerpo?.puntaje);
        const ex = db.valoraciones.find((v) => v.userId === u.id && v.tareaId === tareaId);
        if (ex) Object.assign(ex, { puntaje: cuerpo.puntaje, tareaVersion: cuerpo.version, actualizado: ahora() });
        else db.valoraciones.push({ userId: u.id, tareaId, tareaVersion: cuerpo.version, puntaje: cuerpo.puntaje, creado: ahora(), actualizado: ahora() });
        guardar(); return [204, null];
      }
      if (m === 'DELETE') { db.valoraciones = db.valoraciones.filter((v) => !(v.userId === u.id && v.tareaId === tareaId)); guardar(); return [204, null]; }
    }

    // comentarios
    if (m === 'POST' && ruta === '/comentarios') {
      const u = usuarioDe(req);
      validarTarea(cuerpo?.tareaId, cuerpo?.version); exigirAviso(cuerpo?.avisoAceptado);
      const v = validarComentario(cuerpo);
      const c = { id: crypto.randomUUID(), userId: u.id, tareaId: cuerpo.tareaId, tareaVersion: cuerpo.version, texto: v.texto, nivelImplementado: v.nivelImplementado, estado: 'pendiente', motivo: null, avisoVersion: AVISO_VERSION, creado: ahora() };
      db.comentarios.push(c); guardar();
      return [201, { id: c.id, estado: c.estado }];
    }
    if ((r = /^\/comentarios\/([^/]+)$/.exec(ruta))) {
      const u = usuarioDe(req); const id = decodeURIComponent(r[1]);
      const c = db.comentarios.find((x) => x.id === id && x.userId === u.id);
      if (!c) throw new ErrorOtm('no_existe', 'Comentario inexistente.');
      if (m === 'PATCH') {
        const v = validarComentario(cuerpo);
        Object.assign(c, { texto: v.texto, nivelImplementado: v.nivelImplementado, estado: 'pendiente', motivo: null }); guardar();
        return [204, null];
      }
      if (m === 'DELETE') { db.comentarios = db.comentarios.filter((x) => x !== c); guardar(); return [204, null]; }
    }

    // perfil
    if (ruta === '/perfil') {
      const u = usuarioDe(req);
      if (m === 'PUT') {
        exigirAviso(cuerpo?.avisoAceptado);
        const p = validarPerfil(cuerpo);
        db.perfiles = db.perfiles.filter((x) => x.userId !== u.id);
        db.perfiles.push({ userId: u.id, ...p, avisoVersion: AVISO_VERSION, actualizado: ahora() }); guardar();
        return [204, null];
      }
      if (m === 'DELETE') { db.perfiles = db.perfiles.filter((x) => x.userId !== u.id); guardar(); return [204, null]; }
    }

    // moderación
    if (m === 'GET' && ruta === '/moderacion/pendientes') {
      moderador(req);
      return [200, db.comentarios.filter((c) => c.estado === 'pendiente').sort((a, b) => a.creado.localeCompare(b.creado))
        .map(({ id, tareaId, tareaVersion, texto, nivelImplementado, creado }) => ({ id, tareaId, tareaVersion, texto, nivelImplementado, creado }))];
    }
    if ((r = /^\/moderacion\/([^/]+)$/.exec(ruta)) && m === 'POST') {
      moderador(req);
      if (!['aprobado', 'rechazado'].includes(cuerpo?.estado)) throw new ErrorOtm('estado_invalido', 'Estado inválido.');
      const c = db.comentarios.find((x) => x.id === decodeURIComponent(r[1]));
      if (!c) throw new ErrorOtm('no_existe', 'Comentario inexistente.');
      Object.assign(c, { estado: cuerpo.estado, motivo: cuerpo.motivo ? String(cuerpo.motivo).slice(0, 500) : null }); guardar();
      return [204, null];
    }
    throw new ErrorOtm('no_existe', 'Ruta inexistente.');
  }

  // ------------------------------------------------------------- estáticos
  const TIPOS = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml', '.md': 'text/markdown; charset=utf-8', '.txt': 'text/plain; charset=utf-8', '.xml': 'application/xml', '.ico': 'image/x-icon', '.png': 'image/png', '.webmanifest': 'application/manifest+json' };
  function servirEstatico(url, res) {
    if (!estatico) { res.writeHead(404); return res.end('Sin sitio estático configurado'); }
    const raiz = path.resolve(estatico);
    let rel = decodeURIComponent(url.pathname);
    let archivo = path.resolve(raiz, '.' + rel);
    if (archivo !== raiz && !archivo.startsWith(raiz + path.sep)) { res.writeHead(403); return res.end(); }
    if (fs.existsSync(archivo) && fs.statSync(archivo).isDirectory()) archivo = path.join(archivo, 'index.html');
    if (!fs.existsSync(archivo)) { res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }); return res.end('No encontrado'); }
    res.writeHead(200, { 'Content-Type': TIPOS[path.extname(archivo)] || 'application/octet-stream' });
    fs.createReadStream(archivo).pipe(res);
  }

  const servidor = http.createServer(async (req, res) => {
    const url = new URL(req.url, 'http://localhost');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Headers', 'Authorization, Content-Type');
    res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,PATCH,DELETE,OPTIONS');
    if (req.method === 'OPTIONS') { res.writeHead(204); return res.end(); }
    if (!url.pathname.startsWith('/api/')) return servirEstatico(url, res);
    try {
      const chunks = []; for await (const c of req) chunks.push(c);
      const txt = Buffer.concat(chunks).toString('utf8');
      const cuerpo = txt ? JSON.parse(txt) : undefined;
      const [estado, salida] = await api(req, url, cuerpo);
      if (salida === null) { res.writeHead(estado); return res.end(); }
      res.writeHead(estado, { 'Content-Type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify(salida));
    } catch (e) {
      const ee = e instanceof ErrorOtm ? e : new ErrorOtm('servicio', e instanceof SyntaxError ? 'JSON inválido' : 'Error interno');
      res.writeHead(HTTP[ee.codigo] ?? (ee.codigo === 'servicio' ? 500 : 400), { 'Content-Type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify({ error: { codigo: ee.codigo, mensaje: ee.message } }));
    }
  });
  return servidor;
}

// ---- ejecución directa
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const arg = (n) => { const i = process.argv.indexOf(`--${n}`); return i > 0 ? process.argv[i + 1] : undefined; };
  const puerto = Number(arg('puerto') ?? process.env.OTM_LOCAL_PORT ?? 8787);
  const datos = arg('datos') ?? process.env.OTM_LOCAL_DATA ?? path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../.local-data/db.json');
  const estatico = arg('static') ?? process.env.OTM_LOCAL_STATIC ?? null;
  const moderadores = (process.env.OTM_LOCAL_MODERADORES ?? '').split(',');
  crearServidorLocal({ datos, estatico, moderadores }).listen(puerto, '127.0.0.1', () => {
    console.log(`Backend local simulado en http://127.0.0.1:${puerto}  (datos: ${datos}${estatico ? `, sitio: ${estatico}` : ''})`);
    console.log(moderadores.filter(Boolean).length ? `Moderadores: ${moderadores.join(', ')}` : 'Sin moderadores: define OTM_LOCAL_MODERADORES=correo@ejemplo.cl');
  });
}
