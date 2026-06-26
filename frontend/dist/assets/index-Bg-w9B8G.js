(function () {
  const t = document.createElement("link").relList;
  if (t && t.supports && t.supports("modulepreload")) return;
  for (const i of document.querySelectorAll('link[rel="modulepreload"]')) n(i);
  new MutationObserver((i) => {
    for (const o of i)
      if (o.type === "childList")
        for (const l of o.addedNodes)
          l.tagName === "LINK" && l.rel === "modulepreload" && n(l);
  }).observe(document, { childList: !0, subtree: !0 });
  function s(i) {
    const o = {};
    return (
      i.integrity && (o.integrity = i.integrity),
      i.referrerPolicy && (o.referrerPolicy = i.referrerPolicy),
      i.crossOrigin === "use-credentials"
        ? (o.credentials = "include")
        : i.crossOrigin === "anonymous"
          ? (o.credentials = "omit")
          : (o.credentials = "same-origin"),
      o
    );
  }
  function n(i) {
    if (i.ep) return;
    i.ep = !0;
    const o = s(i);
    fetch(i.href, o);
  }
})();
function sn(e) {
  const t = Object.create(null);
  for (const s of e.split(",")) t[s] = 1;
  return (s) => s in t;
}
const Z = {},
  vt = [],
  De = () => {},
  ai = () => !1,
  gs = (e) =>
    e.charCodeAt(0) === 111 &&
    e.charCodeAt(1) === 110 &&
    (e.charCodeAt(2) > 122 || e.charCodeAt(2) < 97),
  vs = (e) => e.startsWith("onUpdate:"),
  ge = Object.assign,
  nn = (e, t) => {
    const s = e.indexOf(t);
    s > -1 && e.splice(s, 1);
  },
  go = Object.prototype.hasOwnProperty,
  z = (e, t) => go.call(e, t),
  N = Array.isArray,
  mt = (e) => qt(e) === "[object Map]",
  ms = (e) => qt(e) === "[object Set]",
  Sn = (e) => qt(e) === "[object Date]",
  D = (e) => typeof e == "function",
  re = (e) => typeof e == "string",
  He = (e) => typeof e == "symbol",
  Y = (e) => e !== null && typeof e == "object",
  ui = (e) => (Y(e) || D(e)) && D(e.then) && D(e.catch),
  ci = Object.prototype.toString,
  qt = (e) => ci.call(e),
  vo = (e) => qt(e).slice(8, -1),
  fi = (e) => qt(e) === "[object Object]",
  on = (e) =>
    re(e) && e !== "NaN" && e[0] !== "-" && "" + parseInt(e, 10) === e,
  Et = sn(
    ",key,ref,ref_for,ref_key,onVnodeBeforeMount,onVnodeMounted,onVnodeBeforeUpdate,onVnodeUpdated,onVnodeBeforeUnmount,onVnodeUnmounted",
  ),
  ys = (e) => {
    const t = Object.create(null);
    return (s) => t[s] || (t[s] = e(s));
  },
  mo = /-\w/g,
  _e = ys((e) => e.replace(mo, (t) => t.slice(1).toUpperCase())),
  yo = /\B([A-Z])/g,
  st = ys((e) => e.replace(yo, "-$1").toLowerCase()),
  _s = ys((e) => e.charAt(0).toUpperCase() + e.slice(1)),
  Es = ys((e) => (e ? `on${_s(e)}` : "")),
  Ne = (e, t) => !Object.is(e, t),
  ns = (e, ...t) => {
    for (let s = 0; s < e.length; s++) e[s](...t);
  },
  di = (e, t, s, n = !1) => {
    Object.defineProperty(e, t, {
      configurable: !0,
      enumerable: !1,
      writable: n,
      value: s,
    });
  },
  bs = (e) => {
    const t = parseFloat(e);
    return isNaN(t) ? e : t;
  };
let Mn;
const ws = () =>
  Mn ||
  (Mn =
    typeof globalThis < "u"
      ? globalThis
      : typeof self < "u"
        ? self
        : typeof window < "u"
          ? window
          : typeof global < "u"
            ? global
            : {});
function $s(e) {
  if (N(e)) {
    const t = {};
    for (let s = 0; s < e.length; s++) {
      const n = e[s],
        i = re(n) ? $o(n) : $s(n);
      if (i) for (const o in i) t[o] = i[o];
    }
    return t;
  } else if (re(e) || Y(e)) return e;
}
const _o = /;(?![^(]*\))/g,
  bo = /:([^]+)/,
  wo = /\/\*[^]*?\*\//g;
function $o(e) {
  const t = {};
  return (
    e
      .replace(wo, "")
      .split(_o)
      .forEach((s) => {
        if (s) {
          const n = s.split(bo);
          n.length > 1 && (t[n[0].trim()] = n[1].trim());
        }
      }),
    t
  );
}
function ue(e) {
  let t = "";
  if (re(e)) t = e;
  else if (N(e))
    for (let s = 0; s < e.length; s++) {
      const n = ue(e[s]);
      n && (t += n + " ");
    }
  else if (Y(e)) for (const s in e) e[s] && (t += s + " ");
  return t.trim();
}
const xo =
    "itemscope,allowfullscreen,formnovalidate,ismap,nomodule,novalidate,readonly",
  ko = sn(xo);
function pi(e) {
  return !!e || e === "";
}
function Co(e, t) {
  if (e.length !== t.length) return !1;
  let s = !0;
  for (let n = 0; s && n < e.length; n++) s = Bt(e[n], t[n]);
  return s;
}
function Bt(e, t) {
  if (e === t) return !0;
  let s = Sn(e),
    n = Sn(t);
  if (s || n) return s && n ? e.getTime() === t.getTime() : !1;
  if (((s = He(e)), (n = He(t)), s || n)) return e === t;
  if (((s = N(e)), (n = N(t)), s || n)) return s && n ? Co(e, t) : !1;
  if (((s = Y(e)), (n = Y(t)), s || n)) {
    if (!s || !n) return !1;
    const i = Object.keys(e).length,
      o = Object.keys(t).length;
    if (i !== o) return !1;
    for (const l in e) {
      const r = e.hasOwnProperty(l),
        a = t.hasOwnProperty(l);
      if ((r && !a) || (!r && a) || !Bt(e[l], t[l])) return !1;
    }
  }
  return String(e) === String(t);
}
function So(e, t) {
  return e.findIndex((s) => Bt(s, t));
}
const hi = (e) => !!(e && e.__v_isRef === !0),
  v = (e) =>
    re(e)
      ? e
      : e == null
        ? ""
        : N(e) || (Y(e) && (e.toString === ci || !D(e.toString)))
          ? hi(e)
            ? v(e.value)
            : JSON.stringify(e, gi, 2)
          : String(e),
  gi = (e, t) =>
    hi(t)
      ? gi(e, t.value)
      : mt(t)
        ? {
            [`Map(${t.size})`]: [...t.entries()].reduce(
              (s, [n, i], o) => ((s[Rs(n, o) + " =>"] = i), s),
              {},
            ),
          }
        : ms(t)
          ? { [`Set(${t.size})`]: [...t.values()].map((s) => Rs(s)) }
          : He(t)
            ? Rs(t)
            : Y(t) && !N(t) && !fi(t)
              ? String(t)
              : t,
  Rs = (e, t = "") => {
    var s;
    return He(e) ? `Symbol(${(s = e.description) != null ? s : t})` : e;
  };
let fe;
class Mo {
  constructor(t = !1) {
    ((this.detached = t),
      (this._active = !0),
      (this._on = 0),
      (this.effects = []),
      (this.cleanups = []),
      (this._isPaused = !1),
      (this._warnOnRun = !0),
      (this.__v_skip = !0),
      !t &&
        fe &&
        (fe.active
          ? ((this.parent = fe),
            (this.index = (fe.scopes || (fe.scopes = [])).push(this) - 1))
          : ((this._active = !1), (this._warnOnRun = !1))));
  }
  get active() {
    return this._active;
  }
  pause() {
    if (this._active) {
      this._isPaused = !0;
      let t, s;
      if (this.scopes)
        for (t = 0, s = this.scopes.length; t < s; t++) this.scopes[t].pause();
      for (t = 0, s = this.effects.length; t < s; t++) this.effects[t].pause();
    }
  }
  resume() {
    if (this._active && this._isPaused) {
      this._isPaused = !1;
      let t, s;
      if (this.scopes)
        for (t = 0, s = this.scopes.length; t < s; t++) this.scopes[t].resume();
      for (t = 0, s = this.effects.length; t < s; t++) this.effects[t].resume();
    }
  }
  run(t) {
    if (this._active) {
      const s = fe;
      try {
        return ((fe = this), t());
      } finally {
        fe = s;
      }
    }
  }
  on() {
    ++this._on === 1 && ((this.prevScope = fe), (fe = this));
  }
  off() {
    if (this._on > 0 && --this._on === 0) {
      if (fe === this) fe = this.prevScope;
      else {
        let t = fe;
        for (; t; ) {
          if (t.prevScope === this) {
            t.prevScope = this.prevScope;
            break;
          }
          t = t.prevScope;
        }
      }
      this.prevScope = void 0;
    }
  }
  stop(t) {
    if (this._active) {
      this._active = !1;
      let s, n;
      for (s = 0, n = this.effects.length; s < n; s++) this.effects[s].stop();
      for (this.effects.length = 0, s = 0, n = this.cleanups.length; s < n; s++)
        this.cleanups[s]();
      if (((this.cleanups.length = 0), this.scopes)) {
        for (s = 0, n = this.scopes.length; s < n; s++) this.scopes[s].stop(!0);
        this.scopes.length = 0;
      }
      if (!this.detached && this.parent && !t) {
        const i = this.parent.scopes.pop();
        i &&
          i !== this &&
          ((this.parent.scopes[this.index] = i), (i.index = this.index));
      }
      this.parent = void 0;
    }
  }
}
function To() {
  return fe;
}
let se;
const js = new WeakSet();
class vi {
  constructor(t) {
    ((this.fn = t),
      (this.deps = void 0),
      (this.depsTail = void 0),
      (this.flags = 5),
      (this.next = void 0),
      (this.cleanup = void 0),
      (this.scheduler = void 0),
      fe && (fe.active ? fe.effects.push(this) : (this.flags &= -2)));
  }
  pause() {
    this.flags |= 64;
  }
  resume() {
    this.flags & 64 &&
      ((this.flags &= -65), js.has(this) && (js.delete(this), this.trigger()));
  }
  notify() {
    (this.flags & 2 && !(this.flags & 32)) || this.flags & 8 || yi(this);
  }
  run() {
    if (!(this.flags & 1)) return this.fn();
    ((this.flags |= 2), Tn(this), _i(this));
    const t = se,
      s = Me;
    ((se = this), (Me = !0));
    try {
      return this.fn();
    } finally {
      (bi(this), (se = t), (Me = s), (this.flags &= -3));
    }
  }
  stop() {
    if (this.flags & 1) {
      for (let t = this.deps; t; t = t.nextDep) an(t);
      ((this.deps = this.depsTail = void 0),
        Tn(this),
        this.onStop && this.onStop(),
        (this.flags &= -2));
    }
  }
  trigger() {
    this.flags & 64
      ? js.add(this)
      : this.scheduler
        ? this.scheduler()
        : this.runIfDirty();
  }
  runIfDirty() {
    qs(this) && this.run();
  }
  get dirty() {
    return qs(this);
  }
}
let mi = 0,
  Rt,
  jt;
function yi(e, t = !1) {
  if (((e.flags |= 8), t)) {
    ((e.next = jt), (jt = e));
    return;
  }
  ((e.next = Rt), (Rt = e));
}
function ln() {
  mi++;
}
function rn() {
  if (--mi > 0) return;
  if (jt) {
    let t = jt;
    for (jt = void 0; t; ) {
      const s = t.next;
      ((t.next = void 0), (t.flags &= -9), (t = s));
    }
  }
  let e;
  for (; Rt; ) {
    let t = Rt;
    for (Rt = void 0; t; ) {
      const s = t.next;
      if (((t.next = void 0), (t.flags &= -9), t.flags & 1))
        try {
          t.trigger();
        } catch (n) {
          e || (e = n);
        }
      t = s;
    }
  }
  if (e) throw e;
}
function _i(e) {
  for (let t = e.deps; t; t = t.nextDep)
    ((t.version = -1),
      (t.prevActiveLink = t.dep.activeLink),
      (t.dep.activeLink = t));
}
function bi(e) {
  let t,
    s = e.depsTail,
    n = s;
  for (; n; ) {
    const i = n.prevDep;
    (n.version === -1 ? (n === s && (s = i), an(n), Ao(n)) : (t = n),
      (n.dep.activeLink = n.prevActiveLink),
      (n.prevActiveLink = void 0),
      (n = i));
  }
  ((e.deps = t), (e.depsTail = s));
}
function qs(e) {
  for (let t = e.deps; t; t = t.nextDep)
    if (
      t.dep.version !== t.version ||
      (t.dep.computed && (wi(t.dep.computed) || t.dep.version !== t.version))
    )
      return !0;
  return !!e._dirty;
}
function wi(e) {
  if (
    (e.flags & 4 && !(e.flags & 16)) ||
    ((e.flags &= -17), e.globalVersion === Vt) ||
    ((e.globalVersion = Vt),
    !e.isSSR && e.flags & 128 && ((!e.deps && !e._dirty) || !qs(e)))
  )
    return;
  e.flags |= 2;
  const t = e.dep,
    s = se,
    n = Me;
  ((se = e), (Me = !0));
  try {
    _i(e);
    const i = e.fn(e._value);
    (t.version === 0 || Ne(i, e._value)) &&
      ((e.flags |= 128), (e._value = i), t.version++);
  } catch (i) {
    throw (t.version++, i);
  } finally {
    ((se = s), (Me = n), bi(e), (e.flags &= -3));
  }
}
function an(e, t = !1) {
  const { dep: s, prevSub: n, nextSub: i } = e;
  if (
    (n && ((n.nextSub = i), (e.prevSub = void 0)),
    i && ((i.prevSub = n), (e.nextSub = void 0)),
    s.subs === e && ((s.subs = n), !n && s.computed))
  ) {
    s.computed.flags &= -5;
    for (let o = s.computed.deps; o; o = o.nextDep) an(o, !0);
  }
  !t && !--s.sc && s.map && s.map.delete(s.key);
}
function Ao(e) {
  const { prevDep: t, nextDep: s } = e;
  (t && ((t.nextDep = s), (e.prevDep = void 0)),
    s && ((s.prevDep = t), (e.nextDep = void 0)));
}
let Me = !0;
const $i = [];
function ze() {
  ($i.push(Me), (Me = !1));
}
function Je() {
  const e = $i.pop();
  Me = e === void 0 ? !0 : e;
}
function Tn(e) {
  const { cleanup: t } = e;
  if (((e.cleanup = void 0), t)) {
    const s = se;
    se = void 0;
    try {
      t();
    } finally {
      se = s;
    }
  }
}
let Vt = 0;
class Oo {
  constructor(t, s) {
    ((this.sub = t),
      (this.dep = s),
      (this.version = s.version),
      (this.nextDep =
        this.prevDep =
        this.nextSub =
        this.prevSub =
        this.prevActiveLink =
          void 0));
  }
}
class un {
  constructor(t) {
    ((this.computed = t),
      (this.version = 0),
      (this.activeLink = void 0),
      (this.subs = void 0),
      (this.map = void 0),
      (this.key = void 0),
      (this.sc = 0),
      (this.__v_skip = !0));
  }
  track(t) {
    if (!se || !Me || se === this.computed) return;
    let s = this.activeLink;
    if (s === void 0 || s.sub !== se)
      ((s = this.activeLink = new Oo(se, this)),
        se.deps
          ? ((s.prevDep = se.depsTail),
            (se.depsTail.nextDep = s),
            (se.depsTail = s))
          : (se.deps = se.depsTail = s),
        xi(s));
    else if (s.version === -1 && ((s.version = this.version), s.nextDep)) {
      const n = s.nextDep;
      ((n.prevDep = s.prevDep),
        s.prevDep && (s.prevDep.nextDep = n),
        (s.prevDep = se.depsTail),
        (s.nextDep = void 0),
        (se.depsTail.nextDep = s),
        (se.depsTail = s),
        se.deps === s && (se.deps = n));
    }
    return s;
  }
  trigger(t) {
    (this.version++, Vt++, this.notify(t));
  }
  notify(t) {
    ln();
    try {
      for (let s = this.subs; s; s = s.prevSub)
        s.sub.notify() && s.sub.dep.notify();
    } finally {
      rn();
    }
  }
}
function xi(e) {
  if ((e.dep.sc++, e.sub.flags & 4)) {
    const t = e.dep.computed;
    if (t && !e.dep.subs) {
      t.flags |= 20;
      for (let n = t.deps; n; n = n.nextDep) xi(n);
    }
    const s = e.dep.subs;
    (s !== e && ((e.prevSub = s), s && (s.nextSub = e)), (e.dep.subs = e));
  }
}
const Bs = new WeakMap(),
  ft = Symbol(""),
  Ws = Symbol(""),
  Dt = Symbol("");
function de(e, t, s) {
  if (Me && se) {
    let n = Bs.get(e);
    n || Bs.set(e, (n = new Map()));
    let i = n.get(s);
    (i || (n.set(s, (i = new un())), (i.map = n), (i.key = s)), i.track());
  }
}
function Be(e, t, s, n, i, o) {
  const l = Bs.get(e);
  if (!l) {
    Vt++;
    return;
  }
  const r = (a) => {
    a && a.trigger();
  };
  if ((ln(), t === "clear")) l.forEach(r);
  else {
    const a = N(e),
      c = a && on(s);
    if (a && s === "length") {
      const d = Number(n);
      l.forEach((h, _) => {
        (_ === "length" || _ === Dt || (!He(_) && _ >= d)) && r(h);
      });
    } else
      switch (
        ((s !== void 0 || l.has(void 0)) && r(l.get(s)), c && r(l.get(Dt)), t)
      ) {
        case "add":
          a ? c && r(l.get("length")) : (r(l.get(ft)), mt(e) && r(l.get(Ws)));
          break;
        case "delete":
          a || (r(l.get(ft)), mt(e) && r(l.get(Ws)));
          break;
        case "set":
          mt(e) && r(l.get(ft));
          break;
      }
  }
  rn();
}
function pt(e) {
  const t = W(e);
  return t === e ? t : (de(t, "iterate", Dt), ke(e) ? t : t.map(Te));
}
function xs(e) {
  return (de((e = W(e)), "iterate", Dt), e);
}
function Fe(e, t) {
  return Ge(e) ? wt(dt(e) ? Te(t) : t) : Te(t);
}
const Io = {
  __proto__: null,
  [Symbol.iterator]() {
    return Ps(this, Symbol.iterator, (e) => Fe(this, e));
  },
  concat(...e) {
    return pt(this).concat(...e.map((t) => (N(t) ? pt(t) : t)));
  },
  entries() {
    return Ps(this, "entries", (e) => ((e[1] = Fe(this, e[1])), e));
  },
  every(e, t) {
    return Ue(this, "every", e, t, void 0, arguments);
  },
  filter(e, t) {
    return Ue(
      this,
      "filter",
      e,
      t,
      (s) => s.map((n) => Fe(this, n)),
      arguments,
    );
  },
  find(e, t) {
    return Ue(this, "find", e, t, (s) => Fe(this, s), arguments);
  },
  findIndex(e, t) {
    return Ue(this, "findIndex", e, t, void 0, arguments);
  },
  findLast(e, t) {
    return Ue(this, "findLast", e, t, (s) => Fe(this, s), arguments);
  },
  findLastIndex(e, t) {
    return Ue(this, "findLastIndex", e, t, void 0, arguments);
  },
  forEach(e, t) {
    return Ue(this, "forEach", e, t, void 0, arguments);
  },
  includes(...e) {
    return Fs(this, "includes", e);
  },
  indexOf(...e) {
    return Fs(this, "indexOf", e);
  },
  join(e) {
    return pt(this).join(e);
  },
  lastIndexOf(...e) {
    return Fs(this, "lastIndexOf", e);
  },
  map(e, t) {
    return Ue(this, "map", e, t, void 0, arguments);
  },
  pop() {
    return Tt(this, "pop");
  },
  push(...e) {
    return Tt(this, "push", e);
  },
  reduce(e, ...t) {
    return An(this, "reduce", e, t);
  },
  reduceRight(e, ...t) {
    return An(this, "reduceRight", e, t);
  },
  shift() {
    return Tt(this, "shift");
  },
  some(e, t) {
    return Ue(this, "some", e, t, void 0, arguments);
  },
  splice(...e) {
    return Tt(this, "splice", e);
  },
  toReversed() {
    return pt(this).toReversed();
  },
  toSorted(e) {
    return pt(this).toSorted(e);
  },
  toSpliced(...e) {
    return pt(this).toSpliced(...e);
  },
  unshift(...e) {
    return Tt(this, "unshift", e);
  },
  values() {
    return Ps(this, "values", (e) => Fe(this, e));
  },
};
function Ps(e, t, s) {
  const n = xs(e),
    i = n[t]();
  return (
    n !== e &&
      !ke(e) &&
      ((i._next = i.next),
      (i.next = () => {
        const o = i._next();
        return (o.done || (o.value = s(o.value)), o);
      })),
    i
  );
}
const Eo = Array.prototype;
function Ue(e, t, s, n, i, o) {
  const l = xs(e),
    r = l !== e && !ke(e),
    a = l[t];
  if (a !== Eo[t]) {
    const h = a.apply(e, o);
    return r ? Te(h) : h;
  }
  let c = s;
  l !== e &&
    (r
      ? (c = function (h, _) {
          return s.call(this, Fe(e, h), _, e);
        })
      : s.length > 2 &&
        (c = function (h, _) {
          return s.call(this, h, _, e);
        }));
  const d = a.call(l, c, n);
  return r && i ? i(d) : d;
}
function An(e, t, s, n) {
  const i = xs(e),
    o = i !== e && !ke(e);
  let l = s,
    r = !1;
  i !== e &&
    (o
      ? ((r = n.length === 0),
        (l = function (c, d, h) {
          return (
            r && ((r = !1), (c = Fe(e, c))),
            s.call(this, c, Fe(e, d), h, e)
          );
        }))
      : s.length > 3 &&
        (l = function (c, d, h) {
          return s.call(this, c, d, h, e);
        }));
  const a = i[t](l, ...n);
  return r ? Fe(e, a) : a;
}
function Fs(e, t, s) {
  const n = W(e);
  de(n, "iterate", Dt);
  const i = n[t](...s);
  return (i === -1 || i === !1) && pn(s[0])
    ? ((s[0] = W(s[0])), n[t](...s))
    : i;
}
function Tt(e, t, s = []) {
  (ze(), ln());
  const n = W(e)[t].apply(e, s);
  return (rn(), Je(), n);
}
const Ro = sn("__proto__,__v_isRef,__isVue"),
  ki = new Set(
    Object.getOwnPropertyNames(Symbol)
      .filter((e) => e !== "arguments" && e !== "caller")
      .map((e) => Symbol[e])
      .filter(He),
  );
function jo(e) {
  He(e) || (e = String(e));
  const t = W(this);
  return (de(t, "has", e), t.hasOwnProperty(e));
}
class Ci {
  constructor(t = !1, s = !1) {
    ((this._isReadonly = t), (this._isShallow = s));
  }
  get(t, s, n) {
    if (s === "__v_skip") return t.__v_skip;
    const i = this._isReadonly,
      o = this._isShallow;
    if (s === "__v_isReactive") return !i;
    if (s === "__v_isReadonly") return i;
    if (s === "__v_isShallow") return o;
    if (s === "__v_raw")
      return n === (i ? (o ? qo : Ai) : o ? Ti : Mi).get(t) ||
        Object.getPrototypeOf(t) === Object.getPrototypeOf(n)
        ? t
        : void 0;
    const l = N(t);
    if (!i) {
      let a;
      if (l && (a = Io[s])) return a;
      if (s === "hasOwnProperty") return jo;
    }
    const r = Reflect.get(t, s, he(t) ? t : n);
    if ((He(s) ? ki.has(s) : Ro(s)) || (i || de(t, "get", s), o)) return r;
    if (he(r)) {
      const a = l && on(s) ? r : r.value;
      return i && Y(a) ? Js(a) : a;
    }
    return Y(r) ? (i ? Js(r) : fn(r)) : r;
  }
}
class Si extends Ci {
  constructor(t = !1) {
    super(!1, t);
  }
  set(t, s, n, i) {
    let o = t[s];
    const l = N(t) && on(s);
    if (!this._isShallow) {
      const c = Ge(o);
      if ((!ke(n) && !Ge(n) && ((o = W(o)), (n = W(n))), !l && he(o) && !he(n)))
        return (c || (o.value = n), !0);
    }
    const r = l ? Number(s) < t.length : z(t, s),
      a = Reflect.set(t, s, n, he(t) ? t : i);
    return (
      t === W(i) && (r ? Ne(n, o) && Be(t, "set", s, n) : Be(t, "add", s, n)),
      a
    );
  }
  deleteProperty(t, s) {
    const n = z(t, s);
    t[s];
    const i = Reflect.deleteProperty(t, s);
    return (i && n && Be(t, "delete", s, void 0), i);
  }
  has(t, s) {
    const n = Reflect.has(t, s);
    return ((!He(s) || !ki.has(s)) && de(t, "has", s), n);
  }
  ownKeys(t) {
    return (de(t, "iterate", N(t) ? "length" : ft), Reflect.ownKeys(t));
  }
}
class Po extends Ci {
  constructor(t = !1) {
    super(!0, t);
  }
  set(t, s) {
    return !0;
  }
  deleteProperty(t, s) {
    return !0;
  }
}
const Fo = new Si(),
  Lo = new Po(),
  No = new Si(!0);
const zs = (e) => e,
  es = (e) => Reflect.getPrototypeOf(e);
