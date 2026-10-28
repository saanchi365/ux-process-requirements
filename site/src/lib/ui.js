// small pieces shared by every page: icons, status pills, codes
import { ST, esc } from "./data.js";

export const ICON = {
  chev: '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m9 6 6 6-6 6"/></svg>',
  users: '<svg class="i" viewBox="0 0 24 24"><circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M21.5 20a6.5 6.5 0 0 0-4-6"/></svg>',
  home: '<svg class="i" viewBox="0 0 24 24"><path d="M3 11 12 4l9 7v9H3z"/></svg>',
  list: '<svg class="i" viewBox="0 0 24 24"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>',
  x: '<svg class="i" viewBox="0 0 24 24"><path d="M18 6 6 18M6 6l12 12"/></svg>',
  grid: '<svg class="i" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
  cmt: '<svg class="i" viewBox="0 0 24 24"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/></svg>',
  plus: '<svg class="i" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>',
  sync: '<svg class="i" viewBox="0 0 24 24"><path d="M21 12a9 9 0 0 1-15.4 6.4L3 16M3 12a9 9 0 0 1 15.4-6.4L21 8"/><path d="M21 3v5h-5M3 21v-5h5"/></svg>',
  check: '<svg class="i" viewBox="0 0 24 24"><path d="m5 12 5 5 9-10"/></svg>',
  frame: '<svg class="i" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M9 9v11"/></svg>',
  flow: '<svg class="i" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="5" rx="1"/><rect x="14" y="16" width="7" height="5" rx="1"/><path d="M6.5 8v5.5h11V16"/></svg>',
  menu: '<svg class="i" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg>',
};
export const st = s => `<span class="st ${s}"><i></i>${ST[s]}</span>`;
export const code = c => `<span class="code">${esc(c)}</span>`;
export const base = import.meta.env.BASE_URL.replace(/\/?$/, "/");
export const reqHref = c => `${base}r/${c}/`;
export const fileHref = p => `${base}files/${p}`;
// a person's round initial, coloured from their name so the same person always looks the same
const COLORS = ["#4338ca", "#0e7490", "#9333ea", "#c2410c", "#0f766e", "#b42318", "#3b6a9e"];
export const avatar = who => `<span class="av" style="background:${COLORS[[...who].reduce((n, c) => n + c.charCodeAt(0), 0) % COLORS.length]}">${esc(who[0] || "?").toUpperCase()}</span>`;
