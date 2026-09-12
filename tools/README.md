# tools

The builders for the documents that are not written by hand.

| Script | Builds | Goes to |
| --- | --- | --- |
| `loom_parts.js` | Nothing on its own. It holds the spoken lines for the demo video, shared by the two scripts below so they can never disagree. | |
| `build_rehearsal.js` | The full rehearsal guide | `docs/Loom_Rehearsal_Script.docx` and `docs/LOOM_SCRIPT.md` |
| `build_speaker.js` | Ali's own screen and words script | `private/` |
| `build_checklist.py` | Ali's personal checklist | `private/` |

The two JavaScript builders need the `docx` package once:

```bash
cd tools
npm install
node build_rehearsal.js
node build_speaker.js
```

The Python one uses the project's own environment:

```bash
venv\Scripts\python tools/build_checklist.py
```

`private/` is git ignored. It holds documents meant for Ali only.