function Vo(e, t, s) {
  return function (...n) {
    const i = this.__v_raw,
      o = W(i),
      l = mt(o),
      r = e === "entries" || (e === Symbol.iterator && l),
      a = e === "keys" && l,
      c = i[e](...n),
      d = s ? zs : t ? wt : Te;
    return (
      !t && de(o, "iterate", a ? Ws : ft),
      ge(Object.create(c), {
        next() {
          const { value: h, done: _ } = c.next();
          return _
            ? { value: h, done: _ }
            : { value: r ? [d(h[0]), d(h[1])] : d(h), done: _ };
        },
      })
    );
  };
}
function ts(e) {
  return function (...t) {
    return e === "delete" ? !1 : e === "clear" ? void 0 : this;
  };
}
function Do(e, t) {
  const s = {
    get(i) {
      const o = this.__v_raw,
        l = W(o),
        r = W(i);
      e || (Ne(i, r) && de(l, "get", i), de(l, "get", r));
      const { has: a } = es(l),
        c = t ? zs : e ? wt : Te;
      if (a.call(l, i)) return c(o.get(i));
      if (a.call(l, r)) return c(o.get(r));
      o !== l && o.get(i);
    },
    get size() {
      const i = this.__v_raw;
      return (!e && de(W(i), "iterate", ft), i.size);
    },
    has(i) {
      const o = this.__v_raw,
        l = W(o),
        r = W(i);
      return (
        e || (Ne(i, r) && de(l, "has", i), de(l, "has", r)),
        i === r ? o.has(i) : o.has(i) || o.has(r)
      );
    },
    forEach(i, o) {
      const l = this,
        r = l.__v_raw,
        a = W(r),
        c = t ? zs : e ? wt : Te;
      return (
        !e && de(a, "iterate", ft),
        r.forEach((d, h) => i.call(o, c(d), c(h), l))
      );
    },
  };
  return (
    ge(
      s,
      e
        ? {
            add: ts("add"),
            set: ts("set"),
            delete: ts("delete"),
            clear: ts("clear"),
          }
        : {
            add(i) {
              const o = W(this),
                l = es(o),
                r = W(i),
                a = !t && !ke(i) && !Ge(i) ? r : i;
              return (
                l.has.call(o, a) ||
                  (Ne(i, a) && l.has.call(o, i)) ||
                  (Ne(r, a) && l.has.call(o, r)) ||
                  (o.add(a), Be(o, "add", a, a)),
                this
              );
            },
            set(i, o) {
              !t && !ke(o) && !Ge(o) && (o = W(o));
              const l = W(this),
                { has: r, get: a } = es(l);
              let c = r.call(l, i);
              c || ((i = W(i)), (c = r.call(l, i)));
              const d = a.call(l, i);
              return (
                l.set(i, o),
                c ? Ne(o, d) && Be(l, "set", i, o) : Be(l, "add", i, o),
                this
              );
            },
            delete(i) {
              const o = W(this),
                { has: l, get: r } = es(o);
              let a = l.call(o, i);
              (a || ((i = W(i)), (a = l.call(o, i))), r && r.call(o, i));
              const c = o.delete(i);
              return (a && Be(o, "delete", i, void 0), c);
            },
            clear() {
              const i = W(this),
                o = i.size !== 0,
                l = i.clear();
              return (o && Be(i, "clear", void 0, void 0), l);
            },
          },
    ),
    ["keys", "values", "entries", Symbol.iterator].forEach((i) => {
      s[i] = Vo(i, e, t);
    }),
    s
  );
}
function cn(e, t) {
  const s = Do(e, t);
  return (n, i, o) =>
    i === "__v_isReactive"
      ? !e
      : i === "__v_isReadonly"
        ? e
        : i === "__v_raw"
          ? n
          : Reflect.get(z(s, i) && i in n ? s : n, i, o);
}
const Ho = { get: cn(!1, !1) },
  Uo = { get: cn(!1, !0) },
  Ko = { get: cn(!0, !1) };
const Mi = new WeakMap(),
  Ti = new WeakMap(),
  Ai = new WeakMap(),
  qo = new WeakMap();
function Bo(e) {
  switch (e) {
    case "Object":
    case "Array":
      return 1;
    case "Map":
    case "Set":
    case "WeakMap":
    case "WeakSet":
      return 2;
    default:
      return 0;
  }
}
function fn(e) {
  return Ge(e) ? e : dn(e, !1, Fo, Ho, Mi);
}
function Wo(e) {
  return dn(e, !1, No, Uo, Ti);
}
function Js(e) {
  return dn(e, !0, Lo, Ko, Ai);
}
function dn(e, t, s, n, i) {
  if (
    !Y(e) ||
    (e.__v_raw && !(t && e.__v_isReactive)) ||
    e.__v_skip ||
    !Object.isExtensible(e)
  )
    return e;
  const o = i.get(e);
  if (o) return o;
  const l = Bo(vo(e));
  if (l === 0) return e;
  const r = new Proxy(e, l === 2 ? n : s);
  return (i.set(e, r), r);
}
function dt(e) {
  return Ge(e) ? dt(e.__v_raw) : !!(e && e.__v_isReactive);
}
function Ge(e) {
  return !!(e && e.__v_isReadonly);
}
function ke(e) {
  return !!(e && e.__v_isShallow);
}
function pn(e) {
  return e ? !!e.__v_raw : !1;
}
function W(e) {
  const t = e && e.__v_raw;
  return t ? W(t) : e;
}
function zo(e) {
  return (
    !z(e, "__v_skip") && Object.isExtensible(e) && di(e, "__v_skip", !0),
    e
  );
}
const Te = (e) => (Y(e) ? fn(e) : e),
  wt = (e) => (Y(e) ? Js(e) : e);
function he(e) {
  return e ? e.__v_isRef === !0 : !1;
}
function ne(e) {
  return Jo(e, !1);
}
function Jo(e, t) {
  return he(e) ? e : new Go(e, t);
}
class Go {
  constructor(t, s) {
    ((this.dep = new un()),
      (this.__v_isRef = !0),
      (this.__v_isShallow = !1),
      (this._rawValue = s ? t : W(t)),
      (this._value = s ? t : Te(t)),
      (this.__v_isShallow = s));
  }
  get value() {
    return (this.dep.track(), this._value);
  }
  set value(t) {
    const s = this._rawValue,
      n = this.__v_isShallow || ke(t) || Ge(t);
    ((t = n ? t : W(t)),
      Ne(t, s) &&
        ((this._rawValue = t),
        (this._value = n ? t : Te(t)),
        this.dep.trigger()));
  }
}
function Xe(e) {
  return he(e) ? e.value : e;
}
const Yo = {
  get: (e, t, s) => (t === "__v_raw" ? e : Xe(Reflect.get(e, t, s))),
  set: (e, t, s, n) => {
    const i = e[t];
    return he(i) && !he(s) ? ((i.value = s), !0) : Reflect.set(e, t, s, n);
  },
};
function Oi(e) {
  return dt(e) ? e : new Proxy(e, Yo);
}
class Qo {
  constructor(t, s, n) {
    ((this.fn = t),
      (this.setter = s),
      (this._value = void 0),
      (this.dep = new un(this)),
      (this.__v_isRef = !0),
      (this.deps = void 0),
      (this.depsTail = void 0),
      (this.flags = 16),
      (this.globalVersion = Vt - 1),
      (this.next = void 0),
      (this.effect = this),
      (this.__v_isReadonly = !s),
      (this.isSSR = n));
  }
  notify() {
    if (((this.flags |= 16), !(this.flags & 8) && se !== this))
      return (yi(this, !0), !0);
  }
  get value() {
    const t = this.dep.track();
    return (wi(this), t && (t.version = this.dep.version), this._value);
  }
  set value(t) {
    this.setter && this.setter(t);
  }
}
function Xo(e, t, s = !1) {
  let n, i;
  return (D(e) ? (n = e) : ((n = e.get), (i = e.set)), new Qo(n, i, s));
}
const ss = {},
  rs = new WeakMap();
let at;
function Zo(e, t = !1, s = at) {
  if (s) {
    let n = rs.get(s);
    (n || rs.set(s, (n = [])), n.push(e));
  }
}
function el(e, t, s = Z) {
  const {
      immediate: n,
      deep: i,
      once: o,
      scheduler: l,
      augmentJob: r,
      call: a,
    } = s,
    c = (P) => (i ? P : ke(P) || i === !1 || i === 0 ? We(P, 1) : We(P));
  let d,
    h,
    _,
    x,
    K = !1,
    E = !1;
  if (
    (he(e)
      ? ((h = () => e.value), (K = ke(e)))
      : dt(e)
        ? ((h = () => c(e)), (K = !0))
        : N(e)
          ? ((E = !0),
            (K = e.some((P) => dt(P) || ke(P))),
            (h = () =>
              e.map((P) => {
                if (he(P)) return P.value;
                if (dt(P)) return c(P);
                if (D(P)) return a ? a(P, 2) : P();
              })))
          : D(e)
            ? t
              ? (h = a ? () => a(e, 2) : e)
              : (h = () => {
                  if (_) {
                    ze();
                    try {
                      _();
                    } finally {
                      Je();
                    }
                  }
                  const P = at;
                  at = d;
                  try {
                    return a ? a(e, 3, [x]) : e(x);
                  } finally {
                    at = P;
                  }
                })
            : (h = De),
    t && i)
  ) {
    const P = h,
      F = i === !0 ? 1 / 0 : i;
    h = () => We(P(), F);
  }
  const le = To(),
    ee = () => {
      (d.stop(), le && le.active && nn(le.effects, d));
    };
  if (o && t) {
    const P = t;
    t = (...F) => {
      const C = P(...F);
      return (ee(), C);
    };
  }
  let H = E ? new Array(e.length).fill(ss) : ss;
  const Q = (P) => {
    if (!(!(d.flags & 1) || (!d.dirty && !P)))
      if (t) {
        const F = d.run();
        if (P || i || K || (E ? F.some((C, U) => Ne(C, H[U])) : Ne(F, H))) {
          _ && _();
          const C = at;
          at = d;
          try {
            const U = [F, H === ss ? void 0 : E && H[0] === ss ? [] : H, x];
            ((H = F), a ? a(t, 3, U) : t(...U));
          } finally {
            at = C;
          }
        }
      } else d.run();
  };
  return (
    r && r(Q),
    (d = new vi(h)),
    (d.scheduler = l ? () => l(Q, !1) : Q),
    (x = (P) => Zo(P, !1, d)),
    (_ = d.onStop =
      () => {
        const P = rs.get(d);
        if (P) {
          if (a) a(P, 4);
          else for (const F of P) F();
          rs.delete(d);
        }
      }),
    t ? (n ? Q(!0) : (H = d.run())) : l ? l(Q.bind(null, !0), !0) : d.run(),
    (ee.pause = d.pause.bind(d)),
    (ee.resume = d.resume.bind(d)),
    (ee.stop = ee),
    ee
  );
}
function We(e, t = 1 / 0, s) {
  if (
    t <= 0 ||
    !Y(e) ||
    e.__v_skip ||
    ((s = s || new Map()), (s.get(e) || 0) >= t)
  )
    return e;
  if ((s.set(e, t), t--, he(e))) We(e.value, t, s);
  else if (N(e)) for (let n = 0; n < e.length; n++) We(e[n], t, s);
  else if (ms(e) || mt(e))
    e.forEach((n) => {
      We(n, t, s);
    });
  else if (fi(e)) {
    for (const n in e) We(e[n], t, s);
    for (const n of Object.getOwnPropertySymbols(e))
      Object.prototype.propertyIsEnumerable.call(e, n) && We(e[n], t, s);
  }
  return e;
}
function Wt(e, t, s, n) {
  try {
    return n ? e(...n) : e();
  } catch (i) {
    ks(i, t, s);
  }
}
function Ae(e, t, s, n) {
  if (D(e)) {
    const i = Wt(e, t, s, n);
    return (
      i &&
        ui(i) &&
        i.catch((o) => {
          ks(o, t, s);
        }),
      i
    );
  }
  if (N(e)) {
    const i = [];
    for (let o = 0; o < e.length; o++) i.push(Ae(e[o], t, s, n));
    return i;
  }
}
function ks(e, t, s, n = !0) {
  const i = t ? t.vnode : null,
    { errorHandler: o, throwUnhandledErrorInProduction: l } =
      (t && t.appContext.config) || Z;
  if (t) {
    let r = t.parent;
    const a = t.proxy,
      c = `https://vuejs.org/error-reference/#runtime-${s}`;
    for (; r; ) {
      const d = r.ec;
      if (d) {
        for (let h = 0; h < d.length; h++) if (d[h](e, a, c) === !1) return;
      }
      r = r.parent;
    }
    if (o) {
      (ze(), Wt(o, null, 10, [e, a, c]), Je());
      return;
    }
  }
  tl(e, s, i, n, l);
}
function tl(e, t, s, n = !0, i = !1) {
  if (i) throw e;
  console.error(e);
}
const ye = [];
let Pe = -1;
const yt = [];
let Ze = null,
  ht = 0;
const Ii = Promise.resolve();
let as = null;
function Ei(e) {
  const t = as || Ii;
  return e ? t.then(this ? e.bind(this) : e) : t;
}
function sl(e) {
  let t = Pe + 1,
    s = ye.length;
  for (; t < s; ) {
    const n = (t + s) >>> 1,
      i = ye[n],
      o = Ht(i);
    o < e || (o === e && i.flags & 2) ? (t = n + 1) : (s = n);
  }
  return t;
}
function hn(e) {
  if (!(e.flags & 1)) {
    const t = Ht(e),
      s = ye[ye.length - 1];
    (!s || (!(e.flags & 2) && t >= Ht(s)) ? ye.push(e) : ye.splice(sl(t), 0, e),
      (e.flags |= 1),
      Ri());
  }
}
function Ri() {
  as || (as = Ii.then(Pi));
}
function nl(e) {
  (N(e)
    ? yt.push(...e)
    : Ze && e.id === -1
      ? Ze.splice(ht + 1, 0, e)
      : e.flags & 1 || (yt.push(e), (e.flags |= 1)),
    Ri());
}
function On(e, t, s = Pe + 1) {
  for (; s < ye.length; s++) {
    const n = ye[s];
    if (n && n.flags & 2) {
      if (e && n.id !== e.uid) continue;
      (ye.splice(s, 1),
        s--,
        n.flags & 4 && (n.flags &= -2),
        n(),
        n.flags & 4 || (n.flags &= -2));
    }
  }
}
function ji(e) {
  if (yt.length) {
    const t = [...new Set(yt)].sort((s, n) => Ht(s) - Ht(n));
    if (((yt.length = 0), Ze)) {
      Ze.push(...t);
      return;
    }
    for (Ze = t, ht = 0; ht < Ze.length; ht++) {
      const s = Ze[ht];
      (s.flags & 4 && (s.flags &= -2), s.flags & 8 || s(), (s.flags &= -2));
    }
    ((Ze = null), (ht = 0));
  }
}
const Ht = (e) => (e.id == null ? (e.flags & 2 ? -1 : 1 / 0) : e.id);
function Pi(e) {
  try {
    for (Pe = 0; Pe < ye.length; Pe++) {
      const t = ye[Pe];
      t &&
        !(t.flags & 8) &&
        (t.flags & 4 && (t.flags &= -2),
        Wt(t, t.i, t.i ? 15 : 14),
        t.flags & 4 || (t.flags &= -2));
    }
  } finally {
    for (; Pe < ye.length; Pe++) {
      const t = ye[Pe];
      t && (t.flags &= -2);
    }
    ((Pe = -1),
      (ye.length = 0),
      ji(),
      (as = null),
      (ye.length || yt.length) && Pi());
  }
}
let $e = null,
  Fi = null;
function us(e) {
  const t = $e;
  return (($e = e), (Fi = (e && e.type.__scopeId) || null), t);
}
function il(e, t = $e, s) {
  if (!t || e._n) return e;
  const n = (...i) => {
    n._d && Un(-1);
    const o = us(t);
    let l;
    try {
      l = e(...i);
    } finally {
      (us(o), n._d && Un(1));
    }
    return l;
  };
  return ((n._n = !0), (n._c = !0), (n._d = !0), n);
}
function Ve(e, t) {
  if ($e === null) return e;
  const s = As($e),
    n = e.dirs || (e.dirs = []);
  for (let i = 0; i < t.length; i++) {
    let [o, l, r, a = Z] = t[i];
    o &&
      (D(o) && (o = { mounted: o, updated: o }),
      o.deep && We(l),
      n.push({
        dir: o,
        instance: s,
        value: l,
        oldValue: void 0,
        arg: r,
        modifiers: a,
      }));
  }
  return e;
}
function lt(e, t, s, n) {
  const i = e.dirs,
    o = t && t.dirs;
  for (let l = 0; l < i.length; l++) {
    const r = i[l];
    o && (r.oldValue = o[l].value);
    let a = r.dir[n];
    a && (ze(), Ae(a, s, 8, [e.el, r, e, t]), Je());
  }
}
function ol(e, t) {
  if (pe) {
    let s = pe.provides;
    const n = pe.parent && pe.parent.provides;
    (n === s && (s = pe.provides = Object.create(n)), (s[e] = t));
  }
}
function is(e, t, s = !1) {
  const n = lr();
  if (n || _t) {
    let i = _t
      ? _t._context.provides
      : n
        ? n.parent == null || n.ce
          ? n.vnode.appContext && n.vnode.appContext.provides
          : n.parent.provides
        : void 0;
    if (i && e in i) return i[e];
    if (arguments.length > 1) return s && D(t) ? t.call(n && n.proxy) : t;
  }
}
const ll = Symbol.for("v-scx"),
  rl = () => is(ll);
function Ls(e, t, s) {
  return Li(e, t, s);
}
function Li(e, t, s = Z) {
  const { immediate: n, deep: i, flush: o, once: l } = s,
    r = ge({}, s),
    a = (t && n) || (!t && o !== "post");
  let c;
  if (Kt) {
    if (o === "sync") {
      const x = rl();
      c = x.__watcherHandles || (x.__watcherHandles = []);
    } else if (!a) {
      const x = () => {};
      return ((x.stop = De), (x.resume = De), (x.pause = De), x);
    }
  }
  const d = pe;
  r.call = (x, K, E) => Ae(x, d, K, E);
  let h = !1;
  (o === "post"
    ? (r.scheduler = (x) => {
        be(x, d && d.suspense);
      })
    : o !== "sync" &&
      ((h = !0),
      (r.scheduler = (x, K) => {
        K ? x() : hn(x);
      })),
    (r.augmentJob = (x) => {
      (t && (x.flags |= 4),
        h && ((x.flags |= 2), d && ((x.id = d.uid), (x.i = d))));
    }));
  const _ = el(e, t, r);
  return (Kt && (c ? c.push(_) : a && _()), _);
}
function al(e, t, s) {
  const n = this.proxy,
    i = re(e) ? (e.includes(".") ? Ni(n, e) : () => n[e]) : e.bind(n, n);
  let o;
  D(t) ? (o = t) : ((o = t.handler), (s = t));
  const l = zt(this),
    r = Li(i, o.bind(n), s);
  return (l(), r);
}
function Ni(e, t) {
  const s = t.split(".");
  return () => {
    let n = e;
    for (let i = 0; i < s.length && n; i++) n = n[s[i]];
    return n;
  };
}
const ul = Symbol("_vte"),
  cl = (e) => e.__isTeleport,
  Ns = Symbol("_leaveCb");
function gn(e, t) {
  e.shapeFlag & 6 && e.component
    ? ((e.transition = t), gn(e.component.subTree, t))
    : e.shapeFlag & 128
      ? ((e.ssContent.transition = t.clone(e.ssContent)),
        (e.ssFallback.transition = t.clone(e.ssFallback)))
      : (e.transition = t);
}
function Vi(e) {
  e.ids = [e.ids[0] + e.ids[2]++ + "-", 0, 0];
}
function In(e, t) {
  let s;
  return !!((s = Object.getOwnPropertyDescriptor(e, t)) && !s.configurable);
}
const cs = new WeakMap();
function Pt(e, t, s, n, i = !1) {
  if (N(e)) {
    e.forEach((E, le) => Pt(E, t && (N(t) ? t[le] : t), s, n, i));
    return;
  }
  if (Ft(n) && !i) {
    n.shapeFlag & 512 &&
      n.type.__asyncResolved &&
      n.component.subTree.component &&
      Pt(e, t, s, n.component.subTree);
    return;
  }
  const o = n.shapeFlag & 4 ? As(n.component) : n.el,
    l = i ? null : o,
    { i: r, r: a } = e,
    c = t && t.r,
    d = r.refs === Z ? (r.refs = {}) : r.refs,
    h = r.setupState,
    _ = W(h),
    x = h === Z ? ai : (E) => (In(d, E) ? !1 : z(_, E)),
    K = (E, le) => !(le && In(d, le));
  if (c != null && c !== a) {
    if ((En(t), re(c))) ((d[c] = null), x(c) && (h[c] = null));
    else if (he(c)) {
      const E = t;
      (K(c, E.k) && (c.value = null), E.k && (d[E.k] = null));
    }
  }
  if (D(a)) Wt(a, r, 12, [l, d]);
  else {
    const E = re(a),
      le = he(a);
    if (E || le) {
      const ee = () => {
        if (e.f) {
          const H = E ? (x(a) ? h[a] : d[a]) : K() || !e.k ? a.value : d[e.k];
          if (i) N(H) && nn(H, o);
          else if (N(H)) H.includes(o) || H.push(o);
          else if (E) ((d[a] = [o]), x(a) && (h[a] = d[a]));
          else {
            const Q = [o];
            (K(a, e.k) && (a.value = Q), e.k && (d[e.k] = Q));
          }
        } else
          E
            ? ((d[a] = l), x(a) && (h[a] = l))
            : le && (K(a, e.k) && (a.value = l), e.k && (d[e.k] = l));
      };
      if (l) {
        const H = () => {
          (ee(), cs.delete(e));
        };
        ((H.id = -1), cs.set(e, H), be(H, s));
      } else (En(e), ee());
    }
  }
}
function En(e) {
  const t = cs.get(e);
  t && ((t.flags |= 8), cs.delete(e));
}
ws().requestIdleCallback;
ws().cancelIdleCallback;
const Ft = (e) => !!e.type.__asyncLoader,
  Di = (e) => e.type.__isKeepAlive;
function fl(e, t) {
  Hi(e, "a", t);
}
function dl(e, t) {
  Hi(e, "da", t);
}
function Hi(e, t, s = pe) {
  const n =
    e.__wdc ||
    (e.__wdc = () => {
      let i = s;
      for (; i; ) {
        if (i.isDeactivated) return;
        i = i.parent;
      }
      return e();
    });
  if ((Cs(t, n, s), s)) {
    let i = s.parent;
    for (; i && i.parent; )
      (Di(i.parent.vnode) && pl(n, t, s, i), (i = i.parent));
  }
}
function pl(e, t, s, n) {
  const i = Cs(t, e, n, !0);
  Ss(() => {
    nn(n[t], i);
  }, s);
}
function Cs(e, t, s = pe, n = !1) {
  if (s) {
    const i = s[e] || (s[e] = []),
      o =
        t.__weh ||
        (t.__weh = (...l) => {
          ze();
          const r = zt(s),
            a = Ae(t, s, e, l);
          return (r(), Je(), a);
        });
    return (n ? i.unshift(o) : i.push(o), o);
  }
}
const Ye =
    (e) =>
    (t, s = pe) => {
      (!Kt || e === "sp") && Cs(e, (...n) => t(...n), s);
    },
  hl = Ye("bm"),
  xt = Ye("m"),
  gl = Ye("bu"),
  vl = Ye("u"),
  ml = Ye("bum"),
  Ss = Ye("um"),
  yl = Ye("sp"),
  _l = Ye("rtg"),
  bl = Ye("rtc");
function wl(e, t = pe) {
  Cs("ec", e, t);
}
const $l = "components";
function xl(e, t) {
  return Cl($l, e, !0, t) || e;
}
const kl = Symbol.for("v-ndc");
function Cl(e, t, s = !0, n = !1) {
  const i = $e || pe;
  if (i) {
    const o = i.type;
    {
      const r = fr(o, !1);
      if (r && (r === t || r === _e(t) || r === _s(_e(t)))) return o;
    }
    const l = Rn(i[e] || o[e], t) || Rn(i.appContext[e], t);
    return !l && n ? o : l;
  }
}
function Rn(e, t) {
  return e && (e[t] || e[_e(t)] || e[_s(_e(t))]);
}
function oe(e, t, s, n) {
  let i;
  const o = s,
    l = N(e);
  if (l || re(e)) {
    const r = l && dt(e);
    let a = !1,
      c = !1;
    (r && ((a = !ke(e)), (c = Ge(e)), (e = xs(e))), (i = new Array(e.length)));
    for (let d = 0, h = e.length; d < h; d++)
      i[d] = t(a ? (c ? wt(Te(e[d])) : Te(e[d])) : e[d], d, void 0, o);
  } else if (typeof e == "number") {
    i = new Array(e);
    for (let r = 0; r < e; r++) i[r] = t(r + 1, r, void 0, o);
  } else if (Y(e))
    if (e[Symbol.iterator]) i = Array.from(e, (r, a) => t(r, a, void 0, o));
    else {
      const r = Object.keys(e);
      i = new Array(r.length);
      for (let a = 0, c = r.length; a < c; a++) {
        const d = r[a];
        i[a] = t(e[d], d, a, o);
      }
    }
  else i = [];
  return i;
}
const Gs = (e) => (e ? (ao(e) ? As(e) : Gs(e.parent)) : null),
  Lt = ge(Object.create(null), {
    $: (e) => e,
    $el: (e) => e.vnode.el,
    $data: (e) => e.data,
    $props: (e) => e.props,
    $attrs: (e) => e.attrs,
    $slots: (e) => e.slots,
    $refs: (e) => e.refs,
    $parent: (e) => Gs(e.parent),
    $root: (e) => Gs(e.root),
    $host: (e) => e.ce,
    $emit: (e) => e.emit,
    $options: (e) => Ki(e),
    $forceUpdate: (e) =>
      e.f ||
      (e.f = () => {
        hn(e.update);
      }),
    $nextTick: (e) => e.n || (e.n = Ei.bind(e.proxy)),
    $watch: (e) => al.bind(e),
  }),
  Vs = (e, t) => e !== Z && !e.__isScriptSetup && z(e, t),
  Sl = {
    get({ _: e }, t) {
      if (t === "__v_skip") return !0;
      const {
        ctx: s,
        setupState: n,
        data: i,
        props: o,
        accessCache: l,
        type: r,
        appContext: a,
      } = e;
      if (t[0] !== "$") {
        const _ = l[t];
        if (_ !== void 0)
          switch (_) {
            case 1:
              return n[t];
            case 2:
              return i[t];
            case 4:
              return s[t];
            case 3:
              return o[t];
          }
        else {
          if (Vs(n, t)) return ((l[t] = 1), n[t]);
          if (i !== Z && z(i, t)) return ((l[t] = 2), i[t]);
          if (z(o, t)) return ((l[t] = 3), o[t]);
          if (s !== Z && z(s, t)) return ((l[t] = 4), s[t]);
          Ys && (l[t] = 0);
        }
      }
      const c = Lt[t];
      let d, h;
      if (c) return (t === "$attrs" && de(e.attrs, "get", ""), c(e));
      if ((d = r.__cssModules) && (d = d[t])) return d;
      if (s !== Z && z(s, t)) return ((l[t] = 4), s[t]);
      if (((h = a.config.globalProperties), z(h, t))) return h[t];
    },
    set({ _: e }, t, s) {
      const { data: n, setupState: i, ctx: o } = e;
      return Vs(i, t)
        ? ((i[t] = s), !0)
        : n !== Z && z(n, t)
          ? ((n[t] = s), !0)
          : z(e.props, t) || (t[0] === "$" && t.slice(1) in e)
            ? !1
            : ((o[t] = s), !0);
    },
    has(
      {
        _: {
          data: e,
          setupState: t,
          accessCache: s,
          ctx: n,
          appContext: i,
          props: o,
          type: l,
        },
      },
      r,
    ) {
      let a;
      return !!(
        s[r] ||
        (e !== Z && r[0] !== "$" && z(e, r)) ||
        Vs(t, r) ||
        z(o, r) ||
        z(n, r) ||
        z(Lt, r) ||
        z(i.config.globalProperties, r) ||
        ((a = l.__cssModules) && a[r])
      );
    },
    defineProperty(e, t, s) {
      return (
        s.get != null
          ? (e._.accessCache[t] = 0)
          : z(s, "value") && this.set(e, t, s.value, null),
        Reflect.defineProperty(e, t, s)
      );
    },
  };
