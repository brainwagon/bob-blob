#!/bin/sh
# Regenerate Bob's intro with Kokoro-82M through OpenRouter.
# Requires a valid OPENROUTER_API_KEY; the current environment key is expired.
set -eu
cd "$(dirname "$0")"

if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  echo "Set OPENROUTER_API_KEY to regenerate Bob's voice." >&2
  exit 1
fi

TEXT="Hi, I'm Bob! I'm a squishy gummy blob, built in one HTML file with OpenCode. My body is ray marched from signed distance functions, my face is drawn with cartoon decals and visemes, and this is my little velvet stage and microphone. Thanks for stopping by!"

payload=$(jq -n \
  --arg model "hexgrad/kokoro-82m" \
  --arg input "$TEXT" \
  --arg voice "am_puck" \
  '{model:$model, input:$input, voice:$voice, response_format:"mp3"}')

curl -sS --fail-with-body --max-time 120 \
  "https://openrouter.ai/api/v1/audio/speech" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  --data "$payload" \
  -o bob-intro.mp3

afconvert -f WAVE -d LEI16@22050 -c 1 bob-intro.mp3 bob-intro.wav
python3 make-lipsync.py bob-intro.wav bob-lipsync.js
rm -f bob-intro.mp3

echo "Regenerated bob-intro.wav and bob-lipsync.js. Reload index.html."
