---
name: tikz-figures
description: Create or edit TikZ/LaTeX figures — neural network architecture diagrams, molecular/isotopologue structure diagrams, algorithm flowcharts, equation/correction diagrams — matching the house style in C:\Code\Figures. Use for thesis or paper figures, any request to draw/diagram a network, molecule, isotopologue, or algorithm in TikZ, or to add a new figure to the Figures archive.
---

# TikZ Figures — house style

Canonical archive: `C:\Code\Figures`. This is a personal thesis/paper figure
store, one standalone TikZ document per figure, one PDF per figure, indexed
in `README.md`. This skill is always invoked against the **absolute path**
`C:\Code\Figures`, regardless of the caller's own working directory — never
write figures into the calling project.

## Hard invariants (every figure, no exceptions)

1. `\documentclass[...,tikz,...]{standalone}` (or `[tikz,...]`) with a
   `border=` option.
2. `\usepackage{amsmath}`.
3. Sans-serif font stack, always:
   ```latex
   \usepackage{helvet}
   \renewcommand{\familydefault}{\sfdefault}
   \usepackage{sansmath}
   \sansmath
   ```
4. `\usetikzlibrary{...}` includes at minimum `arrows.meta` and
   `positioning` (add `calc`, `fit`, `backgrounds`, `decorations.pathreplacing`,
   `shapes.geometric`, `matrix` etc. as the specific figure needs).
5. Colors are always named: `\definecolor{name}{HTML}{...}` or
   `\colorlet{name}{...}` up top, never a raw hex/X11 color inline inside a
   `\node`/`\draw`.
6. Repeated formatting is always a named style — a `\tikzset{...}` block
   or a bracketed option list on `\begin{tikzpicture}[...]` — never copy-pasted
   inline options across multiple nodes.

These were extracted by auditing all 14 existing figures; 4 of them
(`CO_CN_NO.tex`, `iso_CO.tex`, `iso_CO2.tex`, `CO2_OCS_CS2.tex`) originally
missed rule 3 — that was a mistake, since fixed. Don't repeat it.

## Palette: per figure-family, not global

There is no single house palette — different figure families use different
schemes on purpose (e.g. Okabe-Ito colorblind-safe set for multi-class network
diagrams, a viridis-derived set for equation/correction diagrams, element-tinted
colors for molecule diagrams). **If the user hasn't specified colors for a new
figure, ask which scheme to use** (reuse an existing family's palette, or a new
one) rather than defaulting silently. Never invent a palette without asking.

## Directory & naming convention

`<Category>/<subfolder>/<name>.tex`, compiled to `<name>.pdf` alongside it.

Existing categories — **only place new figures into one of these five**;
if a new figure doesn't cleanly fit any of them, ask the user whether to
shoehorn it in or create a new category. Never create a new category silently.

- `Bridging_molecules`
- `Isotopologue_extrapolation`
- `Isotopologues`
- `MARVEL`
- `Neural_Networks`

## Worked examples (best exemplar per archetype)

| Archetype | Exemplar file | Notes |
|---|---|---|
| Network/ML architecture | `Neural_Networks/GNN_DNN/gnn_dnn.tex` | Okabe-Ito palette, named node/op styles, `pgfonlayer` background grouping boxes |
| Equation / correction diagram | `Isotopologue_extrapolation/ie_ml.tex` | viridis-derived palette, `shapes.geometric`, boxed-term equation layout |
| Molecular bridging diagram | `Bridging_molecules/CO_CN_NO/CO_CN_NO.tex` | element-tinted atoms, multi-bond `\draw` offsets, `calc` midpoints |
| Isotopologue structure diagram | `Isotopologues/CO2/iso_CO2.tex` | atom/bond/number-box styles, isotopologue designation labels |
| Algorithm flow | `MARVEL/marvel_algorithm.tex` | panelled `scope`+`local bounding box` layout, source-legend convention |

Read the relevant exemplar before writing a new figure in that family — it's
the real reference, this table is just the index.

## Workflow for a new figure

1. Determine category (existing 5, ask if ambiguous) and palette (ask if
   unspecified).
2. Start from `assets/template.tex` — already satisfies all hard invariants.
3. Read the matching worked example for layout/style conventions.
4. Write the figure at `C:\Code\Figures\<Category>\<subfolder>\<name>.tex`.
5. Run the self-check: `python .claude\skills\tikz-figures\scripts\self_check.py <path>.tex`.
   Fix anything it flags before proceeding.
6. Compile a draft PNG for quick review:
   `latexmk -pdf -interaction=nonstopmode <name>.tex && pdftocairo -png -r 150 -singlefile <name>.pdf <name>`
   (note the space in `-r 150` — this build of `pdftocairo` rejects `-r150`)
7. Once approved, produce the final artifacts alongside the `.tex`:
   PDF (already produced by step 6) and SVG via
   `pdftocairo -svg <name>.pdf <name>.svg` (or `dvisvgm` if finer vector
   fidelity is needed).
8. **Mandatory:** add the new figure to `README.md`'s categorized link list
   (same format as existing entries — category heading, `[Name](/path/to.pdf)`).
9. Report the absolute path back to the caller. If the calling project has an
   obvious figures folder, optionally copy the PDF there too — the `.tex`
   source of truth always stays in `C:\Code\Figures`.

## Editing an existing figure

Same invariants apply. Re-run `self_check.py` and re-compile after any edit;
don't hand-wave a "looks fine" without regenerating the PDF.

## Cross-repo invocation

This skill is expected to be reachable from any project via a symlink at
`~/.claude/skills/tikz-figures` pointing at
`C:\Code\Figures\.claude\skills\tikz-figures`. If that symlink isn't present
on a given machine, fall back to reading this file directly at its absolute
path — a consuming project's `CLAUDE.md` should say so explicitly, e.g.:
"For TikZ figures, read `C:\Code\Figures\.claude\skills\tikz-figures\SKILL.md`
first."