function jn(e) {
  return N(e) ? e.reduce((t, s) => ((t[s] = null), t), {}) : e;
}
let Ys = !0;
function Ml(e) {
  const t = Ki(e),
    s = e.proxy,
    n = e.ctx;
  ((Ys = !1), t.beforeCreate && Pn(t.beforeCreate, e, "bc"));
  const {
    data: i,
    computed: o,
    methods: l,
    watch: r,
    provide: a,
    inject: c,
    created: d,
    beforeMount: h,
    mounted: _,
    beforeUpdate: x,
    updated: K,
    activated: E,
    deactivated: le,
    beforeDestroy: ee,
    beforeUnmount: H,
    destroyed: Q,
    unmounted: P,
    render: F,
    renderTracked: C,
    renderTriggered: U,
    errorCaptured: Ce,
    serverPrefetch: Gt,
    expose: nt,
    inheritAttrs: kt,
    components: Yt,
    directives: Qt,
    filters: Os,
  } = t;
  if ((c && Tl(c, n, null), l))
    for (const ie in l) {
      const te = l[ie];
      D(te) && (n[ie] = te.bind(s));
    }
  if (i) {
    const ie = i.call(s, s);
    Y(ie) && (e.data = fn(ie));
  }
  if (((Ys = !0), o))
    for (const ie in o) {
      const te = o[ie],
        it = D(te) ? te.bind(s, s) : D(te.get) ? te.get.bind(s, s) : De,
        Xt = !D(te) && D(te.set) ? te.set.bind(s) : De,
        ot = q({ get: it, set: Xt });
      Object.defineProperty(n, ie, {
        enumerable: !0,
        configurable: !0,
        get: () => ot.value,
        set: (Oe) => (ot.value = Oe),
      });
    }
  if (r) for (const ie in r) Ui(r[ie], n, s, ie);
  if (a) {
    const ie = D(a) ? a.call(s) : a;
    Reflect.ownKeys(ie).forEach((te) => {
      ol(te, ie[te]);
    });
  }
  d && Pn(d, e, "c");
  function ve(ie, te) {
    N(te) ? te.forEach((it) => ie(it.bind(s))) : te && ie(te.bind(s));
  }
  if (
    (ve(hl, h),
    ve(xt, _),
    ve(gl, x),
    ve(vl, K),
    ve(fl, E),
    ve(dl, le),
    ve(wl, Ce),
    ve(bl, C),
    ve(_l, U),
    ve(ml, H),
    ve(Ss, P),
    ve(yl, Gt),
    N(nt))
  )
    if (nt.length) {
      const ie = e.exposed || (e.exposed = {});
      nt.forEach((te) => {
        Object.defineProperty(ie, te, {
          get: () => s[te],
          set: (it) => (s[te] = it),
          enumerable: !0,
        });
      });
    } else e.exposed || (e.exposed = {});
  (F && e.render === De && (e.render = F),
    kt != null && (e.inheritAttrs = kt),
    Yt && (e.components = Yt),
    Qt && (e.directives = Qt),
    Gt && Vi(e));
}
function Tl(e, t, s = De) {
  N(e) && (e = Qs(e));
  for (const n in e) {
    const i = e[n];
    let o;
    (Y(i)
      ? "default" in i
        ? (o = is(i.from || n, i.default, !0))
        : (o = is(i.from || n))
      : (o = is(i)),
      he(o)
        ? Object.defineProperty(t, n, {
            enumerable: !0,
            configurable: !0,
            get: () => o.value,
            set: (l) => (o.value = l),
          })
        : (t[n] = o));
  }
}
function Pn(e, t, s) {
  Ae(N(e) ? e.map((n) => n.bind(t.proxy)) : e.bind(t.proxy), t, s);
}
function Ui(e, t, s, n) {
  let i = n.includes(".") ? Ni(s, n) : () => s[n];
  if (re(e)) {
    const o = t[e];
    D(o) && Ls(i, o);
  } else if (D(e)) Ls(i, e.bind(s));
  else if (Y(e))
    if (N(e)) e.forEach((o) => Ui(o, t, s, n));
    else {
      const o = D(e.handler) ? e.handler.bind(s) : t[e.handler];
      D(o) && Ls(i, o, e);
    }
}
function Ki(e) {
  const t = e.type,
    { mixins: s, extends: n } = t,
    {
      mixins: i,
      optionsCache: o,
      config: { optionMergeStrategies: l },
    } = e.appContext,
    r = o.get(t);
  let a;
  return (
    r
      ? (a = r)
      : !i.length && !s && !n
        ? (a = t)
        : ((a = {}),
          i.length && i.forEach((c) => fs(a, c, l, !0)),
          fs(a, t, l)),
    Y(t) && o.set(t, a),
    a
  );
}
function fs(e, t, s, n = !1) {
  const { mixins: i, extends: o } = t;
  (o && fs(e, o, s, !0), i && i.forEach((l) => fs(e, l, s, !0)));
  for (const l in t)
    if (!(n && l === "expose")) {
      const r = Al[l] || (s && s[l]);
      e[l] = r ? r(e[l], t[l]) : t[l];
    }
  return e;
}
const Al = {
  data: Fn,
  props: Ln,
  emits: Ln,
  methods: Ot,
  computed: Ot,
  beforeCreate: me,
  created: me,
  beforeMount: me,
  mounted: me,
  beforeUpdate: me,
  updated: me,
  beforeDestroy: me,
  beforeUnmount: me,
  destroyed: me,
  unmounted: me,
  activated: me,
  deactivated: me,
  errorCaptured: me,
  serverPrefetch: me,
  components: Ot,
  directives: Ot,
  watch: Il,
  provide: Fn,
  inject: Ol,
};
function Fn(e, t) {
  return t
    ? e
      ? function () {
          return ge(
            D(e) ? e.call(this, this) : e,
            D(t) ? t.call(this, this) : t,
          );
        }
      : t
    : e;
}
function Ol(e, t) {
  return Ot(Qs(e), Qs(t));
}
function Qs(e) {
  if (N(e)) {
    const t = {};
    for (let s = 0; s < e.length; s++) t[e[s]] = e[s];
    return t;
  }
  return e;
}
function me(e, t) {
  return e ? [...new Set([].concat(e, t))] : t;
}
function Ot(e, t) {
  return e ? ge(Object.create(null), e, t) : t;
}
function Ln(e, t) {
  return e
    ? N(e) && N(t)
      ? [...new Set([...e, ...t])]
      : ge(Object.create(null), jn(e), jn(t ?? {}))
    : t;
}
function Il(e, t) {
  if (!e) return t;
  if (!t) return e;
  const s = ge(Object.create(null), e);
  for (const n in t) s[n] = me(e[n], t[n]);
  return s;
}
function qi() {
  return {
    app: null,
    config: {
      isNativeTag: ai,
      performance: !1,
      globalProperties: {},
      optionMergeStrategies: {},
      errorHandler: void 0,
      warnHandler: void 0,
      compilerOptions: {},
    },
    mixins: [],
    components: {},
    directives: {},
    provides: Object.create(null),
    optionsCache: new WeakMap(),
    propsCache: new WeakMap(),
    emitsCache: new WeakMap(),
  };
}
let El = 0;
function Rl(e, t) {
  return function (n, i = null) {
    (D(n) || (n = ge({}, n)), i != null && !Y(i) && (i = null));
    const o = qi(),
      l = new WeakSet(),
      r = [];
    let a = !1;
    const c = (o.app = {
      _uid: El++,
      _component: n,
      _props: i,
      _container: null,
      _context: o,
      _instance: null,
      version: pr,
      get config() {
        return o.config;
      },
      set config(d) {},
      use(d, ...h) {
        return (
          l.has(d) ||
            (d && D(d.install)
              ? (l.add(d), d.install(c, ...h))
              : D(d) && (l.add(d), d(c, ...h))),
          c
        );
      },
      mixin(d) {
        return (o.mixins.includes(d) || o.mixins.push(d), c);
      },
      component(d, h) {
        return h ? ((o.components[d] = h), c) : o.components[d];
      },
      directive(d, h) {
        return h ? ((o.directives[d] = h), c) : o.directives[d];
      },
      mount(d, h, _) {
        if (!a) {
          const x = c._ceVNode || J(n, i);
          return (
            (x.appContext = o),
            _ === !0 ? (_ = "svg") : _ === !1 && (_ = void 0),
            e(x, d, _),
            (a = !0),
            (c._container = d),
            (d.__vue_app__ = c),
            As(x.component)
          );
        }
      },
      onUnmount(d) {
        r.push(d);
      },
      unmount() {
        a &&
          (Ae(r, c._instance, 16),
          e(null, c._container),
          delete c._container.__vue_app__);
      },
      provide(d, h) {
        return ((o.provides[d] = h), c);
      },
      runWithContext(d) {
        const h = _t;
        _t = c;
        try {
          return d();
        } finally {
          _t = h;
        }
      },
    });
    return c;
  };
}
let _t = null;
const jl = (e, t) =>
  t === "modelValue" || t === "model-value"
    ? e.modelModifiers
    : e[`${t}Modifiers`] || e[`${_e(t)}Modifiers`] || e[`${st(t)}Modifiers`];
function Pl(e, t, ...s) {
  if (e.isUnmounted) return;
  const n = e.vnode.props || Z;
  let i = s;
  const o = t.startsWith("update:"),
    l = o && jl(n, t.slice(7));
  l &&
    (l.trim && (i = s.map((d) => (re(d) ? d.trim() : d))),
    l.number && (i = s.map(bs)));
  let r,
    a = n[(r = Es(t))] || n[(r = Es(_e(t)))];
  (!a && o && (a = n[(r = Es(st(t)))]), a && Ae(a, e, 6, i));
  const c = n[r + "Once"];
  if (c) {
    if (!e.emitted) e.emitted = {};
    else if (e.emitted[r]) return;
    ((e.emitted[r] = !0), Ae(c, e, 6, i));
  }
}
const Fl = new WeakMap();
function Bi(e, t, s = !1) {
  const n = s ? Fl : t.emitsCache,
    i = n.get(e);
  if (i !== void 0) return i;
  const o = e.emits;
  let l = {},
    r = !1;
  if (!D(e)) {
    const a = (c) => {
      const d = Bi(c, t, !0);
      d && ((r = !0), ge(l, d));
    };
    (!s && t.mixins.length && t.mixins.forEach(a),
      e.extends && a(e.extends),
      e.mixins && e.mixins.forEach(a));
  }
  return !o && !r
    ? (Y(e) && n.set(e, null), null)
    : (N(o) ? o.forEach((a) => (l[a] = null)) : ge(l, o),
      Y(e) && n.set(e, l),
      l);
}
function Ms(e, t) {
  return !e || !gs(t)
    ? !1
    : ((t = t.slice(2).replace(/Once$/, "")),
      z(e, t[0].toLowerCase() + t.slice(1)) || z(e, st(t)) || z(e, t));
}
function Nn(e) {
  const {
      type: t,
      vnode: s,
      proxy: n,
      withProxy: i,
      propsOptions: [o],
      slots: l,
      attrs: r,
      emit: a,
      render: c,
      renderCache: d,
      props: h,
      data: _,
      setupState: x,
      ctx: K,
      inheritAttrs: E,
    } = e,
    le = us(e);
  let ee, H;
  try {
    if (s.shapeFlag & 4) {
      const P = i || n,
        F = P;
      ((ee = Le(c.call(F, P, d, h, x, _, K))), (H = r));
    } else {
      const P = t;
      ((ee = Le(
        P.length > 1 ? P(h, { attrs: r, slots: l, emit: a }) : P(h, null),
      )),
        (H = t.props ? r : Ll(r)));
    }
  } catch (P) {
    ((Nt.length = 0), ks(P, e, 1), (ee = J(tt)));
  }
  let Q = ee;
  if (H && E !== !1) {
    const P = Object.keys(H),
      { shapeFlag: F } = Q;
    P.length &&
      F & 7 &&
      (o && P.some(vs) && (H = Nl(H, o)), (Q = $t(Q, H, !1, !0)));
  }
  return (
    s.dirs &&
      ((Q = $t(Q, null, !1, !0)),
      (Q.dirs = Q.dirs ? Q.dirs.concat(s.dirs) : s.dirs)),
    s.transition && gn(Q, s.transition),
    (ee = Q),
    us(le),
    ee
  );
}
const Ll = (e) => {
    let t;
    for (const s in e)
      (s === "class" || s === "style" || gs(s)) && ((t || (t = {}))[s] = e[s]);
    return t;
  },
  Nl = (e, t) => {
    const s = {};
    for (const n in e) (!vs(n) || !(n.slice(9) in t)) && (s[n] = e[n]);
    return s;
  };
function Vl(e, t, s) {
  const { props: n, children: i, component: o } = e,
    { props: l, children: r, patchFlag: a } = t,
    c = o.emitsOptions;
  if (t.dirs || t.transition) return !0;
  if (s && a >= 0) {
    if (a & 1024) return !0;
    if (a & 16) return n ? Vn(n, l, c) : !!l;
    if (a & 8) {
      const d = t.dynamicProps;
      for (let h = 0; h < d.length; h++) {
        const _ = d[h];
        if (Wi(l, n, _) && !Ms(c, _)) return !0;
      }
    }
  } else
    return (i || r) && (!r || !r.$stable)
      ? !0
      : n === l
        ? !1
        : n
          ? l
            ? Vn(n, l, c)
            : !0
          : !!l;
  return !1;
}
function Vn(e, t, s) {
  const n = Object.keys(t);
  if (n.length !== Object.keys(e).length) return !0;
  for (let i = 0; i < n.length; i++) {
    const o = n[i];
    if (Wi(t, e, o) && !Ms(s, o)) return !0;
  }
  return !1;
}
function Wi(e, t, s) {
  const n = e[s],
    i = t[s];
  return s === "style" && Y(n) && Y(i) ? !Bt(n, i) : n !== i;
}
function Dl({ vnode: e, parent: t, suspense: s }, n) {
  for (; t; ) {
    const i = t.subTree;
    if (
      (i.suspense &&
        i.suspense.activeBranch === e &&
        ((i.suspense.vnode.el = i.el = n), (e = i)),
      i === e)
    )
      (((e = t.vnode).el = n), (t = t.parent));
    else break;
  }
  s && s.activeBranch === e && (s.vnode.el = n);
}
const zi = {},
  Ji = () => Object.create(zi),
  Gi = (e) => Object.getPrototypeOf(e) === zi;
function Hl(e, t, s, n = !1) {
  const i = {},
    o = Ji();
  ((e.propsDefaults = Object.create(null)), Yi(e, t, i, o));
  for (const l in e.propsOptions[0]) l in i || (i[l] = void 0);
  (s ? (e.props = n ? i : Wo(i)) : e.type.props ? (e.props = i) : (e.props = o),
    (e.attrs = o));
}
function Ul(e, t, s, n) {
  const {
      props: i,
      attrs: o,
      vnode: { patchFlag: l },
    } = e,
    r = W(i),
    [a] = e.propsOptions;
  let c = !1;
  if ((n || l > 0) && !(l & 16)) {
    if (l & 8) {
      const d = e.vnode.dynamicProps;
      for (let h = 0; h < d.length; h++) {
        let _ = d[h];
        if (Ms(e.emitsOptions, _)) continue;
        const x = t[_];
        if (a)
          if (z(o, _)) x !== o[_] && ((o[_] = x), (c = !0));
          else {
            const K = _e(_);
            i[K] = Xs(a, r, K, x, e, !1);
          }
        else x !== o[_] && ((o[_] = x), (c = !0));
      }
    }
  } else {
    Yi(e, t, i, o) && (c = !0);
    let d;
    for (const h in r)
      (!t || (!z(t, h) && ((d = st(h)) === h || !z(t, d)))) &&
        (a
          ? s &&
            (s[h] !== void 0 || s[d] !== void 0) &&
            (i[h] = Xs(a, r, h, void 0, e, !0))
          : delete i[h]);
    if (o !== r) for (const h in o) (!t || !z(t, h)) && (delete o[h], (c = !0));
  }
  c && Be(e.attrs, "set", "");
}
function Yi(e, t, s, n) {
  const [i, o] = e.propsOptions;
  let l = !1,
    r;
  if (t)
    for (let a in t) {
      if (Et(a)) continue;
      const c = t[a];
      let d;
      i && z(i, (d = _e(a)))
        ? !o || !o.includes(d)
          ? (s[d] = c)
          : ((r || (r = {}))[d] = c)
        : Ms(e.emitsOptions, a) ||
          ((!(a in n) || c !== n[a]) && ((n[a] = c), (l = !0)));
    }
  if (o) {
    const a = W(s),
      c = r || Z;
    for (let d = 0; d < o.length; d++) {
      const h = o[d];
      s[h] = Xs(i, a, h, c[h], e, !z(c, h));
    }
  }
  return l;
}
function Xs(e, t, s, n, i, o) {
  const l = e[s];
  if (l != null) {
    const r = z(l, "default");
    if (r && n === void 0) {
      const a = l.default;
      if (l.type !== Function && !l.skipFactory && D(a)) {
        const { propsDefaults: c } = i;
        if (s in c) n = c[s];
        else {
          const d = zt(i);
          ((n = c[s] = a.call(null, t)), d());
        }
      } else n = a;
      i.ce && i.ce._setProp(s, n);
    }
    l[0] &&
      (o && !r ? (n = !1) : l[1] && (n === "" || n === st(s)) && (n = !0));
  }
  return n;
}
const Kl = new WeakMap();
function Qi(e, t, s = !1) {
  const n = s ? Kl : t.propsCache,
    i = n.get(e);
  if (i) return i;
  const o = e.props,
    l = {},
    r = [];
  let a = !1;
  if (!D(e)) {
    const d = (h) => {
      a = !0;
      const [_, x] = Qi(h, t, !0);
      (ge(l, _), x && r.push(...x));
    };
    (!s && t.mixins.length && t.mixins.forEach(d),
      e.extends && d(e.extends),
      e.mixins && e.mixins.forEach(d));
  }
  if (!o && !a) return (Y(e) && n.set(e, vt), vt);
  if (N(o))
    for (let d = 0; d < o.length; d++) {
      const h = _e(o[d]);
      Dn(h) && (l[h] = Z);
    }
  else if (o)
    for (const d in o) {
      const h = _e(d);
      if (Dn(h)) {
        const _ = o[d],
          x = (l[h] = N(_) || D(_) ? { type: _ } : ge({}, _)),
          K = x.type;
        let E = !1,
          le = !0;
        if (N(K))
          for (let ee = 0; ee < K.length; ++ee) {
            const H = K[ee],
              Q = D(H) && H.name;
            if (Q === "Boolean") {
              E = !0;
              break;
            } else Q === "String" && (le = !1);
          }
        else E = D(K) && K.name === "Boolean";
        ((x[0] = E), (x[1] = le), (E || z(x, "default")) && r.push(h));
      }
    }
  const c = [l, r];
  return (Y(e) && n.set(e, c), c);
}
function Dn(e) {
  return e[0] !== "$" && !Et(e);
}
const vn = (e) => e === "_" || e === "_ctx" || e === "$stable",
  mn = (e) => (N(e) ? e.map(Le) : [Le(e)]),
  ql = (e, t, s) => {
    if (t._n) return t;
    const n = il((...i) => mn(t(...i)), s);
    return ((n._c = !1), n);
  },
  Xi = (e, t, s) => {
    const n = e._ctx;
    for (const i in e) {
      if (vn(i)) continue;
      const o = e[i];
      if (D(o)) t[i] = ql(i, o, n);
      else if (o != null) {
        const l = mn(o);
        t[i] = () => l;
      }
    }
  },
  Zi = (e, t) => {
    const s = mn(t);
    e.slots.default = () => s;
  },
  eo = (e, t, s) => {
    for (const n in t) (s || !vn(n)) && (e[n] = t[n]);
  },
  Bl = (e, t, s) => {
    const n = (e.slots = Ji());
    if (e.vnode.shapeFlag & 32) {
      const i = t._;
      i ? (eo(n, t, s), s && di(n, "_", i, !0)) : Xi(t, n);
    } else t && Zi(e, t);
  },
  Wl = (e, t, s) => {
    const { vnode: n, slots: i } = e;
    let o = !0,
      l = Z;
    if (n.shapeFlag & 32) {
      const r = t._;
      (r
        ? s && r === 1
          ? (o = !1)
          : eo(i, t, s)
        : ((o = !t.$stable), Xi(t, i)),
        (l = t));
    } else t && (Zi(e, t), (l = { default: 1 }));
    if (o) for (const r in i) !vn(r) && l[r] == null && delete i[r];
  },
  be = Ql;
