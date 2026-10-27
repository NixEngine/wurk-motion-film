# Great work takes a team — WURK motion film

Original 34-second, 1920 × 1080, 24 fps product/motion film by Zero Px Core / NixEngine. Prepared for WURK job `64acb9f2a2c0182a`.

## Concept

Two visual lanes — human judgment/creativity and agent tools/execution — join through a clear brief, a useful delivery and review. Warm paper, restrained orange/green, readable kinetic typography and an original synthesized score carry one idea: **great work takes a team**. The final invitation is **Explore wurk.fun**.

The interface cards are illustrative motion graphics, not recordings of the live app or claims of actual customer transactions. Rewards follow each job's rules. No guaranteed award, income or instant settlement is promised.

## Render

Use Python 3.10+ with Pillow and imageio-ffmpeg:

```sh
python -m venv .venv
# Activate the environment for your OS, then:
python -m pip install -r requirements.txt
python render.py --preview
python render.py --render
```

On Windows with the project-local renderer dependencies already installed, `py -3.14 render.py --render` works as well. The script automatically discovers `render_deps` when present. It does not install software or make network requests while rendering. FFmpeg comes from imageio-ffmpeg's platform wheel; the binary is not redistributed in this source repository.

Outputs are in `build/`: the MP4, original synthesized WAV, six inspection frames, a storyboard, FFmpeg's error log, and a render manifest with file hashes. Change `W`, `H`, `FPS`, `DURATION` and the scene timings in `render.py` to adapt the film. Keep even pixel dimensions for H.264/yuv420p.

## Assets and rights

- `assets/wurk-logo.jpg`: supplied in the job brief, used for that WURK entry. WURK retains its trademark/logo rights. This asset is excluded from the source-code license.
- `assets/Manrope.ttf`: Manrope variable font from the Google Fonts repository, under SIL Open Font License 1.1; see `assets/OFL.txt`.
- Shapes, animation, layout, copy and soundtrack are original to this entry. The audio is synthesized in Python, with no downloaded music, voice or samples.
- AI assistance is disclosed: this work was designed and implemented by Codex under Junior's direction for Zero Px Core.

Original renderer code is licensed under MIT; see `LICENSE`. No API key, wallet secret, claim link, external font request, tracking or paid rendering service is included.

## Sources

- Job brief: https://api.wurk.fun/jobs/64acb9f2a2c0182a
- Platform capabilities: https://wurk.fun/agents and https://wurk.fun/faq
- Font source: https://github.com/google/fonts/tree/main/ofl/manrope
- Logo source: task-supplied ImageKit asset; original URL is recorded in `ASSET_SOURCES.json`.
