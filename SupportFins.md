# 🛸 Support Fins — HiVEMiND local copy

Fork of [gittrahan/support-fins](https://github.com/gittrahan/support-fins) (upstream live at
printfins.com): tip a part on edge and it bakes breakaway support fins into the STL/3MF.
Runs entirely in the browser — vanilla ES modules, no build step.

- Master copy: `D:\Dev\SupportFins` · remote `origin` = MiSTRFiNGA fork, `upstream` = gittrahan.
- RULE 0 exception: **fork of an upstream project + browser/WebGL required** (Three.js) — no Tk shell.

## Launch
- Desktop shortcut **Support Fins** (alien icon) → `Launch Support Fins.bat` → `support_fins_app.py`.
- `support_fins_app.py` (stdlib only) serves `web/` on **127.0.0.1:4731** (claimed in
  `port_registry.json`) and opens a chromeless Edge `--app` window centred on the primary monitor's
  work area. Dedicated profile in `_runtime/edge-profile`, so the server stops when the last window
  closes. A second launch just opens another window. Log: `_runtime/launch.log`.
- `--no-window` serves only. Repair the shortcut with `Create Desktop Shortcut.bat`.

## HiVEMiND branding (the only changes to upstream code)
| Where | Change |
|---|---|
| `web/favicon.svg`, `favicon-32.png`, `apple-touch-icon.png`, `alien.ico` | alien logo |
| `web/style.css` `:root` | navy void `#070a12`, panels `#0e1220`, accent alien lime `#c6f01a` |
| `web/ui/finbuild.js`, `walls.js`, `.sw-fin` | fins in logo lime `#b5e61d` |
| `web/ui/pose.js` | hover face in alien violet `#a78bfa` (keeps Draw's green distinct) |
| `web/ui/scene.js` | background + grid/plate tinted to the palette |

Semantic colours (overhang red, small-overhang amber, bed blue, pad gold) are untouched — they carry meaning.

## HiVEMiND feature changes
| Change | Where |
|---|---|
| **Export → Save As dialog** — every Export menu item asks where to save (File System Access API; plain download fallback in browsers without it; Cancel is silent) | `web/stl.js` `saveAs()`, `web/ui/export.js` |
| **Clear fins** button beside *Fins on* (shown only while fins are on) — fins off + drops hand-drawn walls/braces and removed-fin marks; one Undo restores all | `web/index.html`, `web/ui/settings.js` |
| **Tests run on Windows** — `urlPath()` turns file URLs into real paths (was `/D:/…`, os error 123); OCCT is evaluated as CommonJS because Deno 2.x `require()` now loads it as an empty ES module. 356/356 pass | `tests/_util.js`, `tests/step.test.js` + 3 tests |

## Updating from upstream
`git fetch upstream && git merge upstream/main` — conflicts, if any, will be in the files above.