function zl(e) {
  return Jl(e);
}
function Jl(e, t) {
  const s = ws();
  s.__VUE__ = !0;
  const {
      insert: n,
      remove: i,
      patchProp: o,
      createElement: l,
      createText: r,
      createComment: a,
      setText: c,
      setElementText: d,
      parentNode: h,
      nextSibling: _,
      setScopeId: x = De,
      insertStaticContent: K,
    } = e,
    E = (
      f,
      p,
      y,
      k = null,
      w = null,
      b = null,
      T = void 0,
      M = null,
      S = !!p.dynamicChildren,
    ) => {
      if (f === p) return;
      (f && !At(f, p) && ((k = Zt(f)), Oe(f, w, b, !0), (f = null)),
        p.patchFlag === -2 && ((S = !1), (p.dynamicChildren = null)));
      const { type: $, ref: R, shapeFlag: A } = p;
      switch ($) {
        case Ts:
          le(f, p, y, k);
          break;
        case tt:
          ee(f, p, y, k);
          break;
        case os:
          f == null && H(p, y, k, T);
          break;
        case V:
          Yt(f, p, y, k, w, b, T, M, S);
          break;
        default:
          A & 1
            ? F(f, p, y, k, w, b, T, M, S)
            : A & 6
              ? Qt(f, p, y, k, w, b, T, M, S)
              : (A & 64 || A & 128) && $.process(f, p, y, k, w, b, T, M, S, St);
      }
      R != null && w
        ? Pt(R, f && f.ref, b, p || f, !p)
        : R == null && f && f.ref != null && Pt(f.ref, null, b, f, !0);
    },
    le = (f, p, y, k) => {
      if (f == null) n((p.el = r(p.children)), y, k);
      else {
        const w = (p.el = f.el);
        p.children !== f.children && c(w, p.children);
      }
    },
    ee = (f, p, y, k) => {
      f == null ? n((p.el = a(p.children || "")), y, k) : (p.el = f.el);
    },
    H = (f, p, y, k) => {
      [f.el, f.anchor] = K(f.children, p, y, k, f.el, f.anchor);
    },
    Q = ({ el: f, anchor: p }, y, k) => {
      let w;
      for (; f && f !== p; ) ((w = _(f)), n(f, y, k), (f = w));
      n(p, y, k);
    },
    P = ({ el: f, anchor: p }) => {
      let y;
      for (; f && f !== p; ) ((y = _(f)), i(f), (f = y));
      i(p);
    },
    F = (f, p, y, k, w, b, T, M, S) => {
      if (
        (p.type === "svg" ? (T = "svg") : p.type === "math" && (T = "mathml"),
        f == null)
      )
        C(p, y, k, w, b, T, M, S);
      else {
        const $ = f.el && f.el._isVueCE ? f.el : null;
        try {
          ($ && $._beginPatch(), Gt(f, p, w, b, T, M, S));
        } finally {
          $ && $._endPatch();
        }
      }
    },
    C = (f, p, y, k, w, b, T, M) => {
      let S, $;
      const { props: R, shapeFlag: A, transition: I, dirs: L } = f;
      if (
        ((S = f.el = l(f.type, b, R && R.is, R)),
        A & 8
          ? d(S, f.children)
          : A & 16 && Ce(f.children, S, null, k, w, Ds(f, b), T, M),
        L && lt(f, null, k, "created"),
        U(S, f, f.scopeId, T, k),
        R)
      ) {
        for (const X in R) X !== "value" && !Et(X) && o(S, X, null, R[X], b, k);
        ("value" in R && o(S, "value", null, R.value, b),
          ($ = R.onVnodeBeforeMount) && je($, k, f));
      }
      L && lt(f, null, k, "beforeMount");
      const B = Gl(w, I);
      (B && I.beforeEnter(S),
        n(S, p, y),
        (($ = R && R.onVnodeMounted) || B || L) &&
          be(() => {
            ($ && je($, k, f), B && I.enter(S), L && lt(f, null, k, "mounted"));
          }, w));
    },
    U = (f, p, y, k, w) => {
      if ((y && x(f, y), k)) for (let b = 0; b < k.length; b++) x(f, k[b]);
      if (w) {
        let b = w.subTree;
        if (
          p === b ||
          (io(b.type) && (b.ssContent === p || b.ssFallback === p))
        ) {
          const T = w.vnode;
          U(f, T, T.scopeId, T.slotScopeIds, w.parent);
        }
      }
    },
    Ce = (f, p, y, k, w, b, T, M, S = 0) => {
      for (let $ = S; $ < f.length; $++) {
        const R = (f[$] = M ? qe(f[$]) : Le(f[$]));
        E(null, R, p, y, k, w, b, T, M);
      }
    },
    Gt = (f, p, y, k, w, b, T) => {
      const M = (p.el = f.el);
      let { patchFlag: S, dynamicChildren: $, dirs: R } = p;
      S |= f.patchFlag & 16;
      const A = f.props || Z,
        I = p.props || Z;
      let L;
      if (
        (y && rt(y, !1),
        (L = I.onVnodeBeforeUpdate) && je(L, y, p, f),
        R && lt(p, f, y, "beforeUpdate"),
        y && rt(y, !0),
        ((A.innerHTML && I.innerHTML == null) ||
          (A.textContent && I.textContent == null)) &&
          d(M, ""),
        $
          ? nt(f.dynamicChildren, $, M, y, k, Ds(p, w), b)
          : T || te(f, p, M, null, y, k, Ds(p, w), b, !1),
        S > 0)
      ) {
        if (S & 16) kt(M, A, I, y, w);
        else if (
          (S & 2 && A.class !== I.class && o(M, "class", null, I.class, w),
          S & 4 && o(M, "style", A.style, I.style, w),
          S & 8)
        ) {
          const B = p.dynamicProps;
          for (let X = 0; X < B.length; X++) {
            const G = B[X],
              ae = A[G],
              ce = I[G];
            (ce !== ae || G === "value") && o(M, G, ae, ce, w, y);
          }
        }
        S & 1 && f.children !== p.children && d(M, p.children);
      } else !T && $ == null && kt(M, A, I, y, w);
      ((L = I.onVnodeUpdated) || R) &&
        be(() => {
          (L && je(L, y, p, f), R && lt(p, f, y, "updated"));
        }, k);
    },
    nt = (f, p, y, k, w, b, T) => {
      for (let M = 0; M < p.length; M++) {
        const S = f[M],
          $ = p[M],
          R =
            S.el && (S.type === V || !At(S, $) || S.shapeFlag & 198)
              ? h(S.el)
              : y;
        E(S, $, R, null, k, w, b, T, !0);
      }
    },
    kt = (f, p, y, k, w) => {
      if (p !== y) {
        if (p !== Z)
          for (const b in p) !Et(b) && !(b in y) && o(f, b, p[b], null, w, k);
        for (const b in y) {
          if (Et(b)) continue;
          const T = y[b],
            M = p[b];
          T !== M && b !== "value" && o(f, b, M, T, w, k);
        }
        "value" in y && o(f, "value", p.value, y.value, w);
      }
    },
    Yt = (f, p, y, k, w, b, T, M, S) => {
      const $ = (p.el = f ? f.el : r("")),
        R = (p.anchor = f ? f.anchor : r(""));
      let { patchFlag: A, dynamicChildren: I, slotScopeIds: L } = p;
      (L && (M = M ? M.concat(L) : L),
        f == null
          ? (n($, y, k), n(R, y, k), Ce(p.children || [], y, R, w, b, T, M, S))
          : A > 0 &&
              A & 64 &&
              I &&
              f.dynamicChildren &&
              f.dynamicChildren.length === I.length
            ? (nt(f.dynamicChildren, I, y, w, b, T, M),
              (p.key != null || (w && p === w.subTree)) && to(f, p, !0))
            : te(f, p, y, R, w, b, T, M, S));
    },
    Qt = (f, p, y, k, w, b, T, M, S) => {
      ((p.slotScopeIds = M),
        f == null
          ? p.shapeFlag & 512
            ? w.ctx.activate(p, y, k, T, S)
            : Os(p, y, k, w, b, T, S)
          : bn(f, p, S));
    },
    Os = (f, p, y, k, w, b, T) => {
      const M = (f.component = or(f, k, w));
      if ((Di(f) && (M.ctx.renderer = St), rr(M, !1, T), M.asyncDep)) {
        if ((w && w.registerDep(M, ve, T), !f.el)) {
          const S = (M.subTree = J(tt));
          (ee(null, S, p, y), (f.placeholder = S.el));
        }
      } else ve(M, f, p, y, w, b, T);
    },
    bn = (f, p, y) => {
      const k = (p.component = f.component);
      if (Vl(f, p, y))
        if (k.asyncDep && !k.asyncResolved) {
          ie(k, p, y);
          return;
        } else ((k.next = p), k.update());
      else ((p.el = f.el), (k.vnode = p));
    },
    ve = (f, p, y, k, w, b, T) => {
      const M = () => {
        if (f.isMounted) {
          let { next: A, bu: I, u: L, parent: B, vnode: X } = f;
          {
            const Ee = so(f);
            if (Ee) {
              (A && ((A.el = X.el), ie(f, A, T)),
                Ee.asyncDep.then(() => {
                  be(() => {
                    f.isUnmounted || $();
                  }, w);
                }));
              return;
            }
          }
          let G = A,
            ae;
          (rt(f, !1),
            A ? ((A.el = X.el), ie(f, A, T)) : (A = X),
            I && ns(I),
            (ae = A.props && A.props.onVnodeBeforeUpdate) && je(ae, B, A, X),
            rt(f, !0));
          const ce = Nn(f),
            Ie = f.subTree;
          ((f.subTree = ce),
            E(Ie, ce, h(Ie.el), Zt(Ie), f, w, b),
            (A.el = ce.el),
            G === null && Dl(f, ce.el),
            L && be(L, w),
            (ae = A.props && A.props.onVnodeUpdated) &&
              be(() => je(ae, B, A, X), w));
        } else {
          let A;
          const { el: I, props: L } = p,
            { bm: B, m: X, parent: G, root: ae, type: ce } = f,
            Ie = Ft(p);
          (rt(f, !1),
            B && ns(B),
            !Ie && (A = L && L.onVnodeBeforeMount) && je(A, G, p),
            rt(f, !0));
          {
            ae.ce &&
              ae.ce._hasShadowRoot() &&
              ae.ce._injectChildStyle(ce, f.parent ? f.parent.type : void 0);
            const Ee = (f.subTree = Nn(f));
            (E(null, Ee, y, k, f, w, b), (p.el = Ee.el));
          }
          if ((X && be(X, w), !Ie && (A = L && L.onVnodeMounted))) {
            const Ee = p;
            be(() => je(A, G, Ee), w);
          }
          ((p.shapeFlag & 256 ||
            (G && Ft(G.vnode) && G.vnode.shapeFlag & 256)) &&
            f.a &&
            be(f.a, w),
            (f.isMounted = !0),
            (p = y = k = null));
        }
      };
      f.scope.on();
      const S = (f.effect = new vi(M));
      f.scope.off();
      const $ = (f.update = S.run.bind(S)),
        R = (f.job = S.runIfDirty.bind(S));
      ((R.i = f), (R.id = f.uid), (S.scheduler = () => hn(R)), rt(f, !0), $());
    },
    ie = (f, p, y) => {
      p.component = f;
      const k = f.vnode.props;
      ((f.vnode = p),
        (f.next = null),
        Ul(f, p.props, k, y),
        Wl(f, p.children, y),
        ze(),
        On(f),
        Je());
    },
    te = (f, p, y, k, w, b, T, M, S = !1) => {
      const $ = f && f.children,
        R = f ? f.shapeFlag : 0,
        A = p.children,
        { patchFlag: I, shapeFlag: L } = p;
      if (I > 0) {
        if (I & 128) {
          Xt($, A, y, k, w, b, T, M, S);
          return;
        } else if (I & 256) {
          it($, A, y, k, w, b, T, M, S);
          return;
        }
      }
      L & 8
        ? (R & 16 && Ct($, w, b), A !== $ && d(y, A))
        : R & 16
          ? L & 16
            ? Xt($, A, y, k, w, b, T, M, S)
            : Ct($, w, b, !0)
          : (R & 8 && d(y, ""), L & 16 && Ce(A, y, k, w, b, T, M, S));
    },
    it = (f, p, y, k, w, b, T, M, S) => {
      ((f = f || vt), (p = p || vt));
      const $ = f.length,
        R = p.length,
        A = Math.min($, R);
      let I;
      for (I = 0; I < A; I++) {
        const L = (p[I] = S ? qe(p[I]) : Le(p[I]));
        E(f[I], L, y, null, w, b, T, M, S);
      }
      $ > R ? Ct(f, w, b, !0, !1, A) : Ce(p, y, k, w, b, T, M, S, A);
    },
    Xt = (f, p, y, k, w, b, T, M, S) => {
      let $ = 0;
      const R = p.length;
      let A = f.length - 1,
        I = R - 1;
      for (; $ <= A && $ <= I; ) {
        const L = f[$],
          B = (p[$] = S ? qe(p[$]) : Le(p[$]));
        if (At(L, B)) E(L, B, y, null, w, b, T, M, S);
        else break;
        $++;
      }
      for (; $ <= A && $ <= I; ) {
        const L = f[A],
          B = (p[I] = S ? qe(p[I]) : Le(p[I]));
        if (At(L, B)) E(L, B, y, null, w, b, T, M, S);
        else break;
        (A--, I--);
      }
      if ($ > A) {
        if ($ <= I) {
          const L = I + 1,
            B = L < R ? p[L].el : k;
          for (; $ <= I; )
            (E(null, (p[$] = S ? qe(p[$]) : Le(p[$])), y, B, w, b, T, M, S),
              $++);
        }
      } else if ($ > I) for (; $ <= A; ) (Oe(f[$], w, b, !0), $++);
      else {
        const L = $,
          B = $,
          X = new Map();
        for ($ = B; $ <= I; $++) {
          const we = (p[$] = S ? qe(p[$]) : Le(p[$]));
          we.key != null && X.set(we.key, $);
        }
        let G,
          ae = 0;
        const ce = I - B + 1;
        let Ie = !1,
          Ee = 0;
        const Mt = new Array(ce);
        for ($ = 0; $ < ce; $++) Mt[$] = 0;
        for ($ = L; $ <= A; $++) {
          const we = f[$];
          if (ae >= ce) {
            Oe(we, w, b, !0);
            continue;
          }
          let Re;
          if (we.key != null) Re = X.get(we.key);
          else
            for (G = B; G <= I; G++)
              if (Mt[G - B] === 0 && At(we, p[G])) {
                Re = G;
                break;
              }
          Re === void 0
            ? Oe(we, w, b, !0)
            : ((Mt[Re - B] = $ + 1),
              Re >= Ee ? (Ee = Re) : (Ie = !0),
              E(we, p[Re], y, null, w, b, T, M, S),
              ae++);
        }
        const xn = Ie ? Yl(Mt) : vt;
        for (G = xn.length - 1, $ = ce - 1; $ >= 0; $--) {
          const we = B + $,
            Re = p[we],
            kn = p[we + 1],
            Cn = we + 1 < R ? kn.el || no(kn) : k;
          Mt[$] === 0
            ? E(null, Re, y, Cn, w, b, T, M, S)
            : Ie && (G < 0 || $ !== xn[G] ? ot(Re, y, Cn, 2) : G--);
        }
      }
    },
    ot = (f, p, y, k, w = null) => {
      const { el: b, type: T, transition: M, children: S, shapeFlag: $ } = f;
      if ($ & 6) {
        ot(f.component.subTree, p, y, k);
        return;
      }
      if ($ & 128) {
        f.suspense.move(p, y, k);
        return;
      }
      if ($ & 64) {
        T.move(f, p, y, St);
        return;
      }
      if (T === V) {
        n(b, p, y);
        for (let A = 0; A < S.length; A++) ot(S[A], p, y, k);
        n(f.anchor, p, y);
        return;
      }
      if (T === os) {
        Q(f, p, y);
        return;
      }
      if (k !== 2 && $ & 1 && M)
        if (k === 0)
          M.persisted && !b[Ns]
            ? n(b, p, y)
            : (M.beforeEnter(b), n(b, p, y), be(() => M.enter(b), w));
        else {
          const { leave: A, delayLeave: I, afterLeave: L } = M,
            B = () => {
              f.ctx.isUnmounted ? i(b) : n(b, p, y);
            },
            X = () => {
              const G = b._isLeaving || !!b[Ns];
              (b._isLeaving && b[Ns](!0),
                M.persisted && !G
                  ? B()
                  : A(b, () => {
                      (B(), L && L());
                    }));
            };
          I ? I(b, B, X) : X();
        }
      else n(b, p, y);
    },
    Oe = (f, p, y, k = !1, w = !1) => {
      const {
        type: b,
        props: T,
        ref: M,
        children: S,
        dynamicChildren: $,
        shapeFlag: R,
        patchFlag: A,
        dirs: I,
        cacheIndex: L,
        memo: B,
      } = f;
      if (
        (A === -2 && (w = !1),
        M != null && (ze(), Pt(M, null, y, f, !0), Je()),
        L != null && (p.renderCache[L] = void 0),
        R & 256)
      ) {
        p.ctx.deactivate(f);
        return;
      }
      const X = R & 1 && I,
        G = !Ft(f);
      let ae;
      if ((G && (ae = T && T.onVnodeBeforeUnmount) && je(ae, p, f), R & 6))
        ho(f.component, y, k);
      else {
        if (R & 128) {
          f.suspense.unmount(y, k);
          return;
        }
        (X && lt(f, null, p, "beforeUnmount"),
          R & 64
            ? f.type.remove(f, p, y, St, k)
            : $ && !$.hasOnce && (b !== V || (A > 0 && A & 64))
              ? Ct($, p, y, !1, !0)
              : ((b === V && A & 384) || (!w && R & 16)) && Ct(S, p, y),
          k && wn(f));
      }
      const ce = B != null && L == null;
      ((G && (ae = T && T.onVnodeUnmounted)) || X || ce) &&
        be(() => {
          (ae && je(ae, p, f),
            X && lt(f, null, p, "unmounted"),
            ce && (f.el = null));
        }, y);
    },
    wn = (f) => {
      const { type: p, el: y, anchor: k, transition: w } = f;
      if (p === V) {
        po(y, k);
        return;
      }
      if (p === os) {
        P(f);
        return;
      }
      const b = () => {
        (i(y), w && !w.persisted && w.afterLeave && w.afterLeave());
      };
      if (f.shapeFlag & 1 && w && !w.persisted) {
        const { leave: T, delayLeave: M } = w,
          S = () => T(y, b);
        M ? M(f.el, b, S) : S();
      } else b();
    },
    po = (f, p) => {
      let y;
      for (; f !== p; ) ((y = _(f)), i(f), (f = y));
      i(p);
    },
    ho = (f, p, y) => {
      const { bum: k, scope: w, job: b, subTree: T, um: M, m: S, a: $ } = f;
      (Hn(S),
        Hn($),
        k && ns(k),
        w.stop(),
        b && ((b.flags |= 8), Oe(T, f, p, y)),
        M && be(M, p),
        be(() => {
          f.isUnmounted = !0;
        }, p));
    },
    Ct = (f, p, y, k = !1, w = !1, b = 0) => {
      for (let T = b; T < f.length; T++) Oe(f[T], p, y, k, w);
    },
    Zt = (f) => {
      if (f.shapeFlag & 6) return Zt(f.component.subTree);
      if (f.shapeFlag & 128) return f.suspense.next();
      const p = _(f.anchor || f.el),
        y = p && p[ul];
      return y ? _(y) : p;
    };
  let Is = !1;
  const $n = (f, p, y) => {
      let k;
      (f == null
        ? p._vnode && (Oe(p._vnode, null, null, !0), (k = p._vnode.component))
        : E(p._vnode || null, f, p, null, null, null, y),
        (p._vnode = f),
        Is || ((Is = !0), On(k), ji(), (Is = !1)));
    },
    St = {
      p: E,
      um: Oe,
      m: ot,
      r: wn,
      mt: Os,
      mc: Ce,
      pc: te,
      pbc: nt,
      n: Zt,
      o: e,
    };
  return { render: $n, hydrate: void 0, createApp: Rl($n) };
}
function Ds({ type: e, props: t }, s) {
  return (s === "svg" && e === "foreignObject") ||
    (s === "mathml" &&
      e === "annotation-xml" &&
      t &&
      t.encoding &&
      t.encoding.includes("html"))
    ? void 0
    : s;
}
function rt({ effect: e, job: t }, s) {
  s ? ((e.flags |= 32), (t.flags |= 4)) : ((e.flags &= -33), (t.flags &= -5));
}
function Gl(e, t) {
  return (!e || (e && !e.pendingBranch)) && t && !t.persisted;
}
function to(e, t, s = !1) {
  const n = e.children,
    i = t.children;
  if (N(n) && N(i))
    for (let o = 0; o < n.length; o++) {
      const l = n[o];
      let r = i[o];
      (r.shapeFlag & 1 &&
        !r.dynamicChildren &&
        ((r.patchFlag <= 0 || r.patchFlag === 32) &&
          ((r = i[o] = qe(i[o])), (r.el = l.el)),
        !s && r.patchFlag !== -2 && to(l, r)),
        r.type === Ts &&
          (r.patchFlag === -1 && (r = i[o] = qe(r)), (r.el = l.el)),
        r.type === tt && !r.el && (r.el = l.el));
    }
}
function Yl(e) {
  const t = e.slice(),
    s = [0];
  let n, i, o, l, r;
  const a = e.length;
  for (n = 0; n < a; n++) {
    const c = e[n];
    if (c !== 0) {
      if (((i = s[s.length - 1]), e[i] < c)) {
        ((t[n] = i), s.push(n));
        continue;
      }
      for (o = 0, l = s.length - 1; o < l; )
        ((r = (o + l) >> 1), e[s[r]] < c ? (o = r + 1) : (l = r));
      c < e[s[o]] && (o > 0 && (t[n] = s[o - 1]), (s[o] = n));
    }
  }
  for (o = s.length, l = s[o - 1]; o-- > 0; ) ((s[o] = l), (l = t[l]));
  return s;
}
function so(e) {
  const t = e.subTree.component;
  if (t) return t.asyncDep && !t.asyncResolved ? t : so(t);
}
function Hn(e) {
  if (e) for (let t = 0; t < e.length; t++) e[t].flags |= 8;
}
function no(e) {
  if (e.placeholder) return e.placeholder;
  const t = e.component;
  return t ? no(t.subTree) : null;
}
const io = (e) => e.__isSuspense;
function Ql(e, t) {
  t && t.pendingBranch
    ? N(e)
      ? t.effects.push(...e)
      : t.effects.push(e)
    : nl(e);
}
const V = Symbol.for("v-fgt"),
  Ts = Symbol.for("v-txt"),
  tt = Symbol.for("v-cmt"),
  os = Symbol.for("v-stc"),
  Nt = [];
let xe = null;
function g(e = !1) {
  Nt.push((xe = e ? null : []));
}
function Xl() {
  (Nt.pop(), (xe = Nt[Nt.length - 1] || null));
}
let Ut = 1;
function Un(e, t = !1) {
  ((Ut += e), e < 0 && xe && t && (xe.hasOnce = !0));
}
function oo(e) {
  return (
    (e.dynamicChildren = Ut > 0 ? xe || vt : null),
    Xl(),
    Ut > 0 && xe && xe.push(e),
    e
  );
}
function m(e, t, s, n, i, o) {
  return oo(u(e, t, s, n, i, o, !0));
}
function Se(e, t, s, n, i) {
  return oo(J(e, t, s, n, i, !0));
}
function lo(e) {
  return e ? e.__v_isVNode === !0 : !1;
}
function At(e, t) {
  return e.type === t.type && e.key === t.key;
}
const ro = ({ key: e }) => e ?? null,
  ls = ({ ref: e, ref_key: t, ref_for: s }) => (
    typeof e == "number" && (e = "" + e),
    e != null
      ? re(e) || he(e) || D(e)
        ? { i: $e, r: e, k: t, f: !!s }
        : e
      : null
  );
function u(
  e,
  t = null,
  s = null,
  n = 0,
  i = null,
  o = e === V ? 0 : 1,
  l = !1,
  r = !1,
) {
  const a = {
    __v_isVNode: !0,
    __v_skip: !0,
    type: e,
    props: t,
    key: t && ro(t),
    ref: t && ls(t),
    scopeId: Fi,
    slotScopeIds: null,
    children: s,
    component: null,
    suspense: null,
    ssContent: null,
    ssFallback: null,
    dirs: null,
    transition: null,
    el: null,
    anchor: null,
    target: null,
    targetStart: null,
    targetAnchor: null,
    staticCount: 0,
    shapeFlag: o,
    patchFlag: n,
    dynamicProps: i,
    dynamicChildren: null,
    appContext: null,
    ctx: $e,
  };
  return (
    r
      ? (yn(a, s), o & 128 && e.normalize(a))
      : s && (a.shapeFlag |= re(s) ? 8 : 16),
    Ut > 0 &&
      !l &&
      xe &&
      (a.patchFlag > 0 || o & 6) &&
      a.patchFlag !== 32 &&
      xe.push(a),
    a
  );
}
const J = Zl;
function Zl(e, t = null, s = null, n = 0, i = null, o = !1) {
  if (((!e || e === kl) && (e = tt), lo(e))) {
    const r = $t(e, t, !0);
    return (
      s && yn(r, s),
      Ut > 0 &&
        !o &&
        xe &&
        (r.shapeFlag & 6 ? (xe[xe.indexOf(e)] = r) : xe.push(r)),
      (r.patchFlag = -2),
      r
    );
  }
  if ((dr(e) && (e = e.__vccOpts), t)) {
    t = er(t);
    let { class: r, style: a } = t;
    (r && !re(r) && (t.class = ue(r)),
      Y(a) && (pn(a) && !N(a) && (a = ge({}, a)), (t.style = $s(a))));
  }
  const l = re(e) ? 1 : io(e) ? 128 : cl(e) ? 64 : Y(e) ? 4 : D(e) ? 2 : 0;
  return u(e, t, s, n, i, l, o, !0);
}
function er(e) {
  return e ? (pn(e) || Gi(e) ? ge({}, e) : e) : null;
}
function $t(e, t, s = !1, n = !1) {
  const { props: i, ref: o, patchFlag: l, children: r, transition: a } = e,
    c = t ? sr(i || {}, t) : i,
    d = {
      __v_isVNode: !0,
      __v_skip: !0,
      type: e.type,
      props: c,
      key: c && ro(c),
      ref:
        t && t.ref
          ? s && o
            ? N(o)
              ? o.concat(ls(t))
              : [o, ls(t)]
            : ls(t)
          : o,
      scopeId: e.scopeId,
      slotScopeIds: e.slotScopeIds,
      children: r,
      target: e.target,
      targetStart: e.targetStart,
      targetAnchor: e.targetAnchor,
      staticCount: e.staticCount,
      shapeFlag: e.shapeFlag,
      patchFlag: t && e.type !== V ? (l === -1 ? 16 : l | 16) : l,
      dynamicProps: e.dynamicProps,
      dynamicChildren: e.dynamicChildren,
      appContext: e.appContext,
      dirs: e.dirs,
      transition: a,
      component: e.component,
      suspense: e.suspense,
      ssContent: e.ssContent && $t(e.ssContent),
      ssFallback: e.ssFallback && $t(e.ssFallback),
      placeholder: e.placeholder,
      el: e.el,
      anchor: e.anchor,
      ctx: e.ctx,
      ce: e.ce,
    };
  return (a && n && gn(d, a.clone(d)), d);
}
function O(e = " ", t = 0) {
  return J(Ts, null, e, t);
}
function tr(e, t) {
  const s = J(os, null, e);
  return ((s.staticCount = t), s);
}
function j(e = "", t = !1) {
  return t ? (g(), Se(tt, null, e)) : J(tt, null, e);
}
function Le(e) {
  return e == null || typeof e == "boolean"
    ? J(tt)
    : N(e)
      ? J(V, null, e.slice())
      : lo(e)
        ? qe(e)
        : J(Ts, null, String(e));
}
function qe(e) {
  return (e.el === null && e.patchFlag !== -1) || e.memo ? e : $t(e);
}
function yn(e, t) {
  let s = 0;
  const { shapeFlag: n } = e;
  if (t == null) t = null;
  else if (N(t)) s = 16;
  else if (typeof t == "object")
    if (n & 65) {
      const i = t.default;
      i && (i._c && (i._d = !1), yn(e, i()), i._c && (i._d = !0));
      return;
    } else {
      s = 32;
      const i = t._;
      !i && !Gi(t)
        ? (t._ctx = $e)
        : i === 3 &&
          $e &&
          ($e.slots._ === 1 ? (t._ = 1) : ((t._ = 2), (e.patchFlag |= 1024)));
    }
  else
    D(t)
      ? ((t = { default: t, _ctx: $e }), (s = 32))
      : ((t = String(t)), n & 64 ? ((s = 16), (t = [O(t)])) : (s = 8));
  ((e.children = t), (e.shapeFlag |= s));
}
function sr(...e) {
  const t = {};
  for (let s = 0; s < e.length; s++) {
    const n = e[s];
    for (const i in n)
      if (i === "class")
        t.class !== n.class && (t.class = ue([t.class, n.class]));
      else if (i === "style") t.style = $s([t.style, n.style]);
      else if (gs(i)) {
        const o = t[i],
          l = n[i];
        l && o !== l && !(N(o) && o.includes(l))
          ? (t[i] = o ? [].concat(o, l) : l)
          : l == null && o == null && !vs(i) && (t[i] = l);
      } else i !== "" && (t[i] = n[i]);
  }
  return t;
}
function je(e, t, s, n = null) {
  Ae(e, t, 7, [s, n]);
}
const nr = qi();
let ir = 0;
function or(e, t, s) {
  const n = e.type,
    i = (t ? t.appContext : e.appContext) || nr,
    o = {
      uid: ir++,
      vnode: e,
      type: n,
      parent: t,
      appContext: i,
      root: null,
      next: null,
      subTree: null,
      effect: null,
      update: null,
      job: null,
      scope: new Mo(!0),
      render: null,
      proxy: null,
      exposed: null,
      exposeProxy: null,
      withProxy: null,
      provides: t ? t.provides : Object.create(i.provides),
      ids: t ? t.ids : ["", 0, 0],
      accessCache: null,
      renderCache: [],
      components: null,
      directives: null,
      propsOptions: Qi(n, i),
      emitsOptions: Bi(n, i),
      emit: null,
      emitted: null,
      propsDefaults: Z,
      inheritAttrs: n.inheritAttrs,
      ctx: Z,
      data: Z,
      props: Z,
      attrs: Z,
      slots: Z,
      refs: Z,
      setupState: Z,
      setupContext: null,
      suspense: s,
      suspenseId: s ? s.pendingId : 0,
      asyncDep: null,
      asyncResolved: !1,
      isMounted: !1,
      isUnmounted: !1,
      isDeactivated: !1,
      bc: null,
      c: null,
      bm: null,
      m: null,
      bu: null,
      u: null,
      um: null,
      bum: null,
      da: null,
      a: null,
      rtg: null,
      rtc: null,
      ec: null,
      sp: null,
    };
  return (
    (o.ctx = { _: o }),
    (o.root = t ? t.root : o),
    (o.emit = Pl.bind(null, o)),
    e.ce && e.ce(o),
    o
  );
}
let pe = null;
const lr = () => pe || $e;
let ds, Zs;
{
  const e = ws(),
    t = (s, n) => {
      let i;
      return (
        (i = e[s]) || (i = e[s] = []),
        i.push(n),
        (o) => {
          i.length > 1 ? i.forEach((l) => l(o)) : i[0](o);
        }
      );
    };
  ((ds = t("__VUE_INSTANCE_SETTERS__", (s) => (pe = s))),
    (Zs = t("__VUE_SSR_SETTERS__", (s) => (Kt = s))));
}
const zt = (e) => {
    const t = pe;
    return (
      ds(e),
      e.scope.on(),
      () => {
        (e.scope.off(), ds(t));
      }
    );
  },
  Kn = () => {
    (pe && pe.scope.off(), ds(null));
  };
