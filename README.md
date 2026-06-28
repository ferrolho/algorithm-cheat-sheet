# Algorithm Selection Cheat Sheet

A single-page **A4 landscape PDF** mapping "clue in the problem statement" →
"technique to reach for", inspired by the AlgoMonster flowchart. The finished sheet
is [`algorithm-cheat-sheet.pdf`](algorithm-cheat-sheet.pdf) — exact A4, prints with no scaling.

<p align="center">
  <a href="algorithm-cheat-sheet.pdf" target="_blank" rel="noopener noreferrer">
    <img src="preview.png" alt="The Algorithm Selection Cheat Sheet — click to open the PDF" width="100%">
  </a>
</p>

## Editing

Everything comes from [`flowchart.yaml`](flowchart.yaml) — edit it, then rebuild.
Each `section` is a titled box whose `steps` are decision points read top to bottom.
A step is a question with `if_yes` (a "No" falls through to the next step), with
`if_yes` + `if_no`, with a nested `then:`, or a final `otherwise:` default. Each
technique has a `use` (pill label) and `when` (italic trigger phrases, ` · `-separated).
The comment header in `flowchart.yaml` has the full format and examples.

Pill colours come from the technique name via `fam()` in [`config.py`](config.py),
layout constants live at the top of [`build.py`](build.py), and balancing the sections
across 4 columns is automatic.

## Rebuild

Rendering uses `cairosvg`, which needs the native **cairo** library (not a pip package):

```bash
brew install cairo                 # macOS  (Ubuntu: sudo apt install libcairo2)
pip install -r requirements.txt
./build.sh                         # or: python3 build.py
```

Text is measured with a Helvetica/Arial-metric font auto-detected per platform; if
none is found, install Liberation Sans or set `ALGOSEL_FONT_REGULAR` /
`ALGOSEL_FONT_BOLD` to a TTF.

## Attribution & license

This sheet recreates only the *decision logic* — the general "which clue → which
technique" mapping — popularised by [AlgoMonster's flowchart](https://algo.monster/flowchart).
That logic is common computer-science knowledge (an idea/method, not copyrightable
expression); the wording, keyword phrases, colours, layout, and code here are
original, and **no AlgoMonster text, artwork, or assets are copied or redistributed**.
Independent study aid, **not affiliated with or endorsed by AlgoMonster** — the name
is used only nominatively to credit the inspiration; if their tool helps you, support
the original.

Code and YAML are released under the **MIT License** (see [`LICENSE`](LICENSE)). The
committed `algorithm-cheat-sheet.pdf` is a build output of `flowchart.yaml`, which
remains the source of truth.
