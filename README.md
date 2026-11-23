# Bob

A tiny WebGL2 viewer for a soft, squishy blob character performing on a little
theatre stage, built from signed distance functions (SDFs) in a fragment shader.

Open `index.html` in any modern browser — no build step or server. Keep
`bob-intro.wav` and `bob-lipsync.js` beside it for the spoken intro.

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
- **Face** — flat cartoon decals projected onto the head: white eyes with black
  outlines and moving pupils, occasional blinks, and a full 15-viseme set
  (sil, PP, FF, TH, DD, kk, CH, SS, nn, RR, aa, E, I, O, U) with teeth and
  tongue layers. Idle moods add an open smile, frown, and small "o".
- **Material** — dark cherry gummy: wrapped lighting, a red subsurface glow
  estimated by probing the SDF for thickness, cool rim light, warm bounce, and a
  wet two-lobe highlight.
- **Performance** — idle breathing and arm sway, a short dance every 13 seconds
  (hip sway, bounce, alternating arm raises and foot taps), plus the poke wobble.
  While he dances he sings the viseme sequence into the microphone.
- **Stage** — a round wooden-plank stage, deep red velvet curtains with vertical
  folds and a warm halo, and three-point lighting: warm key, cool edge, warm
  bounce.
- **Microphone** — a ribbon mic on a tripod boom stand at mouth height, with a
  ribbed grille, chrome caps, yoke, collar, counterweight, and a floor cable.
- **Voice** — the “Hear Bob” button plays his intro and drives the mouth from a
  baked 30 fps lip-sync track (`bob-lipsync.js`). The included audio is a local
  macOS `say` placeholder because the OpenRouter key in this environment is
  expired. `./make-voice.sh` regenerates it with `hexgrad/kokoro-82m`
  (voice `am_puck`) when a valid `OPENROUTER_API_KEY` is available, then rebuilds
  the lip-sync track with `make-lipsync.py`.

## Tuning

- `mapChar()` — body proportions, arms/legs, dance/breath animation.
- `faceDecals()` — eyes, pupils, blink shape, mouths, and their outlines.
- `VISEMES` / `SONG` in the script — the 15 mouth presets and the singing order.
- `shadeChar()` — cherry colour, gummy translucency, three-point lighting.
- `mapMic()` / `shadeMic()` — microphone geometry and metal materials.
- `woodColor()`, `backdrop()` — stage floor and curtains.
- `make-voice.sh` — regenerate Bob's Kokoro intro (needs a valid OpenRouter key).
- `make-lipsync.py`, `bob-lipsync.js` — rebuild the lip-sync track from a WAV.
- The camera can be opened at a specific angle with URL params, e.g.
  `index.html?yaw=1.6&pitch=0.2&dist=5.5`.