function ao(e) {
  return e.vnode.shapeFlag & 4;
}
let Kt = !1;
function rr(e, t = !1, s = !1) {
  t && Zs(t);
  const { props: n, children: i } = e.vnode,
    o = ao(e);
  (Hl(e, n, o, t), Bl(e, i, s || t));
  const l = o ? ar(e, t) : void 0;
  return (t && Zs(!1), l);
}
function ar(e, t) {
  const s = e.type;
  ((e.accessCache = Object.create(null)), (e.proxy = new Proxy(e.ctx, Sl)));
  const { setup: n } = s;
  if (n) {
    ze();
    const i = (e.setupContext = n.length > 1 ? cr(e) : null),
      o = zt(e),
      l = Wt(n, e, 0, [e.props, i]),
      r = ui(l);
    if ((Je(), o(), (r || e.sp) && !Ft(e) && Vi(e), r)) {
      if ((l.then(Kn, Kn), t))
        return l
          .then((a) => {
            qn(e, a);
          })
          .catch((a) => {
            ks(a, e, 0);
          });
      e.asyncDep = l;
    } else qn(e, l);
  } else uo(e);
}
function qn(e, t, s) {
  (D(t)
    ? e.type.__ssrInlineRender
      ? (e.ssrRender = t)
      : (e.render = t)
    : Y(t) && (e.setupState = Oi(t)),
    uo(e));
}
function uo(e, t, s) {
  const n = e.type;
  e.render || (e.render = n.render || De);
  {
    const i = zt(e);
    ze();
    try {
      Ml(e);
    } finally {
      (Je(), i());
    }
  }
}
const ur = {
  get(e, t) {
    return (de(e, "get", ""), e[t]);
  },
};
function cr(e) {
  const t = (s) => {
    e.exposed = s || {};
  };
  return {
    attrs: new Proxy(e.attrs, ur),
    slots: e.slots,
    emit: e.emit,
    expose: t,
  };
}
function As(e) {
  return e.exposed
    ? e.exposeProxy ||
        (e.exposeProxy = new Proxy(Oi(zo(e.exposed)), {
          get(t, s) {
            if (s in t) return t[s];
            if (s in Lt) return Lt[s](e);
          },
          has(t, s) {
            return s in t || s in Lt;
          },
        }))
    : e.proxy;
}
function fr(e, t = !0) {
  return D(e) ? e.displayName || e.name : e.name || (t && e.__name);
}
function dr(e) {
  return D(e) && "__vccOpts" in e;
}
const q = (e, t) => Xo(e, t, Kt),
  pr = "3.5.38";
let en;
const Bn = typeof window < "u" && window.trustedTypes;
if (Bn)
  try {
    en = Bn.createPolicy("vue", { createHTML: (e) => e });
  } catch {}
const co = en ? (e) => en.createHTML(e) : (e) => e,
  hr = "http://www.w3.org/2000/svg",
  gr = "http://www.w3.org/1998/Math/MathML",
  Ke = typeof document < "u" ? document : null,
  Wn = Ke && Ke.createElement("template"),
  vr = {
    insert: (e, t, s) => {
      t.insertBefore(e, s || null);
    },
    remove: (e) => {
      const t = e.parentNode;
      t && t.removeChild(e);
    },
    createElement: (e, t, s, n) => {
      const i =
        t === "svg"
          ? Ke.createElementNS(hr, e)
          : t === "mathml"
            ? Ke.createElementNS(gr, e)
            : s
              ? Ke.createElement(e, { is: s })
              : Ke.createElement(e);
      return (
        e === "select" &&
          n &&
          n.multiple != null &&
          i.setAttribute("multiple", n.multiple),
        i
      );
    },
    createText: (e) => Ke.createTextNode(e),
    createComment: (e) => Ke.createComment(e),
    setText: (e, t) => {
      e.nodeValue = t;
    },
    setElementText: (e, t) => {
      e.textContent = t;
    },
    parentNode: (e) => e.parentNode,
    nextSibling: (e) => e.nextSibling,
    querySelector: (e) => Ke.querySelector(e),
    setScopeId(e, t) {
      e.setAttribute(t, "");
    },
    insertStaticContent(e, t, s, n, i, o) {
      const l = s ? s.previousSibling : t.lastChild;
      if (i && (i === o || i.nextSibling))
        for (
          ;
          t.insertBefore(i.cloneNode(!0), s),
            !(i === o || !(i = i.nextSibling));
        );
      else {
        Wn.innerHTML = co(
          n === "svg"
            ? `<svg>${e}</svg>`
            : n === "mathml"
              ? `<math>${e}</math>`
              : e,
        );
        const r = Wn.content;
        if (n === "svg" || n === "mathml") {
          const a = r.firstChild;
          for (; a.firstChild; ) r.appendChild(a.firstChild);
          r.removeChild(a);
        }
        t.insertBefore(r, s);
      }
      return [
        l ? l.nextSibling : t.firstChild,
        s ? s.previousSibling : t.lastChild,
      ];
    },
  },
  mr = Symbol("_vtc");
function yr(e, t, s) {
  const n = e[mr];
  (n && (t = (t ? [t, ...n] : [...n]).join(" ")),
    t == null
      ? e.removeAttribute("class")
      : s
        ? e.setAttribute("class", t)
        : (e.className = t));
}
const zn = Symbol("_vod"),
  _r = Symbol("_vsh"),
  br = Symbol(""),
  wr = /(?:^|;)\s*display\s*:/;
function $r(e, t, s) {
  const n = e.style,
    i = re(s);
  let o = !1;
  if (s && !i) {
    if (t)
      if (re(t))
        for (const l of t.split(";")) {
          const r = l.slice(0, l.indexOf(":")).trim();
          s[r] == null && It(n, r, "");
        }
      else for (const l in t) s[l] == null && It(n, l, "");
    for (const l in s) {
      l === "display" && (o = !0);
      const r = s[l];
      r != null
        ? kr(e, l, !re(t) && t ? t[l] : void 0, r) || It(n, l, r)
        : It(n, l, "");
    }
  } else if (i) {
    if (t !== s) {
      const l = n[br];
      (l && (s += ";" + l), (n.cssText = s), (o = wr.test(s)));
    }
  } else t && e.removeAttribute("style");
  zn in e && ((e[zn] = o ? n.display : ""), e[_r] && (n.display = "none"));
}
const Jn = /\s*!important$/;
function It(e, t, s) {
  if (N(s)) s.forEach((n) => It(e, t, n));
  else if ((s == null && (s = ""), t.startsWith("--"))) e.setProperty(t, s);
  else {
    const n = xr(e, t);
    Jn.test(s)
      ? e.setProperty(st(n), s.replace(Jn, ""), "important")
      : (e[n] = s);
  }
}
const Gn = ["Webkit", "Moz", "ms"],
  Hs = {};
function xr(e, t) {
  const s = Hs[t];
  if (s) return s;
  let n = _e(t);
  if (n !== "filter" && n in e) return (Hs[t] = n);
  n = _s(n);
  for (let i = 0; i < Gn.length; i++) {
    const o = Gn[i] + n;
    if (o in e) return (Hs[t] = o);
  }
  return t;
}
function kr(e, t, s, n) {
  return (
    e.tagName === "TEXTAREA" &&
    (t === "width" || t === "height") &&
    re(n) &&
    s === n
  );
}
const Yn = "http://www.w3.org/1999/xlink";
function Qn(e, t, s, n, i, o = ko(t)) {
  n && t.startsWith("xlink:")
    ? s == null
      ? e.removeAttributeNS(Yn, t.slice(6, t.length))
      : e.setAttributeNS(Yn, t, s)
    : s == null || (o && !pi(s))
      ? e.removeAttribute(t)
      : e.setAttribute(t, o ? "" : He(s) ? String(s) : s);
}
function Xn(e, t, s, n, i) {
  if (t === "innerHTML" || t === "textContent") {
    s != null && (e[t] = t === "innerHTML" ? co(s) : s);
    return;
  }
  const o = e.tagName;
  if (t === "value" && o !== "PROGRESS" && !o.includes("-")) {
    const r = o === "OPTION" ? e.getAttribute("value") || "" : e.value,
      a = s == null ? (e.type === "checkbox" ? "on" : "") : String(s);
    ((r !== a || !("_value" in e)) && (e.value = a),
      s == null && e.removeAttribute(t),
      (e._value = s));
    return;
  }
  let l = !1;
  if (s === "" || s == null) {
    const r = typeof e[t];
    r === "boolean"
      ? (s = pi(s))
      : s == null && r === "string"
        ? ((s = ""), (l = !0))
        : r === "number" && ((s = 0), (l = !0));
  }
  try {
    e[t] = s;
  } catch {}
  l && e.removeAttribute(i || t);
}
function ut(e, t, s, n) {
  e.addEventListener(t, s, n);
}
function Cr(e, t, s, n) {
  e.removeEventListener(t, s, n);
}
const Zn = Symbol("_vei");
function Sr(e, t, s, n, i = null) {
  const o = e[Zn] || (e[Zn] = {}),
    l = o[t];
  if (n && l) l.value = n;
  else {
    const [r, a] = Mr(t);
    if (n) {
      const c = (o[t] = Or(n, i));
      ut(e, r, c, a);
    } else l && (Cr(e, r, l, a), (o[t] = void 0));
  }
}
const ei = /(?:Once|Passive|Capture)$/;
function Mr(e) {
  let t;
  if (ei.test(e)) {
    t = {};
    let n;
    for (; (n = e.match(ei)); )
      ((e = e.slice(0, e.length - n[0].length)), (t[n[0].toLowerCase()] = !0));
  }
  return [e[2] === ":" ? e.slice(3) : st(e.slice(2)), t];
}
let Us = 0;
const Tr = Promise.resolve(),
  Ar = () => Us || (Tr.then(() => (Us = 0)), (Us = Date.now()));
function Or(e, t) {
  const s = (n) => {
    if (!n._vts) n._vts = Date.now();
    else if (n._vts <= s.attached) return;
    const i = s.value;
    if (N(i)) {
      const o = n.stopImmediatePropagation;
      n.stopImmediatePropagation = () => {
        (o.call(n), (n._stopped = !0));
      };
      const l = i.slice(),
        r = [n];
      for (let a = 0; a < l.length && !n._stopped; a++) {
        const c = l[a];
        c && Ae(c, t, 5, r);
      }
    } else Ae(i, t, 5, [n]);
  };
  return ((s.value = e), (s.attached = Ar()), s);
}
const ti = (e) =>
    e.charCodeAt(0) === 111 &&
    e.charCodeAt(1) === 110 &&
    e.charCodeAt(2) > 96 &&
    e.charCodeAt(2) < 123,
  Ir = (e, t, s, n, i, o) => {
    const l = i === "svg";
    t === "class"
      ? yr(e, n, l)
      : t === "style"
        ? $r(e, s, n)
        : gs(t)
          ? vs(t) || Sr(e, t, s, n, o)
          : (
                t[0] === "."
                  ? ((t = t.slice(1)), !0)
                  : t[0] === "^"
                    ? ((t = t.slice(1)), !1)
                    : Er(e, t, n, l)
              )
            ? (Xn(e, t, n),
              !e.tagName.includes("-") &&
                (t === "value" || t === "checked" || t === "selected") &&
                Qn(e, t, n, l, o, t !== "value"))
            : e._isVueCE &&
                (Rr(e, t) ||
                  (e._def.__asyncLoader && (/[A-Z]/.test(t) || !re(n))))
              ? Xn(e, _e(t), n, o, t)
              : (t === "true-value"
                  ? (e._trueValue = n)
                  : t === "false-value" && (e._falseValue = n),
                Qn(e, t, n, l));
  };
function Er(e, t, s, n) {
  if (n)
    return !!(
      t === "innerHTML" ||
      t === "textContent" ||
      (t in e && ti(t) && D(s))
    );
  if (
    t === "spellcheck" ||
    t === "draggable" ||
    t === "translate" ||
    t === "autocorrect" ||
    (t === "sandbox" && e.tagName === "IFRAME") ||
    t === "form" ||
    (t === "list" && e.tagName === "INPUT") ||
    (t === "type" && e.tagName === "TEXTAREA")
  )
    return !1;
  if (t === "width" || t === "height") {
    const i = e.tagName;
    if (i === "IMG" || i === "VIDEO" || i === "CANVAS" || i === "SOURCE")
      return !1;
  }
  return ti(t) && re(s) ? !1 : t in e;
}
function Rr(e, t) {
  const s = e._def.props;
  if (!s) return !1;
  const n = _e(t);
  return Array.isArray(s)
    ? s.some((i) => _e(i) === n)
    : Object.keys(s).some((i) => _e(i) === n);
}
const ps = (e) => {
  const t = e.props["onUpdate:modelValue"] || !1;
  return N(t) ? (s) => ns(t, s) : t;
};
function jr(e) {
  e.target.composing = !0;
}
function si(e) {
  const t = e.target;
  t.composing && ((t.composing = !1), t.dispatchEvent(new Event("input")));
}
const bt = Symbol("_assign");
function ni(e, t, s) {
  return (t && (e = e.trim()), s && (e = bs(e)), e);
}
const ct = {
    created(e, { modifiers: { lazy: t, trim: s, number: n } }, i) {
      e[bt] = ps(i);
      const o = n || (i.props && i.props.type === "number");
      (ut(e, t ? "change" : "input", (l) => {
        l.target.composing || e[bt](ni(e.value, s, o));
      }),
        (s || o) &&
          ut(e, "change", () => {
            e.value = ni(e.value, s, o);
          }),
        t ||
          (ut(e, "compositionstart", jr),
          ut(e, "compositionend", si),
          ut(e, "change", si)));
    },
    mounted(e, { value: t }) {
      e.value = t ?? "";
    },
    beforeUpdate(
      e,
      { value: t, oldValue: s, modifiers: { lazy: n, trim: i, number: o } },
      l,
    ) {
      if (((e[bt] = ps(l)), e.composing)) return;
      const r =
          (o || e.type === "number") && !/^0\d/.test(e.value)
            ? bs(e.value)
            : e.value,
        a = t ?? "";
      if (r === a) return;
      const c = e.getRootNode();
      ((c instanceof Document || c instanceof ShadowRoot) &&
        c.activeElement === e &&
        e.type !== "range" &&
        ((n && t === s) || (i && e.value.trim() === a))) ||
        (e.value = a);
    },
  },
  tn = {
    deep: !0,
    created(e, { value: t, modifiers: { number: s } }, n) {
      const i = ms(t);
      (ut(e, "change", () => {
        const o = Array.prototype.filter
          .call(e.options, (l) => l.selected)
          .map((l) => (s ? bs(hs(l)) : hs(l)));
        (e[bt](e.multiple ? (i ? new Set(o) : o) : o[0]),
          (e._assigning = !0),
          Ei(() => {
            e._assigning = !1;
          }));
      }),
        (e[bt] = ps(n)));
    },
    mounted(e, { value: t }) {
      ii(e, t);
    },
    beforeUpdate(e, t, s) {
      e[bt] = ps(s);
    },
    updated(e, { value: t }) {
      e._assigning || ii(e, t);
    },
  };
function ii(e, t) {
  const s = e.multiple,
    n = N(t);
  if (!(s && !n && !ms(t))) {
    for (let i = 0, o = e.options.length; i < o; i++) {
      const l = e.options[i],
        r = hs(l);
      if (s)
        if (n) {
          const a = typeof r;
          a === "string" || a === "number"
            ? (l.selected = t.some((c) => String(c) === String(r)))
            : (l.selected = So(t, r) > -1);
        } else l.selected = t.has(r);
      else if (Bt(hs(l), t)) {
        e.selectedIndex !== i && (e.selectedIndex = i);
        return;
      }
    }
    !s && e.selectedIndex !== -1 && (e.selectedIndex = -1);
  }
}
function hs(e) {
  return "_value" in e ? e._value : e.value;
}
const Pr = ["ctrl", "shift", "alt", "meta"],
  Fr = {
    stop: (e) => e.stopPropagation(),
    prevent: (e) => e.preventDefault(),
    self: (e) => e.target !== e.currentTarget,
    ctrl: (e) => !e.ctrlKey,
    shift: (e) => !e.shiftKey,
    alt: (e) => !e.altKey,
    meta: (e) => !e.metaKey,
    left: (e) => "button" in e && e.button !== 0,
    middle: (e) => "button" in e && e.button !== 1,
    right: (e) => "button" in e && e.button !== 2,
    exact: (e, t) => Pr.some((s) => e[`${s}Key`] && !t.includes(s)),
  },
  Lr = (e, t) => {
    if (!e) return e;
    const s = e._withMods || (e._withMods = {}),
      n = t.join(".");
    return (
      s[n] ||
      (s[n] = (i, ...o) => {
        for (let l = 0; l < t.length; l++) {
          const r = Fr[t[l]];
          if (r && r(i, t)) return;
        }
        return e(i, ...o);
      })
    );
  },
  Nr = {
    esc: "escape",
    space: " ",
    up: "arrow-up",
    left: "arrow-left",
    right: "arrow-right",
    down: "arrow-down",
    delete: "backspace",
  },
  Vr = (e, t) => {
    const s = e._withKeys || (e._withKeys = {}),
      n = t.join(".");
    return (
      s[n] ||
      (s[n] = (i) => {
        if (!("key" in i)) return;
        const o = st(i.key);
        if (t.some((l) => l === o || Nr[l] === o)) return e(i);
      })
    );
  },
  Dr = ge({ patchProp: Ir }, vr);
let oi;
function Hr() {
  return oi || (oi = zl(Dr));
}
const Ur = (...e) => {
  const t = Hr().createApp(...e),
    { mount: s } = t;
  return (
    (t.mount = (n) => {
      const i = qr(n);
      if (!i) return;
      const o = t._component;
      (!D(o) && !o.render && !o.template && (o.template = i.innerHTML),
        i.nodeType === 1 && (i.textContent = ""));
      const l = s(i, !1, Kr(i));
      return (
        i instanceof Element &&
          (i.removeAttribute("v-cloak"), i.setAttribute("data-v-app", "")),
        l
      );
    }),
    t
  );
};
function Kr(e) {
  if (e instanceof SVGElement) return "svg";
  if (typeof MathMLElement == "function" && e instanceof MathMLElement)
    return "mathml";
}
function qr(e) {
  return re(e) ? document.querySelector(e) : e;
}
const Br = {
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    "stroke-width": "1.9",
    "stroke-linecap": "round",
    "stroke-linejoin": "round",
    "aria-hidden": "true",
  },
  Wr = ["d"],
  et = {
    __name: "Icon",
    props: { name: { type: String, required: !0 } },
    setup(e) {
      const t = {
          grid: "M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z",
          search: "M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16zM21 21l-4.3-4.3",
          link: "M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1",
          share:
            "M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8M16 6l-4-4-4 4M12 2v13",
          cpu: "M9 3v2M15 3v2M9 19v2M15 19v2M3 9h2M3 15h2M19 9h2M19 15h2M5 5h14v14H5zM9 9h6v6H9z",
          network:
            "M12 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6zM5 16a3 3 0 1 0 0 6 3 3 0 0 0 0-6zM19 16a3 3 0 1 0 0 6 3 3 0 0 0 0-6zM12 8v5M12 13l-5 3M12 13l5 3",
          bulb: "M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.3 1 2.3h6c0-1 .4-1.8 1-2.3A7 7 0 0 0 12 2z",
          bot: "M12 2v3M5 8h14a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2zM9 13h.01M15 13h.01M9 17h6",
          file: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6",
          flask:
            "M9 2h6M10 2v6l-5.5 9.5A2 2 0 0 0 6.2 21h11.6a2 2 0 0 0 1.7-3L14 8V2",
          database:
            "M12 3c-4.4 0-8 1.3-8 3s3.6 3 8 3 8-1.3 8-3-3.6-3-8-3zM4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6",
          users:
            "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8",
          play: "M6 4l14 8-14 8z",
          pause: "M7 4h3v16H7zM14 4h3v16h-3z",
          bolt: "M13 2 4 14h7l-1 8 9-12h-7z",
          pulse: "M3 12h4l3 8 4-16 3 8h4",
          spark:
            "M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8",
        },
        s = e,
        n = q(() => t[s.name] || t.grid);
      return (i, o) => (
        g(),
        m("svg", Br, [u("path", { d: n.value }, null, 8, Wr)])
      );
    },
  },
  zr = { class: "sidebar" },
  Jr = { class: "brand" },
  Gr = { class: "logo" },
  Yr = { class: "nav-label" },
  Qr = ["onClick"],
  Xr = { class: "t" },
  Zr = { key: 0, class: "badge" },
  ea = {
    __name: "SideNav",
    props: {
      modelValue: String,
      insightCount: { type: Number, default: null },
    },
    emits: ["update:modelValue"],
    setup(e) {
      const t = e,
        s = q(() => [
          {
            label: "Discover",
            items: [
              { id: "overview", label: "Overview", icon: "grid" },
              { id: "search", label: "Search papers", icon: "search" },
              { id: "related", label: "Related work", icon: "link" },
              { id: "citations", label: "Citations", icon: "share" },
            ],
          },
          {
            label: "Analyze",
            items: [
              { id: "agent", label: "Agents", icon: "cpu" },
              { id: "investigate", label: "Investigate", icon: "network" },
              {
                id: "insights",
                label: "Insights",
                icon: "bulb",
                badge: t.insightCount,
              },
            ],
          },
          {
            label: "Automate",
            items: [{ id: "analyst", label: "Analyst", icon: "bot" }],
          },
        ]);
      return (n, i) => (
        g(),
        m("aside", zr, [
          u("div", Jr, [
            u("span", Gr, [
              J(et, {
                name: "spark",
                style: { width: "18px", height: "18px" },
              }),
            ]),
            i[0] ||
              (i[0] = u(
                "span",
                { class: "name" },
                [
                  O(" ProjMnemosyne "),
                  u("small", null, "Research Intelligence"),
                ],
                -1,
              )),
          ]),
          (g(!0),
          m(
            V,
            null,
            oe(
              s.value,
              (o) => (
                g(),
                m("div", { key: o.label, class: "nav-group" }, [
                  u("div", Yr, v(o.label), 1),
                  (g(!0),
                  m(
                    V,
                    null,
                    oe(
                      o.items,
                      (l) => (
                        g(),
                        m(
                          "button",
                          {
                            key: l.id,
                            class: ue([
                              "nav-item",
                              { active: e.modelValue === l.id },
                            ]),
                            onClick: (r) => n.$emit("update:modelValue", l.id),
                          },
                          [
                            J(et, { name: l.icon }, null, 8, ["name"]),
                            u("span", Xr, v(l.label), 1),
                            l.badge != null
                              ? (g(), m("span", Zr, v(l.badge), 1))
                              : j("", !0),
                          ],
                          10,
                          Qr,
                        )
                      ),
                    ),
                    128,
                  )),
                ])
              ),
            ),
            128,
          )),
          i[1] ||
            (i[1] = u(
              "div",
              { class: "sidebar-foot" },
              [
                O(" code orchestrates, models judge."),
                u("br"),
                O(
                  " L1 ingest · L2 extract · L3 retrieve+graph · L4 tools · L5 agents · L6 A2A ",
                ),
              ],
              -1,
            )),
        ])
      );
    },
  };
