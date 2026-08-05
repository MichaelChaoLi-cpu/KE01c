#!/usr/bin/env python3
"""Acquire selected official MLIT KSJ inputs for urban-fire screening.

The bundle is intentionally narrow: current urban-planning decision layers and
2021 100 m urban land-use meshes covering Kumamoto. Downloads are immutable,
resumable, checksum-recorded, and extracted without altering source archives.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "data" / "raw" / "mlit_ksj" / "fire_screening"
USER_AGENT = "KE01c-post-earthquake-urban-fire-research/1.0"
EXTRACT_SUFFIXES = {
    ".cpg",
    ".csv",
    ".dbf",
    ".geojson",
    ".gml",
    ".prj",
    ".shp",
    ".shx",
    ".xml",
    ".xsd",
}


@dataclass(frozen=True)
class Source:
    key: str
    title: str
    url: str
    filename: str
    role: str
    reference_year: str
    license: str
    limitation: str


SOURCES = (
    Source(
        "mlit_ksj_a55_2024_kumamoto",
        "Urban planning decision information, Kumamoto Prefecture",
        "https://nlftp.mlit.go.jp/ksj/gml/data/A55/A55-24/A55-24_43000_GEOJSON.zip",
        "A55-24_43000_GEOJSON.zip",
        "Fire-prevention districts, land-use zoning, urban parks, and planned roads.",
        "2024",
        "CC BY 4.0",
        "Approximate planning boundaries; local-government records remain authoritative.",
    ),
    Source(
        "mlit_ksj_l03bu_2021_4829",
        "100 m urban land-use mesh 4829",
        "https://nlftp.mlit.go.jp/ksj/gml/data/L03-b-u/L03-b-u-21/L03-b-u-21_4829-jgd2011_GML.zip",
        "L03-b-u-21_4829-jgd2011_GML.zip",
        "Dense low-rise, factory, road, park, open-space, and water land-use classes.",
        "2021",
        "CC BY 4.0",
        "Satellite/map interpretation at 100 m; not a building-material observation.",
    ),
    Source(
        "mlit_ksj_l03bu_2021_4830",
        "100 m urban land-use mesh 4830",
        "https://nlftp.mlit.go.jp/ksj/gml/data/L03-b-u/L03-b-u-21/L03-b-u-21_4830-jgd2011_GML.zip",
        "L03-b-u-21_4830-jgd2011_GML.zip",
        "Dense low-rise, factory, road, park, open-space, and water land-use classes.",
        "2021",
        "CC BY 4.0",
        "Satellite/map interpretation at 100 m; not a building-material observation.",
    ),
    Source(
        "mlit_ksj_l03bu_2021_4831",
        "100 m urban land-use mesh 4831",
        "https://nlftp.mlit.go.jp/ksj/gml/data/L03-b-u/L03-b-u-21/L03-b-u-21_4831-jgd2011_GML.zip",
        "L03-b-u-21_4831-jgd2011_GML.zip",
        "Dense low-rise, factory, road, park, open-space, and water land-use classes.",
        "2021",
        "CC BY 4.0",
        "Satellite/map interpretation at 100 m; not a building-material observation.",
    ),
    Source(
        "mlit_ksj_l03bu_2021_4930",
        "100 m urban land-use mesh 4930",
        "https://nlftp.mlit.go.jp/ksj/gml/data/L03-b-u/L03-b-u-21/L03-b-u-21_4930-jgd2011_GML.zip",
        "L03-b-u-21_4930-jgd2011_GML.zip",
        "Dense low-rise, factory, road, park, open-space, and water land-use classes.",
        "2021",
        "CC BY 4.0",
        "Satellite/map interpretation at 100 m; not a building-material observation.",
    ),
    Source(
        "mlit_ksj_l03bu_2021_4931",
        "100 m urban land-use mesh 4931",
        "https://nlftp.mlit.go.jp/ksj/gml/data/L03-b-u/L03-b-u-21/L03-b-u-21_4931-jgd2011_GML.zip",
        "L03-b-u-21_4931-jgd2011_GML.zip",
        "Dense low-rise, factory, road, park, open-space, and water land-use classes.",
        "2021",
        "CC BY 4.0",
        "Satellite/map interpretation at 100 m; not a building-material observation.",
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(source: Source, destination: Path) -> str:
    if destination.is_file() and destination.stat().st_size > 0:
        return "existing"
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    temporary.unlink(missing_ok=True)
    request = urllib.request.Request(source.url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response, temporary.open("wb") as out:
        shutil.copyfileobj(response, out)
    if temporary.stat().st_size == 0:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"Empty download: {source.url}")
    temporary.replace(destination)
    return "downloaded"


def extract_selected(archive: Path, destination: Path) -> list[str]:
    destination.mkdir(parents=True, exist_ok=True)
    extracted: list[str] = []
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            if member.is_dir():
                continue
            basename = Path(member.filename).name
            if not basename or Path(basename).suffix.lower() not in EXTRACT_SUFFIXES:
                continue
            target = destination / basename
            with bundle.open(member) as source, target.open("wb") as out:
                shutil.copyfileobj(source, out)
            extracted.append(str(target.relative_to(PROJECT_ROOT)))
    return sorted(set(extracted))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    raw_root = root / RAW_ROOT.relative_to(PROJECT_ROOT)
    downloads = raw_root / "downloads"
    extracted_root = raw_root / "extracted"

    records: list[dict[str, object]] = []
    for source in SOURCES:
        archive = downloads / source.filename
        status = download(source, archive)
        extracted = extract_selected(archive, extracted_root / source.key)
        records.append(
            {
                **asdict(source),
                "downloaded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "local_path": str(archive.relative_to(root)),
                "bytes": archive.stat().st_size,
                "sha256": sha256(archive),
                "status": status,
                "extracted_files": extracted,
            }
        )
        print(f"{source.key}: {status} ({archive.stat().st_size:,} bytes)")

    manifest_path = raw_root / "source_manifest.json"
    manifest_path.write_text(
        json.dumps({"schema_version": 1, "sources": records}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(f"manifest: {manifest_path.relative_to(root)}")


if __name__ == "__main__":
    main()
