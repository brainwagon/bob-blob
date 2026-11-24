# Bob

A tiny WebGL2 viewer for a soft, squishy blob character performing on a little
theatre stage, built from signed distance functions (SDFs) in a fragment shader.

Open `index.html` in any modern browser — no build step or server. Keep
`bob-intro.wav` and `bob-lipsync.js` beside it for the spoken intro.

## Deploy to GitHub Pages

The `Deploy to GitHub Pages` workflow publishes the app whenever a commit is
pushed to `main`, or when started manually from the Actions tab. In the
repository settings, set **Pages → Build and deployment → Source** to
**GitHub Actions**. The published site will be available at
https://mvandewettering.com/bob-blob/.

## Controls

| Action | What happens |
| --- | --- |
| Drag | Orbit the camera |
| Scroll / pinch | Zoom |
| Click / tap | Poke him — he squashes and jiggles |
| Double-click | Reset the camera |
| Hear Bob | Plays his spoken intro; the mouth lip-syncs to the audio |

## What's in the scene

- **Character** — ellipsoid body/head, capsule arms and tapered two-bone legs with
  knee joints, all fused with smooth-min. The body is egg-shaped, rear-weighted,
  with disc hands, thumbs, and flat foot pads. Arms and legs attach to the body
  deliberately: only the upper arm and hip blend into the torso.
- **Face** — flat cartoon decals projected onto the head: pear-shaped eyes that
  taper toward the brow (one a touch larger than the other), heavy upper lids
  whose lash lines cut the eye outline, moving pupils, occasional blinks, and a
  full 15-viseme set (sil, PP, FF, TH, DD, kk, CH, SS, nn, RR, aa, E, I, O, U)
  with teeth and tongue layers. Idle moods add an open smile, frown, and small
  "o".
- **Material** — dark cherry gummy: wrapped lighting, a red subsurface glow
  estimated by probing the SDF for thickness, cool rim light, warm bounce, and a
  wet two-lobe highlight. Fake refraction bends a view ray through the skin at
  grazing angles (per-channel, so the silhouette splits into faint rainbow
  fringes) and focuses a wobbling red caustic web onto the boards at his feet.
- **Performance** — idle breathing and arm sway, a short dance every 13 seconds
  (hip sway, bounce, alternating arm raises and foot taps), plus the poke wobble.
  While he dances, his mouth performs the viseme sequence into the microphone.
- **Stage** — a round wooden-plank stage, deep red velvet curtains with vertical
  folds and a warm halo, and three-point lighting: warm key, cool edge, warm
  bounce.
- **Microphone** — a slightly oversized shiny-brass ribbon mic on a chrome
  tripod boom stand at mouth height, with a ribbed brass grille, polished brass
  caps, brass yoke and counterweight, and a floor cable.
- **Voice** — the “Hear Bob” button plays his intro and drives the mouth from a
  baked 30 fps lip-sync track (`bob-lipsync.js`). The included audio is a
  **Tiny Voca M2** male voice rendered in the browser at
  [tiny-voca.n4ze3m.com](https://tiny-voca.n4ze3m.com/) (24 kHz), and the track
  is generated from that WAV. To use Kokoro instead, run `./make-voice.sh` with
  a valid `OPENROUTER_API_KEY`; `make-lipsync.py` rebuilds the track for either
  voice.

## Tuning

- `mapChar()` — body proportions, arms/legs, dance/breath animation.
- `faceDecals()` — eyes, pupils, blink shape, mouths, and their outlines.
- `VISEMES` / `SONG` in the script — the 15 mouth presets and the singing order.
- `shadeChar()` — cherry colour, gummy translucency, three-point lighting.
- `fakeRefraction()` / `causticWeb()` — the refractive rim, its dispersion, and
  the caustic it throws on the stage floor.
- `mapMic()` / `shadeMic()` — microphone geometry and metal materials.
- `woodColor()`, `backdrop()` — stage floor and curtains.
- `make-voice.sh` — regenerate Bob's Kokoro intro (needs a valid OpenRouter key).
- `make-lipsync.py`, `bob-lipsync.js` — rebuild the lip-sync track from a WAV.
- The camera can be opened at a specific angle with URL params, e.g.
  `index.html?yaw=1.6&pitch=0.2&dist=5.5`.