async function ta(e) {
  return fetch(`/api/explain-insight?id=${encodeURIComponent(e)}`).then((t) =>
    t.json(),
  );
}
async function sa() {
  return fetch("/api/overview").then((e) => e.json());
}
let Ks = null;
function na() {
  return (Ks || (Ks = fetch("/api/corpus").then((e) => e.json())), Ks);
}
async function _n() {
  return fetch("/api/analyst/status").then((e) => e.json());
}
async function ia() {
  return fetch("/api/analyst/config").then((e) => e.json());
}
async function li(e, t) {
  return fetch(`/api/analyst/${e}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: t ? JSON.stringify(t) : void 0,
  }).then((s) => s.json());
}
const oa = { class: "topbar" },
  la = { class: "crumb" },
  ra = ["title"],
  aa = {
    __name: "TopBar",
    props: { title: String, subtitle: String },
    emits: ["go"],
    setup(e) {
      const t = ne(null);
      let s = null;
      async function n() {
        try {
          t.value = await _n();
        } catch {
          t.value = null;
        }
      }
      const i = q(() => {
          const r = t.value;
          return !r || !r.running
            ? ""
            : r.paused
              ? "paused"
              : r.phase === "analyzing" || r.phase === "growing"
                ? "busy"
                : "live";
        }),
        o = q(() => {
          const r = t.value;
          return r
            ? r.running
              ? r.paused
                ? "analyst paused"
                : `analyst ${{ analyzing: "analyzing", growing: "fetching papers", sleeping: "waiting", idle: "idle" }[r.phase] || r.phase} · gen ${r.generation}`
              : "analyst idle"
            : "analyst offline";
        }),
        l = q(() => {
          const r = t.value;
          return r
            ? `${r.insights_banked} insights banked · ${r.tasks.done}/${r.tasks.total} tasks done · click to control`
            : "Open analyst control";
        });
      return (
        xt(() => {
          (n(), (s = setInterval(n, 3e3)));
        }),
        Ss(() => clearInterval(s)),
        (r, a) => (
          g(),
          m("div", oa, [
            u("div", la, [
              O(v(e.title) + " ", 1),
              u("small", null, v(e.subtitle), 1),
            ]),
            a[1] || (a[1] = u("div", { class: "spacer" }, null, -1)),
            u(
              "button",
              {
                class: "status-pill",
                title: l.value,
                onClick: a[0] || (a[0] = (c) => r.$emit("go", "analyst")),
              },
              [
                u("span", { class: ue(["dot", i.value]) }, null, 2),
                u("span", null, v(o.value), 1),
              ],
              8,
              ra,
            ),
          ])
        )
      );
    },
  },
  Qe = (e, t) => {
    const s = e.__vccOpts || e;
    for (const [n, i] of t) s[n] = i;
    return s;
  },
  ua = { key: 0, class: "stat-grid" },
  ca = { class: "stat-grid" },
  fa = ["onClick"],
  da = { class: "num" },
  pa = { class: "label" },
  ha = { key: 0, class: "sub" },
  ga = { class: "ov-cols" },
  va = { class: "card" },
  ma = { key: 0, class: "muted" },
  ya = { key: 1, class: "bars" },
  _a = { class: "blabel" },
  ba = { class: "bar-track" },
  wa = { class: "bval" },
  $a = { key: 2, class: "conf-line" },
  xa = { class: "tag tag--conf-high" },
  ka = { class: "tag tag--conf-medium" },
  Ca = { class: "tag" },
  Sa = { class: "muted" },
  Ma = { class: "card" },
  Ta = { class: "analyst-snap" },
  Aa = { class: "muted" },
  Oa = { class: "snap-grid" },
  Ia = { class: "snum" },
  Ea = { class: "muted" },
  Ra = { class: "snum" },
  ja = { class: "snum" },
  Pa = { key: 0, class: "muted", style: { "margin-top": "10px" } },
  Fa = { class: "quick-actions" },
  La = { class: "ico" },
  Na = { class: "ico" },
  Va = { class: "ico" },
  Da = { class: "ico" },
  Ha = { class: "card", style: { "margin-top": "0" } },
  Ua = { key: 0, class: "empty" },
  Ka = { class: "ico" },
  qa = { class: "score" },
  Ba = {
    __name: "Overview",
    emits: ["go"],
    setup(e) {
      const t = ne(null),
        s = q(() => t.value?.analyst || { tasks: {}, generation: 0 }),
        n = q(() => {
          if (!t.value) return [];
          const r = t.value.corpus;
          return [
            {
              label: "Papers in corpus",
              value: r.papers,
              icon: "file",
              color: "",
              go: "search",
              sub: r.papers_cited_external
                ? `+${r.papers_cited_external} cited externally`
                : "",
            },
            {
              label: "Methods",
              value: r.methods,
              icon: "flask",
              color: "cyan",
              go: "agent",
            },
            { label: "Claims", value: r.claims, icon: "pulse", color: "green" },
            {
              label: "Datasets",
              value: r.datasets,
              icon: "database",
              color: "amber",
            },
            {
              label: "Authors",
              value: r.authors,
              icon: "users",
              color: "purple",
            },
            {
              label: "Insights banked",
              value: t.value.insights.total,
              icon: "bulb",
              color: "green",
              go: "insights",
              sub: `${t.value.insights.real} from real reasoning`,
            },
          ];
        }),
        i = q(() => {
          const r = t.value?.insights.by_kind || {},
            a = Math.max(1, ...Object.values(r));
          return Object.entries(r)
            .sort((c, d) => d[1] - c[1])
            .map(([c, d]) => ({
              name: c,
              count: d,
              pct: Math.round((d / a) * 100),
            }));
        }),
        o = q(() =>
          s.value.running
            ? s.value.paused
              ? "paused"
              : ["analyzing", "growing"].includes(s.value.phase)
                ? "busy"
                : "live"
            : "",
        ),
        l = q(() =>
          s.value.running
            ? s.value.paused
              ? "paused"
              : {
                  analyzing: "analyzing",
                  growing: "fetching papers",
                  sleeping: "waiting for next generation",
                  idle: "idle",
                }[s.value.phase] || s.value.phase
            : "stopped",
        );
      return (
        xt(async () => {
          t.value = await sa();
        }),
        (r, a) => (
          g(),
          m("div", null, [
            t.value
              ? (g(),
                m(
                  V,
                  { key: 1 },
                  [
                    u("div", ca, [
                      (g(!0),
                      m(
                        V,
                        null,
                        oe(
                          n.value,
                          (c) => (
                            g(),
                            m(
                              "button",
                              {
                                key: c.label,
                                class: "stat-card",
                                onClick: (d) => c.go && r.$emit("go", c.go),
                              },
                              [
                                u(
                                  "span",
                                  { class: ue(["ico", c.color]) },
                                  [J(et, { name: c.icon }, null, 8, ["name"])],
                                  2,
                                ),
                                u("div", da, v(c.value), 1),
                                u("div", pa, v(c.label), 1),
                                c.sub
                                  ? (g(), m("div", ha, v(c.sub), 1))
                                  : j("", !0),
                              ],
                              8,
                              fa,
                            )
                          ),
                        ),
                        128,
                      )),
                    ]),
                    u("div", ga, [
                      u("div", va, [
                        a[8] ||
                          (a[8] = u("h3", null, "Insight distribution", -1)),
                        t.value.insights.total
                          ? (g(),
                            m("div", ya, [
                              (g(!0),
                              m(
                                V,
                                null,
                                oe(
                                  i.value,
                                  (c) => (
                                    g(),
                                    m(
                                      "div",
                                      { key: c.name, class: "bar-row" },
                                      [
                                        u("span", _a, [
                                          u(
                                            "span",
                                            {
                                              class: ue([
                                                "tag",
                                                `tag--${c.name}`,
                                              ]),
                                            },
                                            v(c.name),
                                            3,
                                          ),
                                        ]),
                                        u("span", ba, [
                                          u(
                                            "span",
                                            {
                                              class: ue(["bar-fill", c.name]),
                                              style: $s({ width: c.pct + "%" }),
                                            },
                                            null,
                                            6,
                                          ),
                                        ]),
                                        u("span", wa, v(c.count), 1),
                                      ],
                                    )
                                  ),
                                ),
                                128,
                              )),
                            ]))
                          : (g(),
                            m(
                              "div",
                              ma,
                              " No insights yet — start the analyst to begin banking findings. ",
                            )),
                        t.value.insights.total
                          ? (g(),
                            m("div", $a, [
                              a[7] ||
                                (a[7] = u(
                                  "span",
                                  { class: "muted" },
                                  "confidence",
                                  -1,
                                )),
                              u(
                                "span",
                                xa,
                                v(t.value.insights.by_confidence.high || 0) +
                                  " high",
                                1,
                              ),
                              u(
                                "span",
                                ka,
                                v(t.value.insights.by_confidence.medium || 0) +
                                  " medium",
                                1,
                              ),
                              u(
                                "span",
                                Ca,
                                v(t.value.insights.by_confidence.low || 0) +
                                  " low",
                                1,
                              ),
                              u(
                                "span",
                                Sa,
                                "· " +
                                  v(t.value.insights.real) +
                                  " real / " +
                                  v(t.value.insights.stub) +
                                  " stub",
                                1,
                              ),
                            ]))
                          : j("", !0),
                      ]),
                      u("div", Ma, [
                        a[11] ||
                          (a[11] = u("h3", null, "Autonomous analyst", -1)),
                        u("div", Ta, [
                          u("span", { class: ue(["dot", o.value]) }, null, 2),
                          u("strong", null, v(l.value), 1),
                          u(
                            "span",
                            Aa,
                            "generation " + v(s.value.generation),
                            1,
                          ),
                        ]),
                        u("div", Oa, [
                          u("div", null, [
                            u("span", Ia, v(s.value.tasks.done), 1),
                            u(
                              "span",
                              Ea,
                              "/ " + v(s.value.tasks.total) + " tasks",
                              1,
                            ),
                          ]),
                          u("div", null, [
                            u("span", Ra, v(s.value.tasks.pending), 1),
                            a[9] ||
                              (a[9] = u(
                                "span",
                                { class: "muted" },
                                "pending",
                                -1,
                              )),
                          ]),
                          u("div", null, [
                            u("span", ja, v(s.value.insights_banked), 1),
                            a[10] ||
                              (a[10] = u(
                                "span",
                                { class: "muted" },
                                "banked",
                                -1,
                              )),
                          ]),
                        ]),
                        s.value.next_up?.length
                          ? (g(),
                            m(
                              "div",
                              Pa,
                              " next up: " +
                                v(s.value.next_up.slice(0, 3).join(", ")),
                              1,
                            ))
                          : j("", !0),
                        u(
                          "button",
                          {
                            class: "ghost",
                            style: { "margin-top": "14px" },
                            onClick:
                              a[0] || (a[0] = (c) => r.$emit("go", "analyst")),
                          },
                          " Open analyst control → ",
                        ),
                      ]),
                    ]),
                    a[17] ||
                      (a[17] = u(
                        "div",
                        { class: "section-title" },
                        "Quick actions",
                        -1,
                      )),
                    u("div", Fa, [
                      u(
                        "button",
                        {
                          class: "action",
                          onClick:
                            a[1] || (a[1] = (c) => r.$emit("go", "search")),
                        },
                        [
                          u("span", La, [J(et, { name: "search" })]),
                          a[12] ||
                            (a[12] = u(
                              "span",
                              null,
                              [
                                u("span", { class: "at" }, "Search the corpus"),
                                u(
                                  "span",
                                  { class: "ad" },
                                  "semantic paper search (L4)",
                                ),
                              ],
                              -1,
                            )),
                        ],
                      ),
                      u(
                        "button",
                        {
                          class: "action",
                          onClick:
                            a[2] ||
                            (a[2] = (c) => r.$emit("go", "investigate")),
                        },
                        [
                          u("span", Na, [J(et, { name: "network" })]),
                          a[13] ||
                            (a[13] = u(
                              "span",
                              null,
                              [
                                u(
                                  "span",
                                  { class: "at" },
                                  "Investigate a topic",
                                ),
                                u(
                                  "span",
                                  { class: "ad" },
                                  "all agents + cross-validation (L6)",
                                ),
                              ],
                              -1,
                            )),
                        ],
                      ),
                      u(
                        "button",
                        {
                          class: "action",
                          onClick:
                            a[3] || (a[3] = (c) => r.$emit("go", "insights")),
                        },
                        [
                          u("span", Va, [J(et, { name: "bulb" })]),
                          a[14] ||
                            (a[14] = u(
                              "span",
                              null,
                              [
                                u("span", { class: "at" }, "Browse insights"),
                                u(
                                  "span",
                                  { class: "ad" },
                                  "ranked analyst findings",
                                ),
                              ],
                              -1,
                            )),
                        ],
                      ),
                      u(
                        "button",
                        {
                          class: "action",
                          onClick:
                            a[4] || (a[4] = (c) => r.$emit("go", "analyst")),
                        },
                        [
                          u("span", Da, [J(et, { name: "bot" })]),
                          a[15] ||
                            (a[15] = u(
                              "span",
                              null,
                              [
                                u("span", { class: "at" }, "Run the analyst"),
                                u(
                                  "span",
                                  { class: "ad" },
                                  "grow the corpus, find more",
                                ),
                              ],
                              -1,
                            )),
                        ],
                      ),
                    ]),
                    a[18] ||
                      (a[18] = u(
                        "div",
                        { class: "section-title" },
                        "Top insights",
                        -1,
                      )),
                    u("div", Ha, [
                      t.value.insights.top.length
                        ? j("", !0)
                        : (g(),
                          m("div", Ua, [
                            u("span", Ka, [J(et, { name: "bulb" })]),
                            a[16] ||
                              (a[16] = O(
                                " Nothing banked yet. The analyst surfaces insights as it works the corpus. ",
                                -1,
                              )),
                          ])),
                      (g(!0),
                      m(
                        V,
                        null,
                        oe(
                          t.value.insights.top,
                          (c) => (
                            g(),
                            m(
                              "div",
                              {
                                key: c.id,
                                class: "row link-row",
                                onClick:
                                  a[5] ||
                                  (a[5] = (d) => r.$emit("go", "insights")),
                              },
                              [
                                u("span", qa, "score " + v(c._score), 1),
                                u(
                                  "span",
                                  { class: ue(["tag", `tag--${c.kind}`]) },
                                  v(c.kind),
                                  3,
                                ),
                                u(
                                  "span",
                                  {
                                    class: ue([
                                      "tag",
                                      `tag--conf-${c.confidence}`,
                                    ]),
                                  },
                                  v(c.confidence),
                                  3,
                                ),
                                O(" " + v(c.summary), 1),
                              ],
                            )
                          ),
                        ),
                        128,
                      )),
                    ]),
                  ],
                  64,
                ))
              : (g(),
                m("div", ua, [
                  (g(),
                  m(
                    V,
                    null,
                    oe(6, (c) =>
                      u("div", { key: c, class: "stat-card" }, [
                        ...(a[6] ||
                          (a[6] = [
                            u(
                              "div",
                              { class: "skeleton", style: { width: "40%" } },
                              null,
                              -1,
                            ),
                            u(
                              "div",
                              {
                                class: "skeleton",
                                style: { width: "70%", height: "24px" },
                              },
                              null,
                              -1,
                            ),
                          ])),
                      ]),
                    ),
                    64,
                  )),
                ])),
          ])
        )
      );
    },
  },
  Wa = Qe(Ba, [["__scopeId", "data-v-f0c9cc68"]]),
  za = { key: 0, class: "card" },
  Ja = { key: 1, class: "card" },
  Ga = { key: 0, class: "muted" },
  Ya = {
    key: 0,
    class: "score",
    title: "Fully extracted into the knowledge graph",
  },
  Qa = ["title", "onClick"],
  Xa = { class: "muted" },
  Za = { key: 1, class: "muted authors" },
  eu = { class: "muted snippet" },
  tu = { class: "chip-row" },
  su = ["onClick"],
  nu = ["onClick"],
  iu = { key: 2 },
  ou = { class: "card" },
  lu = { class: "muted", style: { "font-weight": "500" } },
  ru = { key: 0, class: "muted" },
  au = { class: "tag-cloud" },
  uu = ["onClick"],
  cu = { class: "topic-n" },
  fu = { key: 0, class: "card" },
  du = { class: "tag-cloud" },
  pu = ["onClick"],
  hu = {
    __name: "BrowseCorpus",
    props: { view: String },
    emits: ["open"],
    setup(e) {
      const t = e,
        s = ne(null),
        n = q(() => ["search", "related", "citations"].includes(t.view)),
        i = q(() => ["agent", "investigate"].includes(t.view)),
        o = q(() => (t.view === "citations" ? "citations" : "related")),
        l = q(() =>
          t.view === "citations" ? "Trace citations" : "Find related work",
        ),
        r = q(() =>
          t.view === "investigate" ? "investigate it" : "run the agent on it",
        );
      return (
        xt(async () => {
          s.value = await na();
        }),
        (a, c) => (
          g(),
          m("div", null, [
            s.value
              ? n.value
                ? (g(),
                  m("div", Ja, [
                    u("h3", null, [
                      O(
                        v(s.value.counts.papers) +
                          " paper(s) already digested ",
                        1,
                      ),
                      c[1] ||
                        (c[1] = u(
                          "span",
                          { class: "muted", style: { "font-weight": "500" } },
                          "· pick one or search above",
                          -1,
                        )),
                    ]),
                    s.value.papers.length
                      ? j("", !0)
                      : (g(),
                        m("div", Ga, [
                          ...(c[2] ||
                            (c[2] = [
                              O(" No papers ingested yet. Run ", -1),
                              u(
                                "code",
                                null,
                                "python -m pipeline --ingest 2",
                                -1,
                              ),
                              O(" or grow from the Analyst tab. ", -1),
                            ])),
                        ])),
                    (g(!0),
                    m(
                      V,
                      null,
                      oe(
                        s.value.papers,
                        (d) => (
                          g(),
                          m("div", { key: d.paper_id, class: "row" }, [
                            d.extracted
                              ? (g(), m("span", Ya, "digested"))
                              : j("", !0),
                            u(
                              "strong",
                              {
                                class: "link",
                                title: l.value,
                                onClick: (h) =>
                                  a.$emit("open", {
                                    view: o.value,
                                    query: d.paper_id,
                                  }),
                              },
                              v(d.title),
                              9,
                              Qa,
                            ),
                            u("div", Xa, [
                              u("code", null, v(d.paper_id), 1),
                              d.year
                                ? (g(),
                                  m(
                                    V,
                                    { key: 0 },
                                    [O(" · " + v(d.year), 1)],
                                    64,
                                  ))
                                : j("", !0),
                              d.categories.length
                                ? (g(),
                                  m(
                                    V,
                                    { key: 1 },
                                    [O(" · " + v(d.categories.join(", ")), 1)],
                                    64,
                                  ))
                                : j("", !0),
                            ]),
                            d.authors.length
                              ? (g(),
                                m("div", Za, [
                                  O(v(d.authors.join(", ")), 1),
                                  d.authors.length >= 4
                                    ? (g(), m(V, { key: 0 }, [O(" …")], 64))
                                    : j("", !0),
                                ]))
                              : j("", !0),
                            u("div", eu, [
                              O(v(d.snippet), 1),
                              d.snippet.length >= 220
                                ? (g(), m(V, { key: 0 }, [O("…")], 64))
                                : j("", !0),
                            ]),
                            u("div", tu, [
                              u(
                                "span",
                                {
                                  class: "link",
                                  onClick: (h) =>
                                    a.$emit("open", {
                                      view: "related",
                                      query: d.paper_id,
                                    }),
                                },
                                "→ related work",
                                8,
                                su,
                              ),
                              u(
                                "span",
                                {
                                  class: "link",
                                  onClick: (h) =>
                                    a.$emit("open", {
                                      view: "citations",
                                      query: d.paper_id,
                                    }),
                                },
                                "→ citations",
                                8,
                                nu,
                              ),
                            ]),
                          ])
                        ),
                      ),
                      128,
                    )),
                  ]))
                : i.value
                  ? (g(),
                    m("div", iu, [
                      u("div", ou, [
                        u("h3", null, [
                          O(
                            v(s.value.counts.methods) +
                              " method(s) the corpus is about ",
                            1,
                          ),
                          u("span", lu, "· click one to " + v(r.value), 1),
                        ]),
                        s.value.methods.length
                          ? j("", !0)
                          : (g(),
                            m("div", ru, [
                              ...(c[3] ||
                                (c[3] = [
                                  O(
                                    " No methods in the graph yet. Build it with ",
                                    -1,
                                  ),
                                  u("code", null, "python -m pipeline", -1),
                                  O(". ", -1),
                                ])),
                            ])),
                        u("div", au, [
                          (g(!0),
                          m(
                            V,
                            null,
                            oe(
                              s.value.methods,
                              (d) => (
                                g(),
                                m(
                                  "button",
                                  {
                                    key: d.label,
                                    class: "topic",
                                    onClick: (h) =>
                                      a.$emit("open", {
                                        view: e.view,
                                        query: d.label,
                                      }),
                                  },
                                  [
                                    O(v(d.label) + " ", 1),
                                    u("span", cu, v(d.papers), 1),
                                  ],
                                  8,
                                  uu,
                                )
                              ),
                            ),
                            128,
                          )),
                        ]),
                      ]),
                      s.value.datasets.length
                        ? (g(),
                          m("div", fu, [
                            u("h3", null, [
                              O(
                                v(s.value.counts.datasets) +
                                  " dataset(s) seen in the corpus ",
                                1,
                              ),
                              c[4] ||
                                (c[4] = u(
                                  "span",
                                  {
                                    class: "muted",
                                    style: { "font-weight": "500" },
                                  },
                                  "· also valid topics",
                                  -1,
                                )),
                            ]),
                            u("div", du, [
                              (g(!0),
                              m(
                                V,
                                null,
                                oe(
                                  s.value.datasets,
                                  (d) => (
                                    g(),
                                    m(
                                      "button",
                                      {
                                        key: d.label,
                                        class: "topic subtle",
                                        onClick: (h) =>
                                          a.$emit("open", {
                                            view: e.view,
                                            query: d.label,
                                          }),
                                      },
                                      v(d.label),
                                      9,
                                      pu,
                                    )
                                  ),
                                ),
                                128,
                              )),
                            ]),
                          ]))
                        : j("", !0),
                    ]))
                  : j("", !0)
              : (g(),
                m("div", za, [
                  ...(c[0] ||
                    (c[0] = [
                      u(
                        "div",
                        { class: "skeleton", style: { width: "35%" } },
                        null,
                        -1,
                      ),
                      u(
                        "div",
                        { class: "skeleton", style: { width: "90%" } },
                        null,
                        -1,
                      ),
                      u(
                        "div",
                        { class: "skeleton", style: { width: "70%" } },
                        null,
                        -1,
                      ),
                    ])),
                ])),
          ])
        )
      );
    },
  },
  gu = Qe(hu, [["__scopeId", "data-v-c45964f1"]]),
  vu = { class: "controls" },
  mu = ["placeholder"],
  yu = ["disabled"],
  _u = { class: "hint" },
  bu = {
    __name: "ControlPanel",
    props: { mode: String, agent: String, query: String, loading: Boolean },
    emits: ["update:agent", "update:query", "run"],
    setup(e, { emit: t }) {
      const s = e,
        n = t,
        i = q({ get: () => s.agent, set: (d) => n("update:agent", d) }),
        o = q({ get: () => s.query, set: (d) => n("update:query", d) }),
        l = {
          search: "Free-text query, e.g. 'chain of thought reasoning'",
          related: "A paper id, e.g. 'arxiv:2606.11189v1'",
          citations: "A paper id, e.g. 'semantic_scholar:1b6e8…'",
          agent: "Topic for the agent (blank scans the whole corpus)",
          investigate: "A topic/proposition, e.g. 'supervised fine-tuning'",
        },
        r = {
          search:
            "Ranks papers by semantic similarity of their title + abstract (Layer 4). Click any result to jump to its related work or citations.",
          related:
            "Surfaces similar papers, what it cites, and papers sharing a method (Layer 4).",
          citations:
            "Walks the outgoing citation graph; out-of-corpus citations come back flagged as stubs (Layer 4).",
          agent:
            "Runs one analytical agent over the corpus and returns structured findings (Layer 5).",
          investigate:
            "Runs every agent on the topic, then cross-validates their findings (Layer 6 A2A).",
        },
        a = q(() => l[s.mode] || "query…"),
        c = q(() => r[s.mode] || "");
      return (d, h) => (
        g(),
        m("div", null, [
          u("div", vu, [
            e.mode === "agent"
              ? Ve(
                  (g(),
                  m(
                    "select",
                    {
                      key: 0,
                      "onUpdate:modelValue":
                        h[0] || (h[0] = (_) => (i.value = _)),
                    },
                    [
                      ...(h[4] ||
                        (h[4] = [
                          u(
                            "option",
                            { value: "contradiction" },
                            "contradiction",
                            -1,
                          ),
                          u("option", { value: "synergy" }, "synergy", -1),
                          u("option", { value: "gap" }, "gap", -1),
                          u("option", { value: "evidence" }, "evidence", -1),
                        ])),
                    ],
                    512,
                  )),
                  [[tn, i.value]],
                )
              : j("", !0),
            Ve(
              u(
                "input",
                {
                  "onUpdate:modelValue": h[1] || (h[1] = (_) => (o.value = _)),
                  placeholder: a.value,
                  onKeydown:
                    h[2] || (h[2] = Vr((_) => d.$emit("run"), ["enter"])),
                },
                null,
                40,
                mu,
              ),
              [[ct, o.value]],
            ),
            u(
              "button",
              {
                disabled: e.loading,
                onClick: h[3] || (h[3] = (_) => d.$emit("run")),
              },
              v(e.loading ? "Running…" : "Run"),
              9,
              yu,
            ),
          ]),
          u("div", _u, v(c.value), 1),
        ])
      );
    },
  },
  wu = { class: "jv-key" },
  $u = ["open"],
  xu = { class: "jv-key" },
  ku = { class: "jv-meta" },
  Cu = {
    __name: "JsonView",
    props: { data: { default: null }, depth: { type: Number, default: 0 } },
    setup(e) {
      const t = e,
        s = q(() => Array.isArray(t.data)),
        n = q(() => t.data !== null && typeof t.data == "object");
      function i(c) {
        return c !== null && typeof c == "object";
      }
      function o(c) {
        return Array.isArray(c)
          ? c.length
            ? `[${c.length}]`
            : "[ ]"
          : Object.keys(c).length
            ? `{${Object.keys(c).length}}`
            : "{ }";
      }
      const l = q(() =>
          n.value
            ? (s.value
                ? t.data.map((d, h) => [String(h), d])
                : Object.entries(t.data)
              ).map(([d, h]) => ({
                key: d,
                value: h,
                container:
                  i(h) && (Array.isArray(h) ? h.length : Object.keys(h).length),
                meta: i(h) ? o(h) : "",
              }))
            : [],
        ),
        r = q(() => {
          const c = t.data;
          return c === null
            ? "jv-null"
            : typeof c == "boolean"
              ? "jv-bool"
              : typeof c == "number"
                ? "jv-num"
                : Array.isArray(c) || typeof c == "object"
                  ? "jv-empty"
                  : "jv-str";
        }),
        a = q(() => {
          const c = t.data;
          return c === null
            ? "null"
            : Array.isArray(c)
              ? "[ ]"
              : typeof c == "object"
                ? "{ }"
                : typeof c == "string"
                  ? c === ""
                    ? '""'
                    : c
                  : String(c);
        });
      return (c, d) => {
        const h = xl("JsonView", !0);
        return n.value
          ? (g(),
            m(
              "ul",
              { key: 1, class: ue(["jv", { root: e.depth === 0 }]) },
              [
                (g(!0),
                m(
                  V,
                  null,
                  oe(
                    l.value,
                    (_) => (
                      g(),
                      m("li", { key: _.key, class: "jv-row" }, [
                        _.container
                          ? (g(),
                            m(
                              "details",
                              { key: 1, open: e.depth < 1 },
                              [
                                u("summary", null, [
                                  u("span", xu, v(_.key), 1),
                                  u("span", ku, v(_.meta), 1),
                                ]),
                                J(
                                  h,
                                  { data: _.value, depth: e.depth + 1 },
                                  null,
                                  8,
                                  ["data", "depth"],
                                ),
                              ],
                              8,
                              $u,
                            ))
                          : (g(),
                            m(
                              V,
                              { key: 0 },
                              [
                                u("span", wu, v(_.key), 1),
                                d[0] ||
                                  (d[0] = u(
                                    "span",
                                    { class: "jv-colon" },
                                    ":",
                                    -1,
                                  )),
                                J(h, { data: _.value }, null, 8, ["data"]),
                              ],
                              64,
                            )),
                      ])
                    ),
                  ),
                  128,
                )),
              ],
              2,
            ))
          : (g(),
            m(
              "span",
              { key: 0, class: ue(["jv-val", r.value]) },
              v(a.value),
              3,
            ));
      };
    },
  },
  Su = Qe(Cu, [["__scopeId", "data-v-44e15ef3"]]),
  Mu = { class: "json-disclosure" },
  Tu = { class: "json-panel" },
  Au = ["title"],
  Ou = { class: "jv-wrap" },
  Iu = {
    __name: "RawJson",
    props: { data: Object },
    setup(e) {
      const t = e,
        s = ne(!1);
      async function n() {
        try {
          (await navigator.clipboard.writeText(JSON.stringify(t.data, null, 2)),
            (s.value = !0),
            setTimeout(() => (s.value = !1), 1400));
        } catch {
          s.value = !1;
        }
      }
      return (i, o) => (
        g(),
        m("details", Mu, [
          o[0] || (o[0] = u("summary", null, " inspect data ", -1)),
          u("div", Tu, [
            u(
              "button",
              {
                class: "copy",
                title: s.value ? "Copied!" : "Copy JSON",
                onClick: Lr(n, ["stop"]),
              },
              v(s.value ? "copied ✓" : "copy"),
              9,
              Au,
            ),
            u("div", Ou, [J(Su, { data: e.data }, null, 8, ["data"])]),
          ]),
        ])
      );
    },
  },
  Jt = Qe(Iu, [["__scopeId", "data-v-1a3f4992"]]),
  Eu = { class: "card" },
  Ru = { key: 0, class: "muted" },
  ju = { class: "score" },
  Pu = ["onClick"],
  Fu = { class: "muted" },
  Lu = { class: "muted snippet" },
  Nu = { class: "chip-row" },
  Vu = ["onClick"],
  Du = ["onClick"],
  Hu = {
    __name: "SearchResults",
    props: { data: Object },
    emits: ["open"],
    setup(e) {
      return (t, s) => (
        g(),
        m("div", Eu, [
          u(
            "h3",
            null,
            v(e.data.count) + " paper(s) · match: " + v(e.data.match),
            1,
          ),
          e.data.results?.length
            ? j("", !0)
            : (g(), m("div", Ru, " No papers matched. Try a broader query. ")),
          (g(!0),
          m(
            V,
            null,
            oe(
              e.data.results,
              (n) => (
                g(),
                m("div", { key: n.paper_id, class: "row" }, [
                  u("span", ju, v(n.score), 1),
                  u(
                    "strong",
                    {
                      class: "link",
                      title: "Find related work",
                      onClick: (i) =>
                        t.$emit("open", { view: "related", query: n.paper_id }),
                    },
                    v(n.title),
                    9,
                    Pu,
                  ),
                  u("div", Fu, [
                    u("code", null, v(n.paper_id), 1),
                    (n.categories || []).length
                      ? (g(),
                        m(
                          V,
                          { key: 0 },
                          [O(" · " + v((n.categories || []).join(", ")), 1)],
                          64,
                        ))
                      : j("", !0),
                    n.year
                      ? (g(), m(V, { key: 1 }, [O(" · " + v(n.year), 1)], 64))
                      : j("", !0),
                  ]),
                  u("div", Lu, v(n.snippet), 1),
                  u("div", Nu, [
                    u(
                      "span",
                      {
                        class: "link",
                        onClick: (i) =>
                          t.$emit("open", {
                            view: "related",
                            query: n.paper_id,
                          }),
                      },
                      "→ related work",
                      8,
                      Vu,
                    ),
                    u(
                      "span",
                      {
                        class: "link",
                        onClick: (i) =>
                          t.$emit("open", {
                            view: "citations",
                            query: n.paper_id,
                          }),
                      },
                      "→ citations",
                      8,
                      Du,
                    ),
                  ]),
                ])
              ),
            ),
            128,
          )),
          J(Jt, { data: e.data }, null, 8, ["data"]),
        ])
      );
    },
  },
  Uu = Qe(Hu, [["__scopeId", "data-v-a73eaf72"]]),
  Ku = { class: "card head-card" },
  qu = { class: "muted" },
  Bu = { class: "card" },
  Wu = { key: 0, class: "muted" },
  zu = { class: "score" },
  Ju = ["onClick"],
  Gu = { class: "muted" },
  Yu = { class: "chip-row" },
  Qu = ["onClick"],
  Xu = { class: "card" },
  Zu = { key: 0, class: "muted" },
  ec = { key: 0, class: "tag stub" },
  tc = ["onClick"],
  sc = { key: 2 },
  nc = { class: "muted" },
  ic = { class: "card" },
  oc = { key: 0, class: "muted" },
  lc = ["onClick"],
  rc = { class: "muted" },
  ac = { class: "tag" },
  uc = { class: "muted" },
  cc = {
    __name: "RelatedWork",
    props: { data: Object },
    emits: ["open"],
    setup(e) {
      const t = e,
        s = q(() => t.data.semantically_similar || []),
        n = q(() => t.data.cites || []),
        i = q(() => t.data.shares_methods || []);
      return (o, l) => (
        g(),
        m("div", null, [
          u("div", Ku, [
            l[1] || (l[1] = u("h3", null, "Related work", -1)),
            u("div", qu, [
              l[0] || (l[0] = O(" for ", -1)),
              u("code", null, v(e.data.paper_id), 1),
              O(" · match: " + v(e.data.match), 1),
            ]),
          ]),
          u("div", Bu, [
            u("h3", null, "Similar papers · " + v(s.value.length), 1),
            s.value.length
              ? j("", !0)
              : (g(), m("div", Wu, " No semantically similar papers found. ")),
            (g(!0),
            m(
              V,
              null,
              oe(
                s.value,
                (r) => (
                  g(),
                  m("div", { key: r.paper_id, class: "row" }, [
                    u("span", zu, v(r.score), 1),
                    u(
                      "strong",
                      {
                        class: "link",
                        title: "Find related work for this paper",
                        onClick: (a) =>
                          o.$emit("open", {
                            view: "related",
                            query: r.paper_id,
                          }),
                      },
                      v(r.title || r.paper_id),
                      9,
                      Ju,
                    ),
                    u("div", Gu, [u("code", null, v(r.paper_id), 1)]),
                    u("div", Yu, [
                      u(
                        "span",
                        {
                          class: "link",
                          onClick: (a) =>
                            o.$emit("open", {
                              view: "citations",
                              query: r.paper_id,
                            }),
                        },
                        "→ citations",
                        8,
                        Qu,
                      ),
                    ]),
                  ])
                ),
              ),
              128,
            )),
          ]),
          u("div", Xu, [
            u("h3", null, "Cites · " + v(n.value.length), 1),
            n.value.length
              ? j("", !0)
              : (g(),
                m(
                  "div",
                  Zu,
                  " No in-corpus citations recorded for this paper. ",
                )),
            (g(!0),
            m(
              V,
              null,
              oe(
                n.value,
                (r) => (
                  g(),
                  m("div", { key: r.paper_id, class: "row" }, [
                    r.stub ? (g(), m("span", ec, "external")) : j("", !0),
                    r.stub
                      ? (g(), m("strong", sc, v(r.title || r.paper_id), 1))
                      : (g(),
                        m(
                          "strong",
                          {
                            key: 1,
                            class: "link",
                            onClick: (a) =>
                              o.$emit("open", {
                                view: "related",
                                query: r.paper_id,
                              }),
                          },
                          v(r.title || r.paper_id),
                          9,
                          tc,
                        )),
                    u("div", nc, [u("code", null, v(r.paper_id), 1)]),
                  ])
                ),
              ),
              128,
            )),
          ]),
          u("div", ic, [
            u("h3", null, "Shares methods · " + v(i.value.length), 1),
            i.value.length
              ? j("", !0)
              : (g(),
                m(
                  "div",
                  oc,
                  " No other paper shares a method with this one yet. ",
                )),
            (g(!0),
            m(
              V,
              null,
              oe(
                i.value,
                (r, a) => (
                  g(),
                  m("div", { key: a, class: "row" }, [
                    u(
                      "strong",
                      {
                        class: "link",
                        onClick: (c) =>
                          o.$emit("open", {
                            view: "related",
                            query: r.paper_id,
                          }),
                      },
                      v(r.title || r.paper_id),
                      9,
                      lc,
                    ),
                    u("div", rc, [
                      l[2] || (l[2] = O(" via ", -1)),
                      u("span", ac, v(r.via_method), 1),
                      r.relation
                        ? (g(),
                          m(V, { key: 0 }, [O("· " + v(r.relation), 1)], 64))
                        : j("", !0),
                    ]),
                    u("div", uc, [u("code", null, v(r.paper_id), 1)]),
                  ])
                ),
              ),
              128,
            )),
          ]),
          J(Jt, { data: e.data }, null, 8, ["data"]),
        ])
      );
    },
  },
  fc = Qe(cc, [["__scopeId", "data-v-29189670"]]),
  dc = { class: "card head-card" },
  pc = { class: "muted" },
  hc = { class: "card" },
  gc = { key: 0, class: "empty" },
  vc = { class: "section-title" },
  mc = { key: 0, class: "tag stub" },
  yc = ["onClick"],
  _c = { key: 2 },
  bc = { class: "muted" },
  wc = {
    __name: "Citations",
    props: { data: Object },
    emits: ["open"],
    setup(e) {
      const t = e,
        s = (l) => (l || "").replace(/^paper:/, ""),
        n = q(() => s(t.data.root) || "(unresolved)"),
        i = q(() => t.data.edges || []),
        o = q(() => {
          const l = new Map();
          for (const r of i.value) {
            const a = r.hop ?? 1;
            (l.has(a) || l.set(a, []), l.get(a).push(r));
          }
          return [...l.entries()]
            .sort((r, a) => r[0] - a[0])
            .map(([r, a]) => ({ level: r, edges: a }));
        });
      return (l, r) => (
        g(),
        m("div", null, [
          u("div", dc, [
            r[1] || (r[1] = u("h3", null, "Citation graph", -1)),
            u("div", pc, [
              r[0] || (r[0] = O(" from ", -1)),
              u("code", null, v(n.value), 1),
              O(
                " · depth " +
                  v(e.data.depth) +
                  " · " +
                  v(e.data.resolved_count) +
                  " in-corpus / " +
                  v(e.data.stub_count) +
                  " external ",
                1,
              ),
            ]),
          ]),
          u("div", hc, [
            u("h3", null, v(i.value.length) + " citation edge(s)", 1),
            i.value.length
              ? (g(!0),
                m(
                  V,
                  { key: 1 },
                  oe(
                    o.value,
                    (a) => (
                      g(),
                      m("div", { key: a.level }, [
                        u("div", vc, "hop " + v(a.level), 1),
                        (g(!0),
                        m(
                          V,
                          null,
                          oe(
                            a.edges,
                            (c, d) => (
                              g(),
                              m("div", { key: d, class: "row" }, [
                                c.stub
                                  ? (g(), m("span", mc, "external"))
                                  : j("", !0),
                                c.stub
                                  ? (g(),
                                    m(
                                      "strong",
                                      _c,
                                      v(c.to_label || s(c.to)),
                                      1,
                                    ))
                                  : (g(),
                                    m(
                                      "strong",
                                      {
                                        key: 1,
                                        class: "link",
                                        title:
                                          "Find related work for this paper",
                                        onClick: (h) =>
                                          l.$emit("open", {
                                            view: "related",
                                            query: s(c.to),
                                          }),
                                      },
                                      v(c.to_label || s(c.to)),
                                      9,
                                      yc,
                                    )),
                                u("div", bc, [
                                  u("code", null, v(s(c.from)), 1),
                                  r[3] || (r[3] = O(" → ", -1)),
                                  u("code", null, v(s(c.to)), 1),
                                ]),
                              ])
                            ),
                          ),
                          128,
                        )),
                      ])
                    ),
                  ),
                  128,
                ))
              : (g(),
                m("div", gc, [
                  ...(r[2] ||
                    (r[2] = [
                      u(
                        "div",
                        null,
                        " No outgoing citations were recorded for this paper. ",
                        -1,
                      ),
                      u(
                        "div",
                        { class: "muted", style: { "margin-top": "6px" } },
                        [
                          O(
                            " Citation edges only exist when a paper's reference list was captured at ingest and the cited work is matched in the graph. Try a paper with a richer reference list, or a larger ",
                          ),
                          u("code", null, "depth"),
                          O(". "),
                        ],
                        -1,
                      ),
                    ])),
                ])),
          ]),
          J(Jt, { data: e.data }, null, 8, ["data"]),
        ])
      );
    },
  },
  $c = Qe(wc, [["__scopeId", "data-v-7cabc9b8"]]),
  xc = { class: "card" },
  kc = { key: 0, class: "tag stub" },
  Cc = { key: 1, class: "muted" },
  Sc = { key: 0, class: "muted" },
  fo = {
    __name: "FindingsList",
    props: { title: String, findings: { type: Array, default: () => [] } },
    setup(e) {
      return (t, s) => (
        g(),
        m("div", xc, [
          u(
            "h3",
            null,
            v(e.title) + ": " + v(e.findings.length) + " finding(s) ",
            1,
          ),
          (g(!0),
          m(
            V,
            null,
            oe(
              e.findings,
              (n) => (
                g(),
                m("div", { key: n.id || n.summary, class: "row" }, [
                  u(
                    "span",
                    { class: ue(["tag", `tag--${n.kind}`]) },
                    v(n.kind),
                    3,
                  ),
                  u(
                    "span",
                    { class: ue(["tag", `tag--conf-${n.confidence}`]) },
                    v(n.confidence),
                    3,
                  ),
                  n.stub ? (g(), m("span", kc, " stub ")) : j("", !0),
                  O(" " + v(n.summary) + " ", 1),
                  n.provenance?.length
                    ? (g(),
                      m(
                        "div",
                        Cc,
                        " provenance: " + v(n.provenance.join(", ")),
                        1,
                      ))
                    : j("", !0),
                ])
              ),
            ),
            128,
          )),
          e.findings.length
            ? j("", !0)
            : (g(), m("div", Sc, " (no findings) ")),
        ])
      );
    },
  },
  Mc = { class: "card" },
  Tc = { class: "card" },
  Ac = { class: "tag" },
  Oc = { class: "muted" },
  Ic = { key: 0, class: "muted" },
  Ec = {
    __name: "InvestigateReport",
    props: { report: Object },
    setup(e) {
      const t = e,
        s = q(() => t.report.cross_validations || []);
      return (n, i) => (
        g(),
        m("div", null, [
          u("div", Mc, [
            i[0] || (i[0] = u("h3", null, "A2A report", -1)),
            O(" " + v(e.report.summary), 1),
          ]),
          J(
            fo,
            { title: "Findings", findings: e.report.findings || [] },
            null,
            8,
            ["findings"],
          ),
          u("div", Tc, [
            u("h3", null, " Cross-validation links: " + v(s.value.length), 1),
            (g(!0),
            m(
              V,
              null,
              oe(
                s.value,
                (o, l) => (
                  g(),
                  m("div", { key: l, class: "row" }, [
                    u("span", Ac, v(o.type), 1),
                    O(v(o.note) + " ", 1),
                    u(
                      "div",
                      Oc,
                      " links: " + v((o.finding_ids || []).join(", ")),
                      1,
                    ),
                  ])
                ),
              ),
              128,
            )),
            s.value.length
              ? j("", !0)
              : (g(),
                m(
                  "div",
                  Ic,
                  " (agents' findings did not corroborate on this topic) ",
                )),
            J(Jt, { data: e.report }, null, 8, ["data"]),
          ]),
        ])
      );
    },
  },
  Rc = { high: 3, medium: 2, low: 1 };
function gt(e) {
  return Number.isInteger(e) ? `${e}` : `${Math.round(e * 100) / 100}`;
}
function jc(e) {
  return [
    ...new Set(
      (e || []).filter(
        (t) =>
          t &&
          !t.includes("#") &&
          !t.startsWith("method:") &&
          !t.startsWith("dataset:"),
      ),
    ),
  ];
}
function Pc(e) {
  return e >= 6 ? "high" : e >= 4 ? "moderate" : "low";
}
function Fc(e) {
  const t = (e.confidence || "low").toLowerCase(),
    s = Rc[t] ?? 1,
    n = jc(e.provenance),
    i = n.length * 0.5,
    o = e.stub ? 0 : 2,
    l = s + i + o,
    r = Number.isFinite(Number(e._score)) ? Number(e._score) : l;
  return {
    confidence: t,
    confidenceScore: s,
    papers: n,
    paperScore: i,
    realBonus: o,
    shown: r,
  };
}
function ri(e, t, s = 2) {
  return (e || [])
    .map((n) => n && n[t])
    .filter(Boolean)
    .slice(0, s);
}
function Lc(e, t) {
  return t.length
    ? `"${e}" is the research idea being evaluated. For a beginner, the easiest entry point is the paper claims: ${t.map((s) => `"${s}"`).join(" ")}`
    : `"${e}" is the research idea being evaluated. The analyst is checking whether the papers contain enough evidence to support or challenge it.`;
}
function Nc(e) {
  const t = e.details || {};
  if (e.kind === "evidence") {
    const s = t.topic || "this topic",
      n = ri(t.supporting, "statement");
    return Lc(s, n);
  }
  if (e.kind === "synergy") {
    const s = t.method_a || {},
      n = t.method_b || {},
      i = s.description
        ? `"${s.name}" means ${s.description}`
        : `"${s.name || "one method"}" is one technique in the corpus.`,
      o = n.description
        ? `"${n.name}" means ${n.description}`
        : `"${n.name || "another method"}" is another technique in the corpus.`;
    return `${i} ${o} The insight is about whether these two ideas could reinforce each other if combined.`;
  }
  if (e.kind === "contradiction") {
    const s = (t.claim_a || {}).statement,
      n = (t.claim_b || {}).statement;
    return s && n
      ? `This is about two paper claims that appear to pull in different directions: "${s}" versus "${n}".`
      : `This is about a possible disagreement between papers on "${t.topic || "the same topic"}".`;
  }
  if (e.kind === "gap") {
    const s = t.method || "the method",
      n = t.missing_dataset || "a dataset or benchmark";
    return `This is about evaluation coverage. The method "${s}" may not have been tested on "${n}", so we do not yet know how it behaves there.`;
  }
  if (e.kind === "hypothesis") {
    const s = ri(t.grounded_in, "statement", 1),
      n = `This is a suggested next experiment or research direction around "${t.topic || "this area"}".`;
    return s.length
      ? `${n} It is grounded in a related claim from the corpus: "${s[0]}".`
      : n;
  }
  return "This is an analyst-generated note about a research idea found in the paper corpus.";
}
function Vc(e) {
  const t = e.details || {};
  if (e.kind === "evidence") {
    const s = t.topic || "this topic",
      n = t.verdict || "unclear",
      i = (t.supporting || []).length,
      o = (t.contradicting || []).length,
      l = t.summary ? ` In short: ${t.summary}` : "";
    return `The analyst checked whether the papers support "${s}" and judged the evidence as ${n}. It found ${i} supporting claim(s) and ${o} contradicting claim(s).${l}`;
  }
  if (e.kind === "synergy") {
    const s = (t.method_a || {}).name || "one method",
      n = (t.method_b || {}).name || "another method",
      i = t.rationale ? ` ${t.rationale}` : "";
    return `The analyst thinks "${s}" and "${n}" could be useful together.${i}`;
  }
  if (e.kind === "contradiction") {
    const s = t.topic || "the topic",
      n = t.explanation ? ` ${t.explanation}` : "";
    return `The analyst found two claims that may disagree about "${s}".${n}`;
  }
  if (e.kind === "gap") {
    const s = t.method || "this method",
      n = t.missing_dataset || "a dataset",
      i = t.evaluated_by
        ? ` A peer method, "${t.evaluated_by}", was evaluated there.`
        : "";
    return `The analyst found a coverage gap: "${s}" does not appear to have been evaluated on "${n}".${i}`;
  }
  if (e.kind === "hypothesis") {
    const s = t.topic || "this area",
      n = t.rationale ? ` ${t.rationale}` : "";
    return `This is a proposed research direction for "${s}".${n}`;
  }
  return t.summary
    ? t.summary
    : e.summary || "No summary was recorded for this insight.";
}
function Dc(e, t) {
  const s = Pc(t.shown),
    n = t.papers.length
      ? `${t.papers.length} distinct source paper(s) add ${gt(t.paperScore)} point(s)`
      : "no distinct source-paper IDs add breadth points",
    i = e.stub
      ? "it came from the offline stub, so it gets no real-reasoning bonus"
      : "it came from the real reasoning path, adding 2 points";
  return `This is a ${s} score because confidence is ${t.confidence} (${gt(t.confidenceScore)} point(s)), ${n}, and ${i}.`;
}
const Hc = { class: "explain" },
  Uc = { class: "score-parts" },
  Kc = ["disabled"],
  qc = { key: 0, class: "muted" },
  Bc = { key: 1, class: "llm-result" },
  Wc = { class: "muted" },
  zc = { key: 0 },
  Jc = { key: 1, class: "terms" },
  Gc = { key: 0 },
  Yc = { key: 2, class: "muted" },
  Qc = {
    __name: "InsightExplanation",
    props: { insight: Object },
    setup(e) {
      const t = e,
        s = q(() => Fc(t.insight)),
        n = ne(!1),
        i = ne(""),
        o = ne(null),
        l = q(() => o.value?.explanation || {}),
        r = q(() =>
          typeof l.value.technical_terms == "string"
            ? l.value.technical_terms.trim()
            : "",
        ),
        a = q(() => {
          const h = l.value.technical_terms;
          if (!h || typeof h == "string") return [];
          const _ = (x) =>
            x && typeof x == "object"
              ? Object.entries(x).map(([K, E]) => ({
                  term: K,
                  def: typeof E == "string" ? E : JSON.stringify(E),
                }))
              : [{ term: "", def: String(x) }];
          return Array.isArray(h) ? h.flatMap(_) : _(h);
        }),
        c = [
          { key: "subject", label: "Subject" },
          { key: "why_it_matters", label: "Why It Matters" },
          { key: "insight", label: "The Insight" },
          { key: "evidence", label: "Evidence" },
          { key: "contradicting", label: "Contradicting Evidence" },
          { key: "caveats", label: "Caveats" },
          { key: "full_details", label: "full details" },
        ];
      async function d() {
        ((n.value = !0), (i.value = ""), (o.value = null));
        try {
          const h = await ta(t.insight.id);
          if (h.error) {
            i.value = `LLM explanation unavailable: ${h.error}`;
            return;
          }
          ((o.value = h),
            console.log("LLM explanation response:", h.explanation));
        } catch (h) {
          i.value = `LLM explanation failed: ${h}`;
        } finally {
          n.value = !1;
        }
      }
      return (h, _) => (
        g(),
        m("details", null, [
          _[4] || (_[4] = u("summary", null, " Explain this insight ", -1)),
          u("div", Hc, [
            u("p", null, [
              _[0] || (_[0] = u("strong", null, "What this is about:", -1)),
              O(" " + v(Xe(Nc)(e.insight)), 1),
            ]),
            u("p", null, [
              _[1] || (_[1] = u("strong", null, "Plain language:", -1)),
              O(" " + v(Xe(Vc)(e.insight)), 1),
            ]),
            u("p", null, [
              _[2] || (_[2] = u("strong", null, "Why this score:", -1)),
              O(" " + v(Xe(Dc)(e.insight, s.value)), 1),
            ]),
            u("ul", Uc, [
              u(
                "li",
                null,
                "confidence: " +
                  v(s.value.confidence) +
                  " = " +
                  v(Xe(gt)(s.value.confidenceScore)),
                1,
              ),
              u(
                "li",
                null,
                "source breadth: " +
                  v(s.value.papers.length) +
                  " paper(s) x 0.5 = " +
                  v(Xe(gt)(s.value.paperScore)),
                1,
              ),
              u(
                "li",
                null,
                "reasoning bonus: " + v(Xe(gt)(s.value.realBonus)),
                1,
              ),
              u("li", null, "total score: " + v(Xe(gt)(s.value.shown)), 1),
            ]),
            u(
              "button",
              {
                type: "button",
                class: "llm-action",
                disabled: n.value,
                onClick: d,
              },
              v(n.value ? "Asking LLM..." : "Ask LLM for more detail"),
              9,
              Kc,
            ),
            i.value
              ? (g(), m("div", qc, v(i.value), 1))
              : o.value
                ? (g(),
                  m("div", Bc, [
                    u(
                      "div",
                      Wc,
                      " Generated by " + v(o.value.model || "LLM"),
                      1,
                    ),
                    (g(),
                    m(
                      V,
                      null,
                      oe(
                        c,
                        (x) => (
                          g(),
                          m(
                            V,
                            { key: x.key },
                            [
                              u("h4", null, v(x.label), 1),
                              u("p", null, v(l.value[x.key]), 1),
                            ],
                            64,
                          )
                        ),
                      ),
                      64,
                    )),
                    _[3] || (_[3] = u("h4", null, "technical terms", -1)),
                    r.value
                      ? (g(), m("p", zc, v(r.value), 1))
                      : a.value.length
                        ? (g(),
                          m("dl", Jc, [
                            (g(!0),
                            m(
                              V,
                              null,
                              oe(
                                a.value,
                                (x, K) => (
                                  g(),
                                  m("div", { key: K, class: "term" }, [
                                    x.term
                                      ? (g(), m("dt", Gc, v(x.term), 1))
                                      : j("", !0),
                                    u("dd", null, v(x.def), 1),
                                  ])
                                ),
                              ),
                              128,
                            )),
                          ]))
                        : (g(), m("p", Yc, " none noted ")),
                  ]))
                : j("", !0),
          ]),
        ])
      );
    },
  },
  Xc = Qe(Qc, [["__scopeId", "data-v-45365040"]]),
  Zc = { class: "card" },
  ef = { class: "filterbar" },
  tf = { class: "card" },
  sf = { key: 0, class: "muted" },
  nf = { class: "score" },
  of = { key: 0, class: "tag stub" },
  lf = { key: 1, class: "muted" },
  rf = {
    __name: "InsightsView",
    props: { data: Object },
    setup(e) {
      const t = e,
        s = ne("all"),
        n = ne("all"),
        i = ne(0);
      function o() {
        ((s.value = "all"), (n.value = "all"), (i.value = 0));
      }
      const l = q(() =>
        (t.data.insights || []).filter((r) =>
          (s.value !== "all" && r.kind !== s.value) ||
          (n.value !== "all" && r.confidence !== n.value)
            ? !1
            : (r._score ?? 0) >= (i.value || 0),
        ),
      );
      return (r, a) => (
        g(),
        m("div", null, [
          u("div", Zc, [
            a[5] || (a[5] = u("h3", null, "Filter insights", -1)),
            u("div", ef, [
              Ve(
                u(
                  "select",
                  {
                    "onUpdate:modelValue":
                      a[0] || (a[0] = (c) => (s.value = c)),
                  },
                  [
                    ...(a[3] ||
                      (a[3] = [
                        tr(
                          '<option value="all">all kinds</option><option value="evidence">evidence</option><option value="synergy">synergy</option><option value="gap">gap</option><option value="contradiction">contradiction</option><option value="hypothesis">hypothesis</option>',
                          6,
                        ),
                      ])),
                  ],
                  512,
                ),
                [[tn, s.value]],
              ),
              Ve(
                u(
                  "select",
                  {
                    "onUpdate:modelValue":
                      a[1] || (a[1] = (c) => (n.value = c)),
                  },
                  [
                    ...(a[4] ||
                      (a[4] = [
                        u("option", { value: "all" }, "all confidence", -1),
                        u("option", { value: "high" }, "high", -1),
                        u("option", { value: "medium" }, "medium", -1),
                        u("option", { value: "low" }, "low", -1),
                      ])),
                  ],
                  512,
                ),
                [[tn, n.value]],
              ),
              Ve(
                u(
                  "input",
                  {
                    "onUpdate:modelValue":
                      a[2] || (a[2] = (c) => (i.value = c)),
                    type: "number",
                    placeholder: "min score",
                    style: { width: "120px" },
                  },
                  null,
                  512,
                ),
                [[ct, i.value, void 0, { number: !0 }]],
              ),
              u("button", { onClick: o }, " Reset "),
            ]),
          ]),
          u("div", tf, [
            u(
              "h3",
              null,
              " Autonomous analyst · top " +
                v(l.value.length) +
                " of " +
                v(e.data.count) +
                " insight(s) ",
              1,
            ),
            l.value.length
              ? j("", !0)
              : (g(),
                m("div", sf, [
                  ...(a[6] ||
                    (a[6] = [
                      O(" No insights yet. Run the analyst: ", -1),
                      u("code", null, "python -m analyst run", -1),
                    ])),
                ])),
            (g(!0),
            m(
              V,
              null,
              oe(
                l.value,
                (c) => (
                  g(),
                  m("div", { key: c.id, class: "row" }, [
                    u("span", nf, "score " + v(c._score), 1),
                    u(
                      "span",
                      { class: ue(["tag", `tag--${c.kind}`]) },
                      v(c.kind),
                      3,
                    ),
                    u(
                      "span",
                      { class: ue(["tag", `tag--conf-${c.confidence}`]) },
                      v(c.confidence),
                      3,
                    ),
                    c.stub ? (g(), m("span", of, "stub")) : j("", !0),
                    O(" " + v(c.summary) + " ", 1),
                    c.provenance?.length
                      ? (g(),
                        m(
                          "div",
                          lf,
                          " provenance: " + v(c.provenance.join(", ")),
                          1,
                        ))
                      : j("", !0),
                    J(Xc, { insight: c }, null, 8, ["insight"]),
                  ])
                ),
              ),
              128,
            )),
          ]),
        ])
      );
    },
  },
  af = { class: "card" },
  uf = { key: 0, class: "muted", style: { color: "var(--red)" } },
  cf = {
    key: 1,
    class: "filterbar",
    style: { gap: "14px", "align-items": "center" },
  },
  ff = { class: "muted" },
  df = { class: "muted" },
  pf = { class: "muted" },
  hf = { key: 2, class: "muted", style: { "margin-top": "10px" } },
  gf = { key: 3, class: "muted", style: { "margin-top": "10px" } },
  vf = { key: 4, class: "muted", style: { "margin-top": "8px" } },
  mf = { key: 5, class: "muted", style: { "margin-top": "8px" } },
  yf = {
    key: 6,
    class: "muted",
    style: { "margin-top": "8px", color: "var(--red)" },
  },
  _f = { class: "filterbar", style: { "margin-top": "14px" } },
  bf = ["disabled"],
  wf = ["disabled"],
  $f = ["disabled"],
  xf = ["disabled"],
  kf = ["disabled"],
  Cf = ["disabled"],
  Sf = {
    key: 7,
    class: "muted",
    style: { "margin-top": "10px", color: "var(--green)" },
  },
  Mf = { key: 0, class: "card" },
  Tf = { class: "filterbar" },
  Af = { class: "field" },
  Of = { class: "field" },
  If = { class: "field" },
  Ef = { class: "field" },
  Rf = { class: "field" },
  jf = { class: "box" },
  Pf = { class: "toggle-row" },
  Ff = ["onClick"],
  Lf = { class: "box" },
  Nf = { class: "muted query-label" },
  Vf = ["onUpdate:modelValue", "placeholder"],
  Df = { class: "filterbar", style: { "margin-top": "14px" } },
  Hf = ["disabled"],
  Uf = {
    __name: "AnalystControl",
    setup(e) {
      const t = ne(null),
        s = ne(null),
        n = ne([]),
        i = ne({}),
        o = ne(""),
        l = ne(""),
        r = ne(!1),
        a = ne(!1),
        c = ne(null);
      let d = null,
        h = null;
      const _ = q(() => {
        const F = t.value?.phase;
        return (
          {
            sleeping: "tag--conf-medium",
            analyzing: "tag--synergy",
            growing: "tag--gap",
            idle: "tag",
            paused: "stub",
            stopped: "tag",
          }[F] || "tag"
        );
      });
      async function x() {
        try {
          ((t.value = await _n()),
            (o.value = ""),
            (c.value = t.value.seconds_to_next));
        } catch (F) {
          o.value = `cannot reach analyst: ${F}`;
        }
      }
      async function K() {
        const F = await ia();
        ((n.value = F.all_sources || []),
          (i.value = F.default_queries || {}),
          E(F.config));
      }
      function E(F) {
        s.value = {
          interval_seconds: F.interval_seconds,
          batch_size: F.batch_size,
          grow: F.grow,
          limit: F.limit,
          offline: F.offline,
          sources: [...(F.sources || [])],
          queries: { ...i.value, ...(F.queries || {}) },
        };
      }
      function le() {
        (t.value?.config && E(t.value.config), (l.value = ""));
      }
      function ee(F) {
        const C = s.value.sources,
          U = C.indexOf(F);
        U === -1 ? C.push(F) : C.length > 1 && C.splice(U, 1);
      }
      async function H(F) {
        ((r.value = !0), (l.value = ""));
        try {
          const C = await li(F);
          ((l.value = C.message || C.error || ""),
            C.error && (o.value = C.error),
            await x());
        } catch (C) {
          o.value = String(C);
        } finally {
          r.value = !1;
        }
      }
      function Q() {
        confirm(
          "Archive the current analyst state + banked insights and start a brand-new analyst from generation 0?",
        ) && H("reset");
      }
      async function P() {
        ((a.value = !0), (l.value = ""));
        try {
          const F = await li("config", s.value);
          ((l.value = F.ok ? "configuration saved" : F.error || "save failed"),
            F.config && E(F.config),
            await x());
        } catch (F) {
          o.value = String(F);
        } finally {
          a.value = !1;
        }
      }
      return (
        xt(async () => {
          (await K(),
            await x(),
            (d = setInterval(x, 2e3)),
            (h = setInterval(() => {
              c.value !== null && c.value > 0 && (c.value -= 1);
            }, 1e3)));
        }),
        Ss(() => {
          (clearInterval(d), clearInterval(h));
        }),
        (F, C) => (
          g(),
          m("div", null, [
            u("div", af, [
              C[20] ||
                (C[20] = u("h3", null, "Autonomous analyst · control", -1)),
              o.value ? (g(), m("div", uf, v(o.value), 1)) : j("", !0),
              t.value
                ? (g(),
                  m("div", cf, [
                    u(
                      "span",
                      { class: ue(["tag", _.value]) },
                      v(t.value.phase),
                      3,
                    ),
                    u("span", ff, [
                      C[12] || (C[12] = O("generation ", -1)),
                      u("strong", null, v(t.value.generation), 1),
                    ]),
                    u("span", df, [
                      C[13] || (C[13] = O(" tasks ", -1)),
                      u("strong", null, v(t.value.tasks.done), 1),
                      O(" / " + v(t.value.tasks.total) + " ", 1),
                      t.value.tasks.pending
                        ? (g(),
                          m(
                            V,
                            { key: 0 },
                            [
                              O(
                                " (" + v(t.value.tasks.pending) + " pending) ",
                                1,
                              ),
                            ],
                            64,
                          ))
                        : j("", !0),
                    ]),
                    u("span", pf, [
                      C[14] || (C[14] = O("insights banked ", -1)),
                      u("strong", null, v(t.value.insights_banked), 1),
                    ]),
                  ]))
                : j("", !0),
              t.value && t.value.phase === "sleeping" && c.value !== null
                ? (g(),
                  m("div", hf, [
                    C[15] || (C[15] = O(" next generation in ", -1)),
                    u("strong", null, v(c.value) + "s", 1),
                    C[16] || (C[16] = O(" · or ", -1)),
                    u(
                      "button",
                      {
                        class: "llm-action",
                        style: { margin: "0 0 0 4px", padding: "4px 10px" },
                        onClick: C[0] || (C[0] = (U) => H("run-now")),
                      },
                      " Run now ",
                    ),
                  ]))
                : t.value && t.value.phase === "idle"
                  ? (g(),
                    m("div", gf, [
                      C[17] ||
                        (C[17] = O(" all current tasks done — idle. Set ", -1)),
                      C[18] || (C[18] = u("code", null, "grow > 0", -1)),
                      C[19] ||
                        (C[19] = O(
                          " below (then Save) to keep finding papers, or ",
                          -1,
                        )),
                      u(
                        "button",
                        {
                          class: "llm-action",
                          style: { margin: "0 0 0 4px", padding: "4px 10px" },
                          onClick: C[1] || (C[1] = (U) => H("run-now")),
                        },
                        " Run a generation now ",
                      ),
                    ]))
                  : j("", !0),
              t.value && t.value.next_up?.length
                ? (g(),
                  m("div", vf, " next up: " + v(t.value.next_up.join(", ")), 1))
                : j("", !0),
              t.value?.last_summary
                ? (g(),
                  m(
                    "div",
                    mf,
                    " last generation: ran " +
                      v(t.value.last_summary.ran) +
                      " task(s), " +
                      v(t.value.last_summary.new_insights) +
                      " new insight(s), " +
                      v(t.value.last_summary.pending_after) +
                      " still pending. ",
                    1,
                  ))
                : j("", !0),
              t.value?.last_error
                ? (g(),
                  m("div", yf, " last error: " + v(t.value.last_error), 1))
                : j("", !0),
              u("div", _f, [
                t.value?.running
                  ? j("", !0)
                  : (g(),
                    m(
                      "button",
                      {
                        key: 0,
                        disabled: r.value,
                        onClick: C[2] || (C[2] = (U) => H("start")),
                      },
                      " Start ",
                      8,
                      bf,
                    )),
                t.value?.running && !t.value?.paused
                  ? (g(),
                    m(
                      "button",
                      {
                        key: 1,
                        class: "filterbar-btn",
                        disabled: r.value,
                        onClick: C[3] || (C[3] = (U) => H("pause")),
                      },
                      " Pause ",
                      8,
                      wf,
                    ))
                  : j("", !0),
                t.value?.running && t.value?.paused
                  ? (g(),
                    m(
                      "button",
                      {
                        key: 2,
                        disabled: r.value,
                        onClick: C[4] || (C[4] = (U) => H("resume")),
                      },
                      " Resume ",
                      8,
                      $f,
                    ))
                  : j("", !0),
                t.value?.running
                  ? (g(),
                    m(
                      "button",
                      {
                        key: 3,
                        disabled: r.value,
                        onClick: C[5] || (C[5] = (U) => H("run-now")),
                      },
                      " Fast-forward ",
                      8,
                      xf,
                    ))
                  : j("", !0),
                t.value?.running
                  ? (g(),
                    m(
                      "button",
                      {
                        key: 4,
                        disabled: r.value,
                        onClick: C[6] || (C[6] = (U) => H("stop")),
                      },
                      " Stop ",
                      8,
                      kf,
                    ))
                  : j("", !0),
                t.value?.running
                  ? j("", !0)
                  : (g(),
                    m(
                      "button",
                      {
                        key: 5,
                        disabled: r.value,
                        title:
                          "Archive current state + insights, then start fresh from generation 0",
                        onClick: Q,
                      },
                      " New analyst (reset) ",
                      8,
                      Cf,
                    )),
              ]),
              l.value ? (g(), m("div", Sf, v(l.value), 1)) : j("", !0),
            ]),
            s.value
              ? (g(),
                m("div", Mf, [
                  C[27] || (C[27] = u("h3", null, "Pace and data sources", -1)),
                  C[28] ||
                    (C[28] = u(
                      "div",
                      { class: "muted", style: { "margin-bottom": "12px" } },
                      [
                        O(
                          " Changes apply from the next generation. Saving while sleeping wakes the analyst so a shorter wait or a new ",
                        ),
                        u("code", null, "grow"),
                        O(" takes effect immediately. "),
                      ],
                      -1,
                    )),
                  u("div", Tf, [
                    u("label", Af, [
                      C[21] ||
                        (C[21] = u(
                          "span",
                          { class: "muted" },
                          "wait between generations (s)",
                          -1,
                        )),
                      Ve(
                        u(
                          "input",
                          {
                            "onUpdate:modelValue":
                              C[7] ||
                              (C[7] = (U) => (s.value.interval_seconds = U)),
                            type: "number",
                            min: "0",
                          },
                          null,
                          512,
                        ),
                        [
                          [
                            ct,
                            s.value.interval_seconds,
                            void 0,
                            { number: !0 },
                          ],
                        ],
                      ),
                    ]),
                    u("label", Of, [
                      C[22] ||
                        (C[22] = u(
                          "span",
                          { class: "muted" },
                          "analysis tasks / generation",
                          -1,
                        )),
                      Ve(
                        u(
                          "input",
                          {
                            "onUpdate:modelValue":
                              C[8] || (C[8] = (U) => (s.value.batch_size = U)),
                            type: "number",
                            min: "1",
                          },
                          null,
                          512,
                        ),
                        [[ct, s.value.batch_size, void 0, { number: !0 }]],
                      ),
                    ]),
                    u("label", If, [
                      C[23] ||
                        (C[23] = u(
                          "span",
                          { class: "muted" },
                          "grow: new papers / generation",
                          -1,
                        )),
                      Ve(
                        u(
                          "input",
                          {
                            "onUpdate:modelValue":
                              C[9] || (C[9] = (U) => (s.value.grow = U)),
                            type: "number",
                            min: "0",
                          },
                          null,
                          512,
                        ),
                        [[ct, s.value.grow, void 0, { number: !0 }]],
                      ),
                    ]),
                    u("label", Ef, [
                      C[24] ||
                        (C[24] = u(
                          "span",
                          { class: "muted" },
                          "papers requested / source",
                          -1,
                        )),
                      Ve(
                        u(
                          "input",
                          {
                            "onUpdate:modelValue":
                              C[10] || (C[10] = (U) => (s.value.limit = U)),
                            type: "number",
                            min: "1",
                          },
                          null,
                          512,
                        ),
                        [[ct, s.value.limit, void 0, { number: !0 }]],
                      ),
                    ]),
                    u("div", Rf, [
                      C[26] ||
                        (C[26] = u(
                          "span",
                          { class: "muted" },
                          "reasoning mode",
                          -1,
                        )),
                      u(
                        "button",
                        {
                          type: "button",
                          class: ue(["toggle", { on: s.value.offline }]),
                          onClick:
                            C[11] ||
                            (C[11] = (U) =>
                              (s.value.offline = !s.value.offline)),
                        },
                        [
                          u("span", jf, v(s.value.offline ? "✓" : ""), 1),
                          C[25] ||
                            (C[25] = O(
                              " offline (stub reasoner, no HF_TOKEN) ",
                              -1,
                            )),
                        ],
                        2,
                      ),
                    ]),
                  ]),
                  C[29] ||
                    (C[29] = u(
                      "h4",
                      {
                        style: {
                          margin: "18px 0 8px",
                          color: "var(--accent)",
                          "font-size": "12px",
                        },
                      },
                      " Sources to ingest from (when growing) ",
                      -1,
                    )),
                  u("div", Pf, [
                    (g(!0),
                    m(
                      V,
                      null,
                      oe(
                        n.value,
                        (U) => (
                          g(),
                          m(
                            "button",
                            {
                              key: U,
                              type: "button",
                              class: ue([
                                "toggle",
                                { on: s.value.sources.includes(U) },
                              ]),
                              onClick: (Ce) => ee(U),
                            },
                            [
                              u(
                                "span",
                                Lf,
                                v(s.value.sources.includes(U) ? "✓" : ""),
                                1,
                              ),
                              O(" " + v(U), 1),
                            ],
                            10,
                            Ff,
                          )
                        ),
                      ),
                      128,
                    )),
                  ]),
                  C[30] ||
                    (C[30] = u(
                      "h4",
                      {
                        style: {
                          margin: "18px 0 8px",
                          color: "var(--accent)",
                          "font-size": "12px",
                        },
                      },
                      " Per-source search queries ",
                      -1,
                    )),
                  (g(!0),
                  m(
                    V,
                    null,
                    oe(
                      n.value,
                      (U) => (
                        g(),
                        m("div", { key: `q-${U}`, class: "query-row" }, [
                          u("span", Nf, v(U), 1),
                          Ve(
                            u(
                              "input",
                              {
                                "onUpdate:modelValue": (Ce) =>
                                  (s.value.queries[U] = Ce),
                                placeholder: i.value[U],
                              },
                              null,
                              8,
                              Vf,
                            ),
                            [[ct, s.value.queries[U]]],
                          ),
                        ])
                      ),
                    ),
                    128,
                  )),
                  C[31] ||
                    (C[31] = u(
                      "div",
                      {
                        class: "muted",
                        style: { "margin-top": "6px", "font-size": "11px" },
                      },
                      [
                        O(" arXiv uses search_query syntax (e.g. "),
                        u("code", null, "cat:cs.LG"),
                        O(
                          "), Semantic Scholar takes free text, OpenReview takes a venue id (e.g. ",
                        ),
                        u("code", null, "ICLR.cc/2024/Conference"),
                        O("). "),
                      ],
                      -1,
                    )),
                  u("div", Df, [
                    u(
                      "button",
                      { disabled: a.value, onClick: P },
                      v(a.value ? "Saving..." : "Save configuration"),
                      9,
                      Hf,
                    ),
                    u("button", { onClick: le }, " Revert edits "),
                  ]),
                ]))
              : j("", !0),
          ])
        )
      );
    },
  },
  Kf = Qe(Uf, [["__scopeId", "data-v-0e9ea7d2"]]),
  qf = { class: "app" },
  Bf = { class: "content" },
  Wf = { class: "page-head" },
  zf = { key: 0, class: "card" },
  Jf = { key: 1, class: "card" },
  Gf = {
    __name: "App",
    setup(e) {
      const t = {
          overview: [
            "Overview",
            "Corpus, knowledge graph and analyst at a glance",
          ],
          search: [
            "Search papers",
            "Semantic retrieval over the corpus (Layer 4)",
          ],
          related: [
            "Related work",
            "Similar papers, citations and shared methods (Layer 4)",
          ],
          citations: [
            "Citations",
            "Walk the citation graph from a paper (Layer 4)",
          ],
          agent: [
            "Agents",
            "Run one analytical agent over the corpus (Layer 5)",
          ],
          investigate: [
            "Investigate",
            "All agents on a topic, then cross-validation (Layer 6 · A2A)",
          ],
          insights: [
            "Insights",
            "Ranked findings banked by the autonomous analyst",
          ],
          analyst: [
            "Analyst",
            "Drive the autonomous analysis loop — run, pace, sources",
          ],
        },
        s = ne("overview"),
        n = ne("contradiction"),
        i = ne(""),
        o = ne(!1),
        l = ne(null),
        r = ne(null),
        a = q(() => t[s.value] || ["", ""]);
      function c(_, x) {
        if (
          ((s.value = _),
          (l.value = null),
          x !== void 0 && (i.value = x),
          _ === "insights")
        )
          return h();
        x !== void 0 && h();
      }
      function d({ view: _, query: x }) {
        c(_, x);
      }
      async function h() {
        ((o.value = !0), (l.value = null));
        const _ = i.value.trim();
        let x;
        switch (s.value) {
          case "search":
            x = `/api/search?q=${encodeURIComponent(_)}`;
            break;
          case "related":
            x = `/api/related?paper_id=${encodeURIComponent(_)}`;
            break;
          case "citations":
            x = `/api/citations?paper_id=${encodeURIComponent(_)}&depth=1`;
            break;
          case "agent":
            x = `/api/agent?name=${n.value}&topic=${encodeURIComponent(_)}`;
            break;
          case "investigate":
            x = `/api/investigate?topic=${encodeURIComponent(_)}`;
            break;
          case "insights":
            x = "/api/insights?top=50";
            break;
          default:
            o.value = !1;
            return;
        }
        try {
          ((l.value = await (await fetch(x)).json()),
            s.value === "insights" &&
              typeof l.value.count == "number" &&
              (r.value = l.value.count));
        } catch (K) {
          l.value = { error: String(K) };
        } finally {
          o.value = !1;
        }
      }
      return (
        xt(async () => {
          try {
            r.value = (await _n()).insights_banked;
          } catch {}
        }),
        (_, x) => (
          g(),
          m("div", qf, [
            J(
              ea,
              {
                "model-value": s.value,
                "insight-count": r.value,
                "onUpdate:modelValue": c,
              },
              null,
              8,
              ["model-value", "insight-count"],
            ),
            u("div", Bf, [
              J(
                aa,
                { title: a.value[0], subtitle: a.value[1], onGo: c },
                null,
                8,
                ["title", "subtitle"],
              ),
              (g(),
              m("div", { key: s.value, class: "page" }, [
                u("div", Wf, [
                  u("h2", null, v(a.value[0]), 1),
                  u("p", null, v(a.value[1]), 1),
                ]),
                s.value === "overview"
                  ? (g(), Se(Wa, { key: 0, onGo: c }))
                  : s.value === "analyst"
                    ? (g(), Se(Kf, { key: 1 }))
                    : (g(),
                      m(
                        V,
                        { key: 2 },
                        [
                          J(
                            bu,
                            {
                              mode: s.value,
                              agent: n.value,
                              "onUpdate:agent":
                                x[0] || (x[0] = (K) => (n.value = K)),
                              query: i.value,
                              "onUpdate:query":
                                x[1] || (x[1] = (K) => (i.value = K)),
                              loading: o.value,
                              onRun: h,
                            },
                            null,
                            8,
                            ["mode", "agent", "query", "loading"],
                          ),
                          l.value?.error
                            ? (g(),
                              m("div", zf, [
                                x[2] ||
                                  (x[2] = u(
                                    "span",
                                    { class: "muted" },
                                    "error:",
                                    -1,
                                  )),
                                O(" " + v(l.value.error), 1),
                              ]))
                            : o.value
                              ? (g(),
                                m("div", Jf, [
                                  ...(x[3] ||
                                    (x[3] = [
                                      u(
                                        "div",
                                        {
                                          class: "skeleton",
                                          style: { width: "30%" },
                                        },
                                        null,
                                        -1,
                                      ),
                                      u(
                                        "div",
                                        {
                                          class: "skeleton",
                                          style: { width: "90%" },
                                        },
                                        null,
                                        -1,
                                      ),
                                      u(
                                        "div",
                                        {
                                          class: "skeleton",
                                          style: { width: "80%" },
                                        },
                                        null,
                                        -1,
                                      ),
                                      u(
                                        "div",
                                        {
                                          class: "skeleton",
                                          style: { width: "60%" },
                                        },
                                        null,
                                        -1,
                                      ),
                                    ])),
                                ]))
                              : s.value === "search" && l.value
                                ? (g(),
                                  Se(
                                    Uu,
                                    { key: 2, data: l.value, onOpen: d },
                                    null,
                                    8,
                                    ["data"],
                                  ))
                                : s.value === "related" && l.value
                                  ? (g(),
                                    Se(
                                      fc,
                                      { key: 3, data: l.value, onOpen: d },
                                      null,
                                      8,
                                      ["data"],
                                    ))
                                  : s.value === "citations" && l.value
                                    ? (g(),
                                      Se(
                                        $c,
                                        { key: 4, data: l.value, onOpen: d },
                                        null,
                                        8,
                                        ["data"],
                                      ))
                                    : s.value === "agent" && l.value
                                      ? (g(),
                                        Se(
                                          fo,
                                          {
                                            key: 5,
                                            title: `Agent: ${l.value.agent}`,
                                            findings: l.value.findings || [],
                                          },
                                          null,
                                          8,
                                          ["title", "findings"],
                                        ))
                                      : s.value === "investigate" && l.value
                                        ? (g(),
                                          Se(
                                            Ec,
                                            { key: 6, report: l.value },
                                            null,
                                            8,
                                            ["report"],
                                          ))
                                        : s.value === "insights" && l.value
                                          ? (g(),
                                            Se(
                                              rf,
                                              { key: 7, data: l.value },
                                              null,
                                              8,
                                              ["data"],
                                            ))
                                          : l.value
                                            ? (g(),
                                              Se(
                                                Jt,
                                                { key: 8, data: l.value },
                                                null,
                                                8,
                                                ["data"],
                                              ))
                                            : (g(),
                                              Se(
                                                gu,
                                                {
                                                  key: 9,
                                                  view: s.value,
                                                  onOpen: d,
                                                },
                                                null,
                                                8,
                                                ["view"],
                                              )),
                        ],
                        64,
                      )),
              ])),
            ]),
          ])
        )
      );
    },
  };
Ur(Gf).mount("#app");
