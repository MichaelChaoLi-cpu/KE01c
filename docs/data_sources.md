# KE01c Initial Data Sources

## Event scope

The study concerns the Kumamoto earthquake beginning on 2026-07-28. Event
reports and operational observations must be stored as dated snapshots because
official totals and webpages continue to change after publication.

## Working evidence chain

1. Observed shaking and secondary hazards alter ignition conditions and the
   availability of roads, water, and fire-service resources.
2. Building density, spacing, land use, and firebreaks determine conditional
   spread potential when an ignition is imposed.
3. Road access, response-base redundancy, and bounded water-availability
   scenarios determine nominal firefighting service under disruption.
4. Population and critical facilities determine potential consequences.
5. The primary decision comparison is the marginal protection benefit of a
   stated intervention, such as road restoration, a temporary water point, or
   response-unit pre-positioning.

Observed 2026 fires are context and possible validation evidence. They are not
the sample frame for the prefecture-wide screening model.

## Reused project assets

Reusable GeoParquet files from KE01 and KE01b are copied into
`data/raw/prior_projects/` as immutable external inputs. The source repositories
remain read-only. `src/data/acquire_prior_project_assets.py` verifies that every
destination SHA-256 matches its source and writes the full provenance record to
`data/raw/prior_projects/source_manifest.json`.

| Component | Prior project | Initial analytical role | Main limitation |
|---|---|---|---|
| 125 m population and disclosure groups | KE01 | Population and older-population exposure | 2020 baseline; disclosure groups are not exact household locations |
| GSI building polygons | KE01 | Building coverage, spacing, continuity, and possible firebreak geometry | No material, age, use, occupancy, or damage status |
| Shelters and evacuation sites | KE01 | Critical-facility and evacuation context | Designation does not verify post-event operation |
| 2026 damage and service snapshots | KE01 | Observed event context and scenario constraints | Mixed times and geographic resolutions; incomplete coverage |
| Medical, welfare, school, and public facilities | KE01 | Critical-facility exposure | Reference years differ and post-event operation is unknown |
| Administrative areas | KE01b | Clipping and municipality reporting | Boundary vintage differs from some layers |
| Road centerlines and emergency roads | KE01b | Routable response network and restoration candidates | No ready-made topology, observed speed, or verified 2026 passability |
| Fire stations, jurisdictions, and aggregate validation | KE01b | Nominal response bases and service areas | 2012 point roster; no current station-level vehicles or staffing |
| Landslide-warning zones | KE01b | Secondary-hazard road-disruption screening | Warning zones do not prove observed failure |

## New MLIT KSJ sources

The first-pass MLIT bundle is intentionally limited to layers that directly
change fire-spread or firebreak interpretation. It is acquired by
`src/data/acquire_mlit_fire_screening_sources.py`, stored under
`data/raw/mlit_ksj/fire_screening/`, and checksum-recorded in its source
manifest.

| Dataset | Reference year | Role | Status and limitation |
|---|---:|---|---|
| A55 urban-planning decision information, Kumamoto Prefecture | 2024 | Fire/pre-fire-prevention districts, zoning, urban parks, and planned roads | Acquired; approximate planning boundaries and incomplete local-government coverage are possible |
| L03-b-u 100 m urban land-use meshes 4829, 4830, 4831, 4930, and 4931 | 2021 | Dense low-rise, low-rise, factory, road, park/open-space, and water classes | Acquired; interpreted land use is not observed building combustibility |

Official catalogue pages:

- <https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-A55-2024.html>
- <https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-L03-b-u-v3_1.html>

## Source tiers for the fire study

### Tier A: minimum viable screening

- Copied population, building, road, fire-station, administrative, hazard, and
  critical-facility assets.
- A55 fire-prevention, zoning, park, and planned-road polygons.
- L03-b-u dense-low-rise, factory, road, green-space, and water classes.
- JMA observed shaking and event-window wind observations.
- Time-stamped 2026 official road, utility, damage, and emergency-response
  updates where available.

Tier A supports prefecture-wide conditional spread, nominal response-access,
exposure, and intervention screening. It does not establish actual ignition
probability or real firefighting capacity.

### Tier B: spatial refinement and robustness

- PLATEAU building attributes in covered municipalities.
- GSI elevation and water features where slope or alternative-water proximity
  is retained in the final design.
- Current municipal fire-station verification and publicly documented equipment
  totals.
- Alternative road-blockage, wind, ignition-seed, grid-size, and indicator
  definitions.

### Tier C: request or manually verify

- Geocoded hydrants, fire cisterns, usable open-water intakes, storage, flow,
  pressure, and post-event availability.
- Water-network topology, pipe damage, outage footprints, and restoration time.
- Station-level engines, tankers, crews, fuel, damage, and mutual-aid status.
- Computer-aided dispatch or incident records with alarm, dispatch, arrival,
  control, and extinguishment times.
- Geocoded 2026 fire incidents and verified building damage for external checks.

These data are required before results are described as actual water-supply,
dispatch-capacity, or operational-response gaps.

## Deferred MLIT datasets

- P13 urban parks is from 2011 and point-based; A55 provides newer planning
  polygons and is preferred.
- P07 fuel stations is from 2016 and non-commercial; it is not included in the
  first pass because current completeness and licensing would complicate use.
- W05 rivers is useful only if alternative-water access becomes a confirmed
  research variable; proximity alone does not establish usable firefighting
  supply.
- Additional national-scale datasets are excluded until a stated research
  question requires them.

## Interpretation boundary

The first-pass data architecture separates observed event context, modelled
conditional fire behaviour, nominal response accessibility, and planning
interventions. Missing operational data are represented by explicit scenarios
or left unestimated; they are never coded as zero.
