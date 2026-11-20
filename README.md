<a href="https://geometor.github.io/model/"><img src="docsrc/_static/logo.png" alt="GEOMETOR • model Medallion" align="right" width="150"></a>

# GEOMETOR • model

**Visit the Online Archive:** https://geometor.github.io/model/

<p align="center">
  <a href="https://geometor.github.io/model/"><img src="docsrc/_static/hero.svg" alt="GEOMETOR • model featured geometric construction"></a>
</p>

**Symbolic Geometry Model • Exact SymPy compass-and-straightedge construction engine**

## Mission

`geometor/model` is part of the interconnected [GEOMETOR](https://geometor.com) semantic digital archive. It provides the core symbolic algebra engine for defining, constructing, and verifying compass-and-straightedge geometric systems with infinite algebraic precision. Powered by SymPy, it liberates geometric proofs from floating-point approximation error into exact polynomial coordinates, ancestor dependency tracking, automatic intersection discovery, and calibrated theme-adaptive vector rendering across the GEOMETOR corpus.

## Capabilities & Interactive Docs

- [Symbolic Geometry Model](https://geometor.github.io/model/) — Comprehensive documentation of the exact SymPy construction engine, algebraic element hierarchies, and interactive CLI.
- [Model Usage & Elements](https://geometor.github.io/model/usage/model/) — In-depth guide to points, lines, circles, segments, wedges, polygons, chains, and polynomial roots.
- [Construction Demos](https://geometor.github.io/model/demos/) — Executable construction walkthroughs including the Vesica Piscis and regular polygons.
- [Python API Reference](https://geometor.github.io/model/modules/) — Complete auto-generated module documentation for `geometor.model`.

## Quickstart

```python
from geometor.model import Model

model = Model("equilateral")
A = model.set_point(0, 0, classes=["given"], label="A")
B = model.set_point(1, 0, classes=["given"], label="B")

model.construct_circle(A, B)
model.construct_circle(B, A)

# Intersections C and D are automatically discovered and labeled
for pt in model.points:
    print(pt.label, pt.x, pt.y)
```
## Repository Contents

- `docsrc/` — RST documentation, guides, and API tracks compiled by [PHOTON publish](https://github.com/photon-platform/publish).
- `src/geometor/model/` — Core symbolic geometry engine, element classes, intersection solvers, and JSON serialization.

## Local Build & Verification

```bash
publish build
uv run --no-sync pytest
```
## Part of the GEOMETOR Knowledge Archive

Explore all **74 Book Codices** and **11 Mathematical Catalogs** at https://geometor.com/books/.
