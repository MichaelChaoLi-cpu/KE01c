"""Build the integrated analytical framework as SVG, then export a 400 dpi PNG."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import time

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data/results/figures"
SVG_PATH = OUTPUT_DIR / "Figure_integrated_fire_consequence_and_station_value_framework.svg"
PNG_PATH = OUTPUT_DIR / "Figure_integrated_fire_consequence_and_station_value_framework.png"

CANVAS_WIDTH = 1600
CANVAS_HEIGHT = 880
OUTPUT_DPI = 400
OUTPUT_WIDTH = 5600
OUTPUT_HEIGHT = 3080
CHROME_PATH = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


SVG = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{CANVAS_WIDTH}" height="{CANVAS_HEIGHT}" viewBox="0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}"
     role="img" aria-labelledby="figure-desc">
  <desc id="figure-desc">Plain-language flow showing how post-earthquake conditions, neighbourhood form, emergency access, water, and exposed people inform fire-service priorities.</desc>
  <defs>
    <style>
      .label {{ font-family: "DejaVu Sans", Arial, sans-serif; font-size: 16px; font-weight: 700; letter-spacing: 0.3px; }}
      .card-title {{ font-family: "DejaVu Sans", Arial, sans-serif; font-size: 25px; font-weight: 700; fill: #1f3140; }}
      .body {{ font-family: "DejaVu Sans", Arial, sans-serif; font-size: 18px; font-weight: 400; fill: #617383; }}
      .metric {{ font-family: "DejaVu Sans", Arial, sans-serif; font-size: 19px; font-weight: 700; fill: #243746; }}
      .hero-kicker {{ font-family: "DejaVu Sans", Arial, sans-serif; font-size: 15px; font-weight: 700; letter-spacing: 0.4px; fill: #bfd7e6; }}
      .hero-title {{ font-family: "DejaVu Sans", Arial, sans-serif; font-size: 31px; font-weight: 700; fill: #ffffff; }}
      .formula {{ font-family: "DejaVu Sans", Arial, sans-serif; font-size: 21px; font-weight: 400; fill: #e9f1f5; }}
      .small {{ font-family: "DejaVu Sans", Arial, sans-serif; font-size: 15px; font-weight: 400; fill: #6c7c89; }}
      .output-title {{ font-family: "DejaVu Sans", Arial, sans-serif; font-size: 25px; font-weight: 700; fill: #223441; }}
      .output-metric {{ font-family: "DejaVu Sans", Arial, sans-serif; font-size: 20px; font-weight: 700; fill: #344b5b; }}
      .output-body {{ font-family: "DejaVu Sans", Arial, sans-serif; font-size: 17px; font-weight: 400; fill: #627482; }}
      .footer {{ font-family: "DejaVu Sans", Arial, sans-serif; font-size: 15px; font-weight: 400; fill: #637481; }}
    </style>
    <filter id="shadow" x="-15%" y="-15%" width="130%" height="140%">
      <feDropShadow dx="0" dy="5" stdDeviation="7" flood-color="#213849" flood-opacity="0.10"/>
    </filter>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#9aabb7"/>
    </marker>
    <linearGradient id="hero" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#29495d"/>
      <stop offset="1" stop-color="#1e3545"/>
    </linearGradient>
  </defs>

  <rect width="1600" height="950" fill="#ffffff"/>

  <g transform="translate(0,-70)">
  <!-- Connectors behind the cards -->
  <g fill="none" stroke="#9aabb7" stroke-width="2.2" marker-end="url(#arrow)">
    <path d="M 235 335 C 235 385, 420 392, 575 430"/>
    <path d="M 615 335 C 615 385, 665 396, 710 430"/>
    <path d="M 995 335 C 995 385, 935 396, 890 430"/>
    <path d="M 1375 335 C 1375 385, 1180 392, 1025 430"/>
    <path d="M 800 567 L 800 617"/>
  </g>

  <!-- Evidence cards -->
  <g filter="url(#shadow)">
    <rect x="70" y="145" width="330" height="190" rx="18" fill="#ffffff" stroke="#5f91ad" stroke-width="2"/>
    <rect x="70" y="145" width="330" height="8" rx="4" fill="#5f91ad"/>
    <rect x="450" y="145" width="330" height="190" rx="18" fill="#ffffff" stroke="#6681af" stroke-width="2"/>
    <rect x="450" y="145" width="330" height="8" rx="4" fill="#6681af"/>
    <rect x="830" y="145" width="330" height="190" rx="18" fill="#ffffff" stroke="#42928a" stroke-width="2"/>
    <rect x="830" y="145" width="330" height="8" rx="4" fill="#42928a"/>
    <rect x="1210" y="145" width="330" height="190" rx="18" fill="#ffffff" stroke="#ad7e58" stroke-width="2"/>
    <rect x="1210" y="145" width="330" height="8" rx="4" fill="#ad7e58"/>
  </g>

  <!-- Card 1 -->
  <text x="98" y="183" class="label" fill="#4d839f">Neighbourhoods</text>
  <text x="98" y="221" class="card-title">Could fire spread easily?</text>
  <text x="98" y="257" class="body">Dense, closely spaced buildings</text>
  <text x="98" y="284" class="body">Few roads or open spaces as breaks</text>
  <line x1="98" y1="300" x2="372" y2="300" stroke="#d8e2e8"/>
  <text x="98" y="324" class="metric">Higher chance of rapid spread</text>

  <!-- Card 2 -->
  <text x="478" y="183" class="label" fill="#5c78a8">Emergency access</text>
  <text x="478" y="221" class="card-title">Can firefighters arrive?</text>
  <text x="478" y="257" class="body">Longer travel after road disruption</text>
  <text x="478" y="284" class="body">Few backup stations or routes</text>
  <line x1="478" y1="300" x2="752" y2="300" stroke="#d8e2e8"/>
  <text x="478" y="324" class="metric">Slower, less reliable response</text>

  <!-- Card 3 -->
  <text x="858" y="183" class="label" fill="#37857e">Firefighting water</text>
  <text x="858" y="221" class="card-title">Is water dependable?</text>
  <text x="858" y="257" class="body">Compare normal supply with areas</text>
  <text x="858" y="284" class="body">where the network cannot be relied on</text>
  <line x1="858" y1="300" x2="1132" y2="300" stroke="#d8e2e8"/>
  <text x="858" y="324" class="metric">Possible limits on suppression</text>

  <!-- Card 4 -->
  <text x="1238" y="183" class="label" fill="#9b6d49">People and services</text>
  <text x="1238" y="221" class="card-title">Who could be affected?</text>
  <text x="1238" y="257" class="body">Residents and older people</text>
  <text x="1238" y="284" class="body">Hospitals, shelters, and schools</text>
  <line x1="1238" y1="300" x2="1512" y2="300" stroke="#d8e2e8"/>
  <text x="1238" y="324" class="metric">More people and essential services</text>

  <!-- Central estimand -->
  <g filter="url(#shadow)">
    <rect x="300" y="430" width="1000" height="137" rx="22" fill="url(#hero)"/>
  </g>
  <text x="342" y="490" class="hero-title">Where could a fire have the greatest consequences?</text>
  <text x="342" y="532" class="formula">Focus on places where spread, delayed response, limited water, and vulnerable people overlap.</text>

  <!-- Branching rail -->
  <g fill="none" stroke="#9aabb7" stroke-width="2.2" marker-end="url(#arrow)">
    <path d="M 800 617 L 270 617 L 270 657"/>
    <path d="M 800 617 L 800 657"/>
    <path d="M 800 617 L 1330 617 L 1330 657"/>
  </g>
  <rect x="687" y="594" width="226" height="45" rx="22.5" fill="#eef3f6" stroke="#c2cfd7"/>
  <text x="800" y="622" text-anchor="middle" class="label" fill="#506877">Planning decisions</text>

  <!-- Output cards -->
  <g filter="url(#shadow)">
    <rect x="70" y="657" width="400" height="185" rx="18" fill="#ffffff" stroke="#c49132" stroke-width="2"/>
    <rect x="600" y="657" width="400" height="185" rx="18" fill="#ffffff" stroke="#8068a8" stroke-width="2"/>
    <rect x="1130" y="657" width="400" height="185" rx="18" fill="#ffffff" stroke="#6d974f" stroke-width="2"/>
  </g>

  <circle cx="108" cy="694" r="19" fill="#fff0cf"/>
  <text x="108" y="700" text-anchor="middle" class="label" fill="#a47625">01</text>
  <text x="142" y="701" class="output-title">Priority neighbourhoods</text>
  <text x="102" y="748" class="output-metric">Where should attention go first?</text>
  <text x="102" y="782" class="output-body">Direct patrols, access protection, and</text>
  <text x="102" y="808" class="output-body">local checks to the highest-need areas.</text>

  <circle cx="638" cy="694" r="19" fill="#eee9f6"/>
  <text x="638" y="700" text-anchor="middle" class="label" fill="#705a96">02</text>
  <text x="672" y="701" class="output-title">Most valuable fire stations</text>
  <text x="632" y="748" class="output-metric">Which stations are hardest to replace?</text>
  <text x="632" y="782" class="output-body">Find stations whose loss leaves important</text>
  <text x="632" y="808" class="output-body">areas without a good alternative response.</text>

  <circle cx="1168" cy="694" r="19" fill="#e9f2e3"/>
  <text x="1168" y="700" text-anchor="middle" class="label" fill="#5f8842">03</text>
  <text x="1202" y="701" class="output-title">Best use of extra resources</text>
  <text x="1162" y="748" class="output-metric">Which action protects the most?</text>
  <text x="1162" y="782" class="output-body">Compare extra response units, water support,</text>
  <text x="1162" y="808" class="output-body">and reopening important road links.</text>

  <!-- Interpretation boundary -->
  <line x1="70" y1="884" x2="1530" y2="884" stroke="#d5dde2" stroke-width="1.5"/>
  <rect x="70" y="898" width="154" height="28" rx="14" fill="#eef2f4"/>
  <text x="147" y="917" text-anchor="middle" class="label" font-size="13" fill="#576b79">Important note</text>
  <text x="246" y="918" class="footer">A planning comparison — it does not predict where a fire will start, exactly what will burn, or real-time firefighting performance.</text>
  </g>
</svg>
"""


