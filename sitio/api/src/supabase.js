// Adaptador de producción: Supabase (@supabase/supabase-js).
// Solo usa la URL y la anon key públicas; la seguridad la imponen las políticas RLS de sitio/db.
import { createClient } from '@supabase/supabase-js';
import {
  AVISO_VERSION, ErrorOtm, exigirAviso, resumenVacio, validarComentario, validarCredenciales,
  validarPerfil, validarPuntaje, validarTarea,
} from './comun.js';

function envolver(error) {
  if (!error) return;
  const msg = error.message || String(error);
  const codigo =
    error.code === '42501' ? 'sin_permiso'
    : error.code === '23505' ? 'duplicado'
    : /invalid login/i.test(msg) ? 'credenciales'
    : /already registered/i.test(msg) ? 'correo_en_uso'
    : /rate limit/i.test(msg) ? 'limite'
    : 'servicio';
  throw new ErrorOtm(codigo, msg);
}

export function crearBackendSupabase({ supabaseUrl, supabaseAnonKey }) {
  if (!supabaseUrl || !supabaseAnonKey) throw new ErrorOtm('sin_configuracion', 'Faltan PUBLIC_SUPABASE_URL / PUBLIC_SUPABASE_ANON_KEY.');
  const sb = createClient(supabaseUrl, supabaseAnonKey, { auth: { persistSession: true, autoRefreshToken: true } });

  // Sin upsert: PostgREST lo traduce a ON CONFLICT DO UPDATE SET <todas las columnas>, y 0002_rls.sql solo
  // concede UPDATE sobre las columnas editables (42501). Se actualiza la fila propia y, si no existe, se inserta.
  async function guardarPropia(tabla, clave, editables) {
    const actualizar = () => Object.entries(clave).reduce((q, [k, v]) => q.eq(k, v), sb.from(tabla).update(editables)).select(Object.keys(clave)[0]);
    let { data, error } = await actualizar();
    envolver(error);
    if (data.length) return;
    ({ error } = await sb.from(tabla).insert({ ...clave, ...editables }));
    if (error?.code === '23505') ({ error } = await actualizar());   // otra pestaña la creó entretanto
    envolver(error);
  }

  async function usuario() {
    const { data, error } = await sb.auth.getSession();
    envolver(error);
    const u = data.session?.user;
    if (!u) throw new ErrorOtm('sin_sesion', 'Inicia sesión.');
    return u;
  }

  return {
    modo: 'supabase',

    // ---- cuenta
    async registrar(cred) {
      const { email, password } = validarCredenciales(cred);
      const { data, error } = await sb.auth.signUp({ email, password });
      envolver(error);
      // Si el proyecto exige confirmar el correo, no hay sesión hasta confirmarlo.
      return { id: data.user?.id ?? null, email, requiereConfirmacion: !data.session };
    },
    async iniciarSesion(cred) {
      const { email, password } = validarCredenciales(cred);
      const { data, error } = await sb.auth.signInWithPassword({ email, password });
      envolver(error);
      return { id: data.user.id, email: data.user.email };
    },
    async cerrarSesion() {
      envolver((await sb.auth.signOut()).error);
    },
    async sesion() {
      const { data } = await sb.auth.getSession();
      const u = data.session?.user;
      if (!u) return null;
      const { data: esMod } = await sb.rpc('es_moderador');
      return { id: u.id, email: u.email, esModerador: esMod === true };
    },

    // ---- lectura pública
    async resumenes() {
      const { data, error } = await sb.rpc('resumen_valoraciones');
      envolver(error);
      const out = {};
      for (const r of data ?? []) {
        out[r.tarea_id] = {
          n: Number(r.n), promedio: r.promedio == null ? null : Number(r.promedio),
          distribucion: [r.n1, r.n2, r.n3, r.n4, r.n5].map(Number),
        };
      }
      return out;
    },
    async resumen(tareaId) {
      return (await this.resumenes())[tareaId] ?? resumenVacio();
    },
    async comentariosPublicos(tareaId) {
      const { data, error } = await sb.rpc('comentarios_aprobados', { p_tarea_id: tareaId });
      envolver(error);
      return (data ?? []).map((c) => ({
        id: c.id, tareaVersion: c.tarea_version, texto: c.texto,
        nivelImplementado: c.nivel_implementado, rotulo: c.rotulo, creado: c.creado,
      }));
    },

    // ---- datos propios
    async misDatos() {
      const u = await usuario();
      const [v, c, p] = await Promise.all([
        sb.from('valoraciones').select('tarea_id,tarea_version,puntaje,actualizado').eq('user_id', u.id),
        sb.from('comentarios').select('id,tarea_id,tarea_version,texto,nivel_implementado,estado,motivo_moderacion,creado').eq('user_id', u.id).order('creado', { ascending: false }),
        sb.from('perfiles').select('nivel_ensenanza,tipo_establecimiento,region,anios_experiencia').eq('user_id', u.id).maybeSingle(),
      ]);
      envolver(v.error); envolver(c.error); envolver(p.error);
      return {
        valoraciones: v.data.map((r) => ({ tareaId: r.tarea_id, tareaVersion: r.tarea_version, puntaje: r.puntaje })),
        comentarios: c.data.map((r) => ({
          id: r.id, tareaId: r.tarea_id, tareaVersion: r.tarea_version, texto: r.texto,
          nivelImplementado: r.nivel_implementado, estado: r.estado, motivo: r.motivo_moderacion, creado: r.creado,
        })),
        perfil: p.data && {
          nivelEnsenanza: p.data.nivel_ensenanza, tipoEstablecimiento: p.data.tipo_establecimiento,
          region: p.data.region, aniosExperiencia: p.data.anios_experiencia,
        },
      };
    },

    // ---- valorar
    async valorar({ tareaId, version, puntaje }) {
      validarTarea(tareaId, version); validarPuntaje(puntaje);
      const u = await usuario();
      await guardarPropia('valoraciones', { user_id: u.id, tarea_id: tareaId }, { tarea_version: version, puntaje });
    },
    async retirarValoracion(tareaId) {
      const u = await usuario();
      envolver((await sb.from('valoraciones').delete().eq('user_id', u.id).eq('tarea_id', tareaId)).error);
    },

    // ---- comentar
    async comentar({ tareaId, version, texto, nivelImplementado, avisoAceptado }) {
      validarTarea(tareaId, version); exigirAviso(avisoAceptado);
      const v = validarComentario({ texto, nivelImplementado });
      const u = await usuario();
      const { data, error } = await sb.from('comentarios').insert({
        user_id: u.id, tarea_id: tareaId, tarea_version: version, texto: v.texto,
        nivel_implementado: v.nivelImplementado, aviso_version: AVISO_VERSION,
      }).select('id,estado').single();
      envolver(error);
      return { id: data.id, estado: data.estado };
    },
    async editarComentario(id, { texto, nivelImplementado }) {
      const v = validarComentario({ texto, nivelImplementado });
      await usuario();
      const { error } = await sb.from('comentarios').update({ texto: v.texto, nivel_implementado: v.nivelImplementado }).eq('id', id);
      envolver(error);
    },
    async retirarComentario(id) {
      await usuario();
      envolver((await sb.from('comentarios').delete().eq('id', id)).error);
    },

    // ---- perfil (opcional en el piloto)
    async guardarPerfil(perfil, avisoAceptado) {
      exigirAviso(avisoAceptado);
      const p = validarPerfil(perfil);
      const u = await usuario();
      await guardarPropia('perfiles', { user_id: u.id }, {
        nivel_ensenanza: p.nivelEnsenanza, tipo_establecimiento: p.tipoEstablecimiento,
        region: p.region, anios_experiencia: p.aniosExperiencia, aviso_version: AVISO_VERSION,
      });
    },
    async retirarPerfil() {
      const u = await usuario();
      envolver((await sb.from('perfiles').delete().eq('user_id', u.id)).error);
    },
    async retirarTodo() {
      envolver((await sb.rpc('retirar_mis_datos')).error);
    },

    // ---- moderación (solo moderadores; lo impone la base)
    async pendientes() {
      const { data, error } = await sb.rpc('comentarios_pendientes');
      envolver(error);
      return data.map((c) => ({ id: c.id, tareaId: c.tarea_id, tareaVersion: c.tarea_version, texto: c.texto, nivelImplementado: c.nivel_implementado, creado: c.creado }));
    },
    async moderar(id, estado, motivo = null) {
      envolver((await sb.rpc('moderar_comentario', { p_id: id, p_estado: estado, p_motivo: motivo })).error);
    },
  };
}