def main() -> None:
    """Write an editable SVG and a 400 dpi PNG rendition."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SVG_PATH.write_text(SVG, encoding="utf-8")

    if not CHROME_PATH.is_file():
        raise FileNotFoundError(f"SVG renderer not found: {CHROME_PATH}")

    # Chrome renders the native SVG at 3.5 device pixels per SVG pixel:
    # 1600 x 880 -> 5600 x 3080, equivalent to a 14-inch figure at 400 dpi.
    with tempfile.TemporaryDirectory(prefix="ke01c_chrome_") as profile_dir:
        raw_png = Path(profile_dir) / "chrome_render.png"
        command = [
            str(CHROME_PATH),
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--no-first-run",
            "--disable-background-networking",
            "--allow-file-access-from-files",
            "--run-all-compositor-stages-before-draw",
            "--default-background-color=ffffffff",
            f"--user-data-dir={profile_dir}",
            f"--window-size={CANVAS_WIDTH},{CANVAS_HEIGHT}",
            "--force-device-scale-factor=3.5",
            f"--screenshot={raw_png}",
            SVG_PATH.as_uri(),
        ]
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if raw_png.is_file() and raw_png.stat().st_size > 0:
                try:
                    with Image.open(raw_png) as rendered:
                        rendered.verify()
                    break
                except OSError:
                    pass
            if process.poll() is not None and not raw_png.is_file():
                raise RuntimeError(f"Chrome exited with code {process.returncode} before rendering")
            time.sleep(0.1)
        else:
            raise TimeoutError("Chrome did not finish the SVG raster within 30 seconds")

        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

        # Chrome controls raster dimensions; Pillow writes explicit publication DPI metadata.
        with Image.open(raw_png) as image:
            if image.size != (OUTPUT_WIDTH, OUTPUT_HEIGHT):
                raise RuntimeError(
                    f"Unexpected Chrome raster size {image.size}; "
                    f"expected {(OUTPUT_WIDTH, OUTPUT_HEIGHT)}"
                )
            image.save(PNG_PATH, dpi=(OUTPUT_DPI, OUTPUT_DPI), optimize=True)

    with Image.open(PNG_PATH) as image:
        if image.size != (OUTPUT_WIDTH, OUTPUT_HEIGHT):
            raise RuntimeError(
                f"Unexpected Chrome raster size {image.size}; "
                f"expected {(OUTPUT_WIDTH, OUTPUT_HEIGHT)}"
            )
        dpi = image.info.get("dpi")
        if dpi is None or min(dpi) <= 300:
            raise RuntimeError(f"PNG DPI metadata is not above 300: {dpi}")

    print(f"SVG: {SVG_PATH}")
    print(f"PNG: {PNG_PATH}")


if __name__ == "__main__":
    main()
