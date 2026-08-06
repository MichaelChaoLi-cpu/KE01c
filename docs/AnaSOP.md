# AnaSOP
Analysis Standard Operating Procedure

## 1. Research Objective

### Central Research Question

- Research question: Under event-specific post-earthquake road and water-supply disruption scenarios, how do grid-level conditional fire consequences and full-system dependence on individual fire bases vary across Kumamoto Prefecture, how stable are those results under length-dependent and spatially correlated road-section failures, and how can the combined evidence guide limited firefighting-resource placement after the earthquake beginning on 2026-07-28?
- Why it matters: A risk surface alone does not reveal which response bases are difficult to replace within the represented access network or which intervention produces the largest modelled protection gain. Joint estimation connects spatial screening to an explicit allocation decision.
- Data support currently visible: The current evidence covers building footprints, 125 m population exposure, 390,234 section-linked routable road edges, 343,844 junction-to-junction road sections, calibrated stochastic-failure inputs, nominal fire-service locations and jurisdictions, urban land use, fire-prevention and open-space features, critical facilities, secondary hazards, and event-specific damage and service-disruption context.
- Key readable variables or data scope: building coverage and continuity, building separation, land-use class, firebreak proximity, population and older-population exposure, critical-facility exposure, road class and width, station-to-demand travel time, backup-station count, route dependence, Road Section ID, Road Section Length (m), Timely Response Probability, and bounded water-availability scenarios.
- What would verify it: The analysis must produce spatially coherent conditional consequence estimates, reproducible leave-one-fire-base-out accessibility losses across event-specific and documented stochastic sensitivity scenarios, and measurable reductions in weighted exposure or response penalties under at least one feasible intervention.
- What would falsify or weaken it: The central claim would be weakened if road topology cannot support credible routing, stochastic results are dominated by implausibly long road sections, fire-base criticality is dominated by unverified facility records, cell priorities are unstable across reasonable spread definitions, or intervention priorities reverse under modest scenario or cost-proxy changes.
- Required next feasibility check: Retain the compact non-identifying priority critical-facility table for class, municipality, and mesh-level screening only; do not interpret it as a facility-specific action list.

### Supporting Research Questions

#### Supporting Point 1

- Role relative to central point: mechanism
- Research question: Which populated 125 m cells have the greatest conditional fire-spread susceptibility and consequence when ignition is imposed rather than predicted?
- Why it matters: Separating conditional spread and consequence from ignition probability avoids presenting an unsupported probability of a specific building burning.
- Data support currently visible: Building geometry, population exposure, urban land use, roads, parks, water and other potential firebreaks, critical facilities, and event damage context support relative spatial screening.
- Key readable variables or data scope: building density, continuous built-up area, separation distance, building area, surrounding road and open-space width, dense-low-rise and industrial land use, exposed population, and exposed critical facilities.
- What would verify it: High-ranked cells should remain relatively high under alternative component weights, adjacency thresholds, firebreak definitions, scaling methods, and cell-assignment rules.
- What would falsify or weaken it: Results that are primarily determined by one arbitrary weight or that cannot distinguish dense urban clusters from clearly separated development would undermine the measure.
- Required feasibility check: Complete the declared built-form and consequence ablations; wind and building material remain outside the current data-supported scope.

#### Supporting Point 2

- Role relative to central point: mechanism and robustness
- Research question: How do event-specific bounded road disruptions change nominal response time, backup coverage, and single-route dependence for high-consequence locations, and how reliable are those outcomes under additional length-dependent and spatially correlated road-section failures?
- Why it matters: Normal-condition proximity can overstate response capability when bridges, narrow roads, landslide-prone links, or key emergency routes become unavailable.
- Data support currently visible: A prefecture-wide road network, emergency transport routes, fire-service locations, administrative coverage, and secondary-hazard zones support scenario-based accessibility analysis.
- Key readable variables or data scope: shortest travel time, number of stations within stated thresholds, second-best travel time, edge and route criticality, road class and width, emergency-route status, hazard-intersection indicators, Road Section ID, Road Section Length (m), Expected Failed Road Length Share, and Timely Response Probability.
- What would verify it: Event-specific disruption scenarios should identify reproducible increases in travel time and losses of backup coverage, while 1%, 3%, and 5% expected failed-road-length sensitivities and a 10% stress case should reveal whether conclusions remain stable under additional road uncertainty.
- What would falsify or weaken it: Poor network connectivity, excessive snapping error, or implausible normal-condition travel times would make the accessibility comparison unreliable.
- Required feasibility check: Preserve the completed event-specific and 1,000-replicate length-dependent results and the declared alternative-mechanism sensitivities. Complete road-section unavailability remains a deliberate conservative rescue-safety boundary rather than a claim of continuous physical damage.

#### Supporting Point 3

- Role relative to central point: system-dependence application
- Research question: How much does accessibility-supported protection deteriorate when each eligible fire base is removed from the otherwise available response system, and which bases remain difficult to replace across alternative road and demand scenarios?
- Why it matters: Station proximity and jurisdiction size do not measure substitutability. Leave-one-fire-base-out loss directly shows how much the represented system depends on a base when all other eligible bases remain available.
- Data support currently visible: Nominal response-base locations, road accessibility, population and critical-facility demand, and scenario-specific conditional consequences support deterministic fire-base removal contrasts.
- Key readable variables or data scope: `Candidate Dispatch Base`, `Leave-One-Out Fire Base Value`, `Leave-One-Out Fire Base Value Share`, weighted response-penalty increase, population and critical facilities affected, backup-base loss, and variation across declared road scenarios.
- What would verify it: Removal losses should be nonnegative, reproducible, spatially coherent, and retain interpretable magnitude and high-criticality membership across normal roads, event-specific roads, exposure objectives, and multiple declared stochastic road states.
- What would falsify or weaken it: Results would weaken if station records are not valid response origins, network topology creates implausible substitution patterns, or high-criticality membership changes arbitrarily under modest routing or demand specifications.
- Required feasibility check: Preserve the completed deterministic leave-one-out estimates and multi-state stability results; report scenario-sensitive membership without using Shapley or another coalition-allocation estimator.

#### Supporting Point 4

- Role relative to central point: decision application
- Research question: Which combination of response-unit pre-positioning, temporary water support, and priority road restoration produces the largest robust reduction in weighted conditional fire consequence?
- Why it matters: The practical objective is not merely to rank risky places or stations, but to compare feasible actions under limited resources.
- Data support currently visible: The integrated risk, access, exposure, road, and station layers support counterfactual comparisons; water interventions can initially be represented only by explicit boundary scenarios.
- Key readable variables or data scope: population and critical facilities returned to response thresholds, reduction in response delay, redundancy restored, conditional consequence reduced, Road Section ID, Road Section Length (m), Road Restoration Cost Proxy, intervention unit count, and performance across scenarios.
- What would verify it: Recommended interventions should outperform simple baselines such as population-only placement, nearest-station placement, or restoration of the highest road class, and should remain useful across multiple scenarios.
- What would falsify or weaken it: Recommendations that depend on unavailable operational attributes or reverse under minor scenario changes should be reported as indeterminate rather than optimal.
- Required feasibility check: Preserve the completed 100-state fixed-plan road-restoration evaluation. Candidate staging-site and bounded-water-support results remain event-specific screens and must not be described as multi-state robust.

### Scope of Analysis

- Topics: post-earthquake conditional urban-fire consequence, response accessibility, leave-one-fire-base-out system dependence, infrastructure redundancy, and resource-allocation robustness.
- Units of analysis: 125 m populated grids for prefecture-wide screening; individual buildings as morphology inputs within selected high-priority urban clusters; eligible fire bases for one-base removal contrasts; routable road edges for deterministic event scenarios; and junction-to-junction road sections for stochastic failure and restoration sensitivity.
- Geographic scope: Kumamoto Prefecture; building footprints supply morphology inputs, but reported consequence and priority outcomes remain at the populated 125 m cell level.
- Event scope: The earthquake sequence beginning on 2026-07-28 provides the observed disruption context. The study is a spatial scenario assessment and does not analyze temporal ordering or disorder.
- Validation scope: The eight reported fires may be used only for limited external plausibility checks, not as a training sample or the study population.

### Study Design Declaration

- Research type: applied
- Study design: Event-specific spatial scenario analysis combining conditional fire-consequence screening, network accessibility, leave-one-fire-base-out system-dependence estimation, and counterfactual intervention comparison, with a separate nested Monte Carlo road-section reliability layer for robustness.
- Interpretation limit: Results are not causal estimates, specific-building ignition probabilities, forecasts of actual burned area, or measurements of real-time dispatch capacity. Until station-level vehicles and staffing, hydrant functionality, water-network performance, building materials, and observed road passability are verified, results must be described as conditional, nominal, accessibility-based, or scenario-based.

## 2. Theoretical Background  /  Conceptual Framework  /  Problem Formulation

- Research type: applied
- Section focus: Empirical context, operational interdependence, and cautious decision support under incomplete post-event information.

### Research Gap

- Existing spatial fire-risk screening can identify dense or exposed urban areas, while accessibility studies can identify nominal service gaps. Neither output alone measures how much accessibility-supported protection is lost when one response base is unavailable, nor directly connects that system dependence to resource-allocation choices.
- The applied gap is therefore an integrated, event-specific framework that links conditional fire consequences, disrupted network accessibility, leave-one-fire-base-out criticality, and intervention benefit while explicitly distinguishing observed conditions from imposed scenarios.
- This gap statement is provisional and requires a later primary-literature review; it is not yet a claim of novelty.

### Conceptual Framework

- Earthquake-related shaking and secondary hazards define the event context and plausible disruption scenarios. They do not determine a building-specific ignition probability in the current design.
- Built-form continuity, separation, land use, and firebreaks determine conditional spread susceptibility once an ignition is imposed. Population and critical facilities determine consequence weights.
- Roads connect response bases to demand locations. Link disruption can increase travel time, remove backup coverage, and change how strongly the full represented system depends on a station even when the station itself remains operational.
- The event-specific network state remains the primary planning contrast. Length-dependent independent failures, spatially clustered failures, and hazard-weighted failures are separate robustness mechanisms; none is interpreted as the observed probability that a 2026 road section failed.
- Fire bases are treated as nominal response origins in one full represented system. Their criticality is the increase in stated system loss after removing one eligible base while retaining every other eligible base.
- Resource interventions modify the station set, effective access network, or bounded water-support condition. Their value is measured by the reduction in weighted conditional consequence relative to explicit baselines. Road restoration is evaluated at the road-section level, while section length or event-exposed length is retained as a cost proxy rather than treating every section as operationally equivalent.
- Scope boundary: The framework estimates spatial susceptibility, nominal accessibility, stochastic reliability under declared failure mechanisms, and counterfactual planning value; it does not estimate engineering fragility, actual real-time suppression capacity, repair duration, or temporal fire evolution.

### Problem Formulation

- Let \(b\) denote a building or screening grid, \(S\) a set of available fire stations, and \(\omega\) a stated earthquake-disruption and ignition scenario. Conditional consequence is represented as

\[
C_b(S, \omega) = g(Spread_b(\omega), Access_b(S, \omega), Water_b(\omega), Exposure_b),
\]

  where the functional form \(g\) and all normalizations remain subject to feasibility and robustness testing.
- Define scenario-specific system loss for an available fire-base set as

\[
J_{\omega}(S) = \sum_b w_b C_b(S, \omega),
\]

  where \(J_{\omega}(S)\) is system loss under available base set \(S\), and \(w_b\) states the population, vulnerability, or critical-facility reporting weight assigned to location \(b\).
- For eligible fire base \(i\), leave-one-fire-base-out criticality is

\[
L_i(\omega) = J_{\omega}(N \setminus \{i\}) - J_{\omega}(N).
\]

  Here, \(N\) is the full eligible fire-base set and \(L_i(\omega)\) is the additional modelled loss caused by removing base \(i\) under scenario \(\omega\). The current source contains 94 facility records but only 81 records marked as candidate dispatch bases; headquarters records that are not dispatch candidates and co-located duplicates are excluded from the removal set. Every retained base is evaluated once per declared scenario and exposure objective.
- Scenario comparisons report the raw removal loss, its share of total leave-one-out loss within the same scenario-objective pair, and its variation across road states. Population, older-population, and critical-facility objectives remain separate rather than being collapsed into an unexplained universal station score.
- Interpretation limit: The eight reported fires are insufficient for supervised fire-risk training. Grid outputs are conditional scores, not calibrated probabilities. Leave-one-out criticality measures dependence of the represented full system on a base; it does not measure intrinsic station quality, real operational capacity, or causal impact.

## 3. Data Overview

### Data Scope

- Files reviewed: 43, comprising 19 immutable source inputs and 24 standardized analysis components. Source and standardized representations were both inspected, so the file count is not the number of independent evidence sources.
- Standardized records reviewed: 2,012,516 across the 24 analysis components. Component sizes range from 1 to 1,036,590 rows and from 3 to 20 retained columns.
- Variables summarized: 474 variable-file combinations.
- Distribution plots generated in the current run: 80.
- Files skipped during briefing: 0.
- Geographic scope: Kumamoto Prefecture. Prefecture-wide screening and reporting use populated 125 m cells; building footprints are morphology inputs rather than prediction units.

| Analysis component | Observation or geometry unit | Standardized rows | Reference period | Coverage and analytical role |
|---|---|---:|---|---|
| Administrative reporting | municipality or ward polygon | 49 | mixed boundary vintage | Prefecture-wide clipping, aggregation, and reporting |
| Building form | building footprint polygon | 1,036,590 | pre-event static reference | Coverage, separation, and continuity; no material, age, occupancy, or damage status |
| Population exposure | populated 125 m cell and disclosure-group polygon | 62,945 cells and 36,657 groups | 2020 | Population and older-population exposure; disclosure protection limits household precision |
| Road accessibility | source road segment, routable edge, emergency-route segment, and junction-to-junction section | 430,201 source segments, 390,234 section-linked routed edges, 343,844 road sections, and 264 emergency-route segments | 2024 | Nominal routing, bounded event-specific scenarios, section-aware stochastic failure, and section-level restoration variables are available and validated for the retained analyses |
| Fire-service supply | response-base point, jurisdiction polygon, and organization reference | 94 bases, 1,823 jurisdiction records, and 1 organization record | 2012 base roster with later contextual records | Nominal service origins and reporting context; 81 records are eligible candidate dispatch bases |
| Critical facilities | shelter, evacuation-site, medical, welfare, school, and public-facility point | 12,636 combined records | mixed pre-event reference years | Exposure screening; designation does not verify post-event operation or capacity |
| Secondary hazards | warning-zone polygon | 56,424 | 2025 | Bounded road-disruption screening; warning status does not establish observed road failure |
| Urban land use | 100 m mesh polygon | 371,094 | 2021 | Dense-low-rise, factory, road, green-space, and water context; not building combustibility |
| Urban planning controls | fire-prevention, zoning, park, and planned-road geometry | 14, 1,255, 709, and 1,732 | 2024 | Firebreak and planning context; local-government coverage may be incomplete |
| Event evidence | damage, housing, and service-disruption snapshot record | 9, 5, and 14 | 2026-07-28 to 2026-08-02 observation window | Event context and scenario bounds; mixed observation times and geographic resolutions |

### Missingness and Candidate Screening

- Of 474 variable-file combinations, 376 have no missing observations and 50 have missingness of at least 80 percent. Missing source values remain missing and are not interpreted as zero.
- The automated screen identified 117 numeric candidates, 121 categorical candidates, 27 identifier-like fields, 91 text or high-cardinality fields, 91 constant or empty fields, 14 time candidates, and 13 fields whose primary screening label is high missingness.
- Distribution plots are exploratory diagnostics rather than study findings. Binary geometry is summarized as spatial metadata and is not plotted as a categorical value.

### Temporal Treatment

- Time-like metadata were detected in 14 files, including event observation times and source reference dates or years.
- By explicit research-scope decision, no time-series visualization, temporal ordering model, disorder analysis, or event-sequence inference will be performed.
- Time-like fields may be retained only to document source vintage and the observation window. The analytical design remains a cross-sectional spatial scenario assessment.

### Data Limitations

- No skipped files were recorded by the briefing script.
- Standardized spatial layers retain two geographic coordinate reference systems. They must be harmonized and projected before area, distance, adjacency, or routing calculations.
- Reference periods differ across population, station, road, facility, hazard, land-use, and planning components. They are not treated as contemporaneous measurements of post-earthquake operating conditions.
- Event snapshots have mixed times and geographic resolutions and do not define a complete temporal panel.
- Current data do not verify station-level vehicles or staffing, hydrant functionality, water-network performance, building material, wind fields, or observed road passability.
- Current data do not provide engineering road-fragility probabilities, repair duration or cost, or an empirically calibrated spatial-correlation model for 2026 road failures. Length-dependent, clustered, and hazard-weighted failures are therefore sensitivity mechanisms rather than observed event probabilities.
- Junction-to-junction sections may contain very long rural chains. Before section-level reliability or restoration results are final, the upper tail of `Road Section Length (m)` and connector behavior under full-section versus local-fragment closure must be audited.
- The eight reported fires remain limited plausibility evidence and are not a supervised-learning sample.
- This section is exploratory. Final readable-variable definitions and inclusion decisions belong to Section 4.
- AnaSOP intentionally omits raw dataset names, source file paths, original column names, and exploratory-output paths.

## 4. Variable Construction  /  Key Variables

The table separates standardized source inputs from planned derived analysis variables. Repeated readable names used consistently across spatial layers are documented once.

| variable_name | full_name | role | formal_definition | construction_or_coding | is_final_variable |
|---|---|---|---|---|---|
| Shelter ID | Shelter Identifier | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Same Address as Emergency Evacuation Site | Same Address as Emergency Evacuation Site | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Geometry | Geometry | spatial key | Spatial geometry with active GeoParquet metadata and a declared CRS. | Active geometry retained; source CRS preserved, with MLIT logical layers harmonized to EPSG:6668. | yes |
| Evacuation Site ID | Evacuation Site Identifier | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Earthquake Designation | Earthquake Designation | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Large-Scale Fire Designation | Large-Scale Fire Designation | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Same Address as Designated Shelter | Same Address as Designated Shelter | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Building ID | Building Identifier | spread explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Building Feature Code | Building Feature Code | spread explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Building Area (m2) | Building Area (m2) | spread explanatory | Source building-footprint area in square metres. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Medical Facility ID | Medical Facility Identifier | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Medical Institution Class | Medical Institution Class | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Bed Count | Bed Count | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Emergency Hospital Designation | Emergency Hospital Designation | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Disaster Base Hospital Class | Disaster Base Hospital Class | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Public Facility ID | Public Facility Identifier | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Public Facility Class | Public Facility Class | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| School Facility ID | School Facility Identifier | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| School Code | School Code | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| School Class | School Class | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Suspension Status | Suspension Status | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Welfare Facility ID | Welfare Facility Identifier | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Welfare Facility Major Class | Welfare Facility Major Class | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Welfare Facility Medium Class | Welfare Facility Medium Class | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Welfare Facility Minor Class | Welfare Facility Minor Class | critical-facility exposure | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Disclosure Group Code | Disclosure Group Code | identifier / reporting key | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Disclosure Group Size | Disclosure Group Size | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Total Population | Total Population | exposure / vulnerability | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Total Households | Total Households | exposure / vulnerability | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| General Households | General Households | exposure / vulnerability | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Population Age 65+ | Population Age 65+ | exposure / vulnerability | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Population Age 75+ | Population Age 75+ | exposure / vulnerability | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Population Age 85+ | Population Age 85+ | exposure / vulnerability | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| One-Person Households | One-Person Households | exposure / vulnerability | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Households with Member Age 65+ | Households with Member Age 65+ | exposure / vulnerability | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Older Single-Person Households | Older Single-Person Households | exposure / vulnerability | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Older Couple Households | Older Couple Households | exposure / vulnerability | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Population Age 65+ Share | Population Age 65+ Share | exposure / vulnerability | \(PopulationAge65Plus / TotalPopulation\). | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Population Age 75+ Share | Population Age 75+ Share | exposure / vulnerability | \(PopulationAge75Plus / TotalPopulation\). | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Population Age 85+ Share | Population Age 85+ Share | exposure / vulnerability | \(PopulationAge85Plus / TotalPopulation\). | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Older Single-Person Household Share | Older Single-Person Household Share | exposure / vulnerability | \(OlderSinglePersonHouseholds / TotalHouseholds\). | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Older Couple Household Share | Older Couple Household Share | exposure / vulnerability | \(OlderCoupleHouseholds / TotalHouseholds\). | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Mesh Code | Mesh Code | identifier / reporting key | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Disclosure Status | Disclosure Status | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Aggregation Destination Mesh Code | Aggregation Destination Mesh Code | identifier / reporting key | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Aggregated Source Mesh Codes | Aggregated Source Mesh Codes | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Geographic Level | Geographic Level | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Municipality | Municipality | identifier / reporting key | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Disruption Type | Disruption Type | scenario input | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Service Status | Service Status | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Reported Municipality Count | Reported Municipality Count | identifier / reporting key | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Reported Affected Households | Reported Affected Households | exposure / vulnerability | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Reported Affected People | Reported Affected People | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Observed Power Outage Customers | Observed Power Outage Customers | scenario input | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Observed Water Outage Households | Observed Water Outage Households | exposure / vulnerability | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Evidence Tier | Evidence Tier | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Verification Status | Verification Status | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Municipality Code | Municipality Code | identifier / reporting key | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Municipality Name | Municipality Name | identifier / reporting key | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Ward Name | Ward Name | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Municipality Label | Municipality Label | identifier / reporting key | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Emergency Road Class Code | Emergency Road Class Code | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Emergency Road Type Code | Emergency Road Type Code | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Route ID | Route Identifier | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Branch ID | Branch Identifier | identifier / reporting key | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Emergency Road Service Status | Emergency Road Service Status | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Emergency Road Class | Emergency Road Class | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Emergency Road Type | Emergency Road Type | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Fire Base Name | Fire Base Name | response supply | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Fire Base Type Code | Fire Base Type Code | response supply | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Fire Base Type | Fire Base Type | response supply | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Candidate Dispatch Base | Candidate Dispatch Base | response supply | Boolean source classification used to retain eligible nominal response origins. | Retain source Boolean; 81 of 94 facility records are eligible candidate dispatch bases. | yes |
| Hazard Type Code | Hazard Type Code | scenario input | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Warning Zone Class Code | Warning Zone Class Code | scenario input | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Zone ID | Zone Identifier | identifier / reporting key | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Special Warning Zone Pending Code | Special Warning Zone Pending Code | scenario input | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Hazard Type | Hazard Type | scenario input | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Warning Zone Class | Warning Zone Class | scenario input | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Special Warning Zone Pending | Special Warning Zone Pending | scenario input | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Road Centerline Type Code | Road Centerline Type Code | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Road Category Code | Road Category Code | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Road State Code | Road State Code | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Vertical Level | Vertical Level | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Width Category Code | Width Category Code | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Road Centerline Type | Road Centerline Type | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Road Category | Road Category | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Road State | Road State | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Width Category | Width Category | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Fire Prevention Area Type | Fire Prevention Area Type | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Fire Prevention Area Code | Fire Prevention Area Code | identifier / reporting key | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Land Use Zone Name | Land Use Zone Name | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Land Use Zone Code | Land Use Zone Code | identifier / reporting key | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Floor Area Ratio | Floor Area Ratio | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Permitted Building Coverage Ratio | Permitted Building Coverage Ratio | spread explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Park Type | Park Type | supporting explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Park Code | Park Code | identifier / reporting key | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Planned Road Type | Planned Road Type | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Planned Road Code | Planned Road Code | accessibility explanatory | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Urban Land Use Mesh Code | Urban Land Use Mesh Code | identifier / reporting key | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Urban Land Use Code | Urban Land Use Code | identifier / reporting key | Source-defined value retained without numerical transformation or missing-value imputation. | Selected and assigned a confirmed English readable name; surrounding whitespace stripped for text fields. | yes |
| Road Section ID | Junction-to-Junction Road Section Identifier | accessibility and intervention unit | Unique identifier for one maximal continuous same-level road chain between true junctions. | Transferred into the project as a read-only upstream-derived attribute and validated against every retained routable edge. | yes |
| Road Section Length (m) | Junction-to-Junction Road Section Length | failure exposure and cost proxy | Total routed length over all internal edges assigned to one Road Section ID. | Summed from Road Length (m) within each Road Section ID; edge-to-section length equality and upper-tail quantiles were validated. | yes |
| Road Edge Count | Internal Routable Edge Count per Road Section | topology diagnostic | Number of internal routable edges assigned to one Road Section ID. | Counted within Road Section ID and validated against the section table. | yes |
| Route Name | Human-Readable Road Route Name | accessibility descriptor | Route name attached to a routable edge or road section when source matching is available. | Retained after whitespace stripping; unmatched route names remain missing and are not imputed. | yes |
| Road Failure Model | Declared Road-Section Failure Mechanism | robustness scenario input | Named mechanism used to generate a stochastic road state. | `Length-Dependent Independent` is finalized for the calibrated input table; Spatially Clustered and Hazard-Weighted remain analysis-stage alternatives. | yes |
| Expected Failed Road Length Share | Target Expected Unavailable Road-Length Share | robustness severity input | Target share \(d\) of total eligible Road Section Length (m) expected to be unavailable under a declared failure model. | Finalized levels are 0.5%, 1%, 3%, 5%, and 10%; the first is a near-baseline check and the last is a stress case. | yes |
| Failure Intensity per Metre | Calibrated Road Failure Intensity per Metre | robustness parameter | Positive parameter \(\lambda_d\) calibrated so length-weighted expected section closure equals severity \(d\). | Numerically calibrated over all 343,844 eligible positive-length road sections for each finalized severity. | yes |
| Section Failure Probability | Scenario-Specific Road-Section Failure Probability | robustness scenario input | \(q_s(\lambda_d)=1-\exp(-\lambda_d L_s)\), where \(L_s\) is Road Section Length (m). | Constructed for each Road Section ID and finalized severity under the Length-Dependent Independent mechanism; it is not an engineering or observed-event probability. | yes |
| Road Section Failure Indicator | Replicate-Specific Road-Section Closure Indicator | robustness treatment | \(Z_{srd}=\mathbf{1}[U_{sr}<q_s(\lambda_d)]\) for road section \(s\), replicate \(r\), and severity \(d\). | Generated from deterministic seeds; shared scores preserve nested severity states within replicate. | yes |
| Simulation Replicate | Stochastic Road-State Replicate Identifier | robustness identifier | Integer index for one reproducible stochastic road-state draw. | Generated with deterministic seeds and retained at declared convergence checkpoints. | yes |
| Realized Failed Road Length Share | Realized Unavailable Road-Length Share | robustness diagnostic | Total Road Section Length (m) over failed sections divided by total eligible section length in one replicate. | Calculated for every retained stochastic state and compared with the target severity. | yes |
| Timely Response Probability | Probability of Nominal Fire-Service Response within Threshold | accessibility reliability outcome | Monte Carlo mean of the indicator that minimum fire-service response time does not exceed a declared threshold. | Estimated separately by Road Failure Model, Expected Failed Road Length Share, and response threshold. | yes |
| P90 Response Time (min) | Ninetieth-Percentile Nominal Fire-Service Response Time | accessibility reliability outcome | Empirical 90th percentile of minimum response time across stochastic road states; grids with at least 10% disconnection are reported as unreachable for the unconditional percentile, and connected-only summaries must be labelled explicitly. | Estimated from retained stochastic states; it is not an observed response-time percentile. | yes |
| Event-Exposed Road Length (m) | Event-Hazard-Exposed Length within Road Section | intervention exposure | Sum of internal Road Length (m) assigned to Warning Zone or Special Warning Zone exposure classes within one Road Section ID. | Constructed from edge-level event exposure and set to zero where no internal edge is event-exposed. | yes |
| Event-Exposed Road Length Share | Share of Road Section Length with Event-Hazard Exposure | intervention diagnostic | Event-Exposed Road Length (m) divided by Road Section Length (m). | Constructed without imputation; values are bounded from zero to one. | yes |
| Road Restoration Cost Proxy | Relative Road-Section Restoration Resource Requirement | intervention cost proxy | Event-Exposed Road Length (m) divided by the median positive event-exposed road-section length. | Constructed only for the 42,068 event-exposed sections; unaffected sections remain missing because observed repair duration and monetary cost are unavailable. | yes |
| Building Count | Building Count per Analysis Cell | spread explanatory | \(N_j = \sum_b 1(p_b \in j)\), where \(p_b\) is the building point-on-surface. | Building footprints are projected to EPSG:6670 and assigned to one populated 125 m cell by point-on-surface location. | yes |
| Observed Building Footprint Coverage Ratio | Observed Building Footprint Coverage Ratio | spread explanatory | \(BCR_j = \min\{1, \sum_b Area(b \cap j) / Area(j)\}\). | Exact footprint-cell intersections are calculated in EPSG:6670 and divided by cell area. | yes |
| Mean Building Separation (m) | Mean Nearest-Building Boundary Separation | spread explanatory | \(D_j = N_{j,valid}^{-1}\sum_{b:p_b\in j}\min_{k\ne b} dist(\partial b,\partial k)\) for buildings with a valid nearest neighbour. | Nearest building-boundary distances are calculated prefecture-wide in EPSG:6670, so the nearest neighbour may lie across a cell boundary. | yes |
| Built Continuity Index | Local Built-Form Continuity Index | spread explanatory | \(K_j = N_{j,\leq 6m}/N_{j,valid}\), the share of assigned buildings whose nearest building boundary is no more than 6 m away. | Constructed from the same prefecture-wide nearest-neighbour search; cells without a valid pair are set to zero. | yes |
| Firebreak Share | Mapped Road-Corridor and Open-Land Firebreak Share | spread protective | \(F_j = \min\{1,(A_j^{road}+A_j^{open})/Area(j)\}\). | Road centreline length is converted to corridor area using width-class values of 2, 4.25, 9.25, 16.25, or 22 m (unknown: 4 m); mapped open-land codes 0902, 1002, 1003, 1100, 1400, and 1500 are added by exact overlap. | yes |
| Conditional Spread Susceptibility | Conditional Fire-Spread Susceptibility | intermediate outcome | \(S_j=[R(BCR_j)+R(K_j)+1-R(D_j)+1-R(F_j)]/4\), where \(R\) is the empirical percentile transform. | Equal-weight grid screening score conditional on imposed ignition; cells with fewer than two buildings receive zero continuity rank, missing inverse-separation values are set to zero, and the score is not an ignition probability. | yes |
| Normal Response Time (min) | Normal-Scenario Minimum Fire-Service Travel Time | accessibility outcome | \(T_j^0 = \min_{i \in N} t_{ij}^0\), capped at 30 min when nominal service is unmet. | Shortest-path time from the 81 eligible candidate dispatch bases on the explicitly augmented normal road graph. | yes |
| Disrupted Response Time (min) | Disruption-Scenario Minimum Fire-Service Travel Time | accessibility outcome | \(T_j(\omega) = \min_{i \in N(\omega)} t_{ij}(\omega)\), capped at 30 min when nominal service is unmet. | Shortest-path time on the declared event-specific or stochastic road state after applying its link-availability rule. | yes |
| Backup Fire Base Count | Number of Alternative Candidate Dispatch Bases | accessibility redundancy | \(B_j(\omega)=\max\{0,\sum_i1[t_{ij}(\omega)\leq10]-1\}\). | Count of candidate bases beyond the nearest base that can reach the cell within the declared 10-minute threshold. | yes |
| Single Route Dependence | Shared Shortest-Route Dependence | accessibility vulnerability | For one qualifying base the value is 1; for multiple qualifying bases it is the largest number of their selected shortest paths sharing one road edge divided by the qualifying-base count. | Calculated on the event-specific graph for bases within 10 min; endpoint connector edges are excluded and cells without a qualifying route remain missing. | yes |
| Water Constraint Scenario | Bounded Firefighting Water-Availability Scenario | scenario input | Two-category boundary condition: `Normal-reliance boundary` or `Bounded water-unavailable stress`. | The stress category is assigned to cell centroids within Kumamoto Minami Ward; it is a scenario boundary and not observed hydrant or network failure. | yes |
| Conditional Fire Consequence | Weighted Conditional Fire Consequence | main outcome | \(C_j^{(o)}=S_jE_j^{(o)}(1+A_j+W_j)\); the base consequence layer sets \(W_j=0\), while the combined intervention stress sets \(W_j=1\) inside the bounded water-stress area. | Exposure \(E_j^{(o)}\) is defined separately for population, older population, and critical facilities; \(A_j\) is the accessibility penalty. The result is conditional on ignition, not a calibrated building-fire probability. | yes |
| Leave-One-Out Fire Base Value | Leave-One-Out Candidate Dispatch-Base Criticality | station criticality outcome | \(L_i^{(o)}(\omega) = J^{(o)}(N \setminus \{i\}, \omega) - J^{(o)}(N, \omega)\). | Deterministic increase in modelled system loss after removing one eligible base from the full represented system under one scenario and exposure objective. | yes |
| Leave-One-Out Fire Base Value Share | Scenario-Normalized Leave-One-Out Fire-Base Criticality Share | station criticality outcome | \(l_i^{(o)}(\omega)=L_i^{(o)}(\omega)/\sum_{k \in N}L_k^{(o)}(\omega)\) when the denominator is positive. | Used only for within-scenario comparison across eligible bases; zero-total-loss scenarios remain unidentified. | yes |
| Road-Scenario Leave-One-Out IQR | Across-Scenario Leave-One-Out Criticality Interquartile Range | station criticality robustness | Interquartile range of `Leave-One-Out Fire Base Value Share` across the declared road states for one base and exposure objective. | Reported as instability rather than subtracted from the central estimate; no universal composite station score is constructed. | yes |
| Intervention Benefit | Weighted Conditional-Consequence Reduction from Intervention | decision outcome | \(Benefit_a(\omega) = J_0(\omega) - J_a(\omega)\). | Constructed from the same event-specific baseline and post-action loss calculation; prioritized and simple-baseline results are compared within each action class and declared budget definition. | yes |
| Retained Protection Gain Share | Fixed-Plan Retained Intervention-Benefit Share | intervention robustness outcome | \(R_{\mathcal{A}}^{(o)}(\omega_r)=Benefit_{\mathcal{A}}^{(o)}(\omega_r)/Benefit_{\mathcal{A}}^{(o)}(\omega_{event})\) when the event-specific denominator is positive. | Select the road-restoration bundle under the event-specific road case, evaluate the same bundle unchanged across each predeclared 3% stochastic road state, and retain the ratio without clipping. | yes |
| Candidate Staging Site ID | Traceable Candidate Staging-Site Identifier | intervention identifier | Stable source-prefixed identifier for one mapped candidate site. | Retain the source facility identifier; use a geometry-derived stable identifier for an urban park without a suitable source identifier. | yes |
| Candidate Staging Site Type | Candidate Staging-Site Facility Class | intervention explanatory | Categorical source class of the mapped candidate site. | Classify as Emergency evacuation site, Designated shelter, Public facility, School, or Urban park. | yes |
| Candidate Staging Site Name | Source-Reported Candidate Staging-Site Name | intervention descriptor | Source-reported name of the mapped candidate site. | Retain the source name without translation or imputation; every selected site requires field verification. | yes |
| Candidate Source Status | Candidate Staging-Site Source Status | supporting descriptor | Source-reported designation, classification, or status retained for candidate screening and audit. | Retain the available source value without harmonizing it into an operational-readiness measure. | yes |
| Access Mesh Code | Staging-Site Routing Access Mesh | routing key | Identifier of the nearest populated demand mesh used to connect a candidate site to the road graph. | Match in EPSG:6670 within 250 m; the matched mesh must have an accepted network connector and a node in the central event graph. | yes |
| Staging-to-Mesh Distance (m) | Candidate-Site to Access-Mesh Distance | routing diagnostic | Euclidean distance from the mapped candidate point to its matched Access Mesh Code in EPSG:6670. | Retain only matches no greater than 250 m and report the distance without imputation. | yes |
| Staging Access Network Snap Distance (m) | Access-Mesh to Road-Network Snap Distance | routing diagnostic | Accepted road-network connector distance carried from the matched Access Mesh Code. | Use the validated demand-mesh connector; this is not a measured driveway or direct facility-access distance. | yes |
| Field Verification Required | Candidate Staging-Site Field-Verification Flag | interpretation boundary | Boolean flag that is true for every selected candidate staging site. | Indicates that parking, turning space, site safety, capacity, permission, fuel, communications, and staffing have not been operationally verified. | yes |
## 5. Identification Strategy

### Design Principle

The study uses model-based scenario contrasts rather than causal identification or supervised prediction. It holds the mapped built environment and exposed population fixed, varies explicitly declared road, fire-base, and water-support conditions, and measures the resulting change in conditional consequence. The event-specific bounded road and water conditions are the primary planning scenarios. Stochastic road-section failures form a separate robustness layer and are never used to assign an empirical probability to the 2026 event.

The primary consequence and accessibility unit is the populated 125 m cell. Individual building footprints contribute to cell-level coverage, separation, and continuity measures but are not a reporting or prediction unit in the streamlined output plan. Candidate dispatch bases are nominal response origins, and one-base removal from the full eligible set is the station-criticality contrast. Routable road edges retain travel impedance and connector positions, while junction-to-junction Road Section ID values define stochastic closures and section-level restoration sensitivity. The scenario set combines imposed ignition conditioning, event-specific network disruption rules, bounded water-availability assumptions, fire-base availability, and separately labelled stochastic road states. No event scenario is assigned an empirical occurrence probability.

### Identifying Contrasts

The evidence chain is based on five within-model contrasts:

1. **Built-form contrast:** compare cells with different `Observed Building Footprint Coverage Ratio`, `Mean Building Separation (m)`, `Built Continuity Index`, and `Firebreak Share` while treating ignition as imposed; use `Permitted Building Coverage Ratio` only as planning context. This identifies relative `Conditional Spread Susceptibility`, not ignition probability or burned area.
2. **Event-network contrast:** compare `Normal Response Time (min)` with `Disrupted Response Time (min)` under transparent event-specific link-removal or link-penalty rules, then examine changes in `Backup Fire Base Count` and `Single Route Dependence`.
3. **Road-reliability contrast:** hold demand and response bases fixed while repeatedly varying Road Section ID availability under nested `Expected Failed Road Length Share` levels. The percentage is a nominal input calibrated over the eligible pre-mask road network, not an equal net-additional damage level after event-specific road removal. This produces `Timely Response Probability`, `P90 Response Time (min)`, and stability diagnostics under Length-Dependent Independent, Spatially Clustered, and Hazard-Weighted failure mechanisms.
4. **Fire-base removal contrast:** compare system loss under the full eligible base set with system loss after removing each `Candidate Dispatch Base` once. This produces `Leave-One-Out Fire Base Value` and `Leave-One-Out Fire Base Value Share`. Normal roads, event-specific roads, exposure objectives, and multiple predeclared stochastic road states provide the robustness contrasts; no coalition-allocation estimator is used.
5. **Intervention contrast:** compare the same event-specific scenario before and after a response-unit pre-positioning, bounded water-support, or road-section restoration action. This produces `Intervention Benefit` under both unit-count and clearly labelled cost-proxy budgets.

### Assumptions Required for Interpretation

- Road travel speeds are fixed lookup assumptions based on `Road Category`, `Width Category`, and `Road State`; they are not observed post-earthquake speeds. `Emergency Road Service Status`, `Hazard Type`, `Warning Zone Class`, and `Special Warning Zone Pending` define bounded disruption rules rather than verified passability for every segment.
- Length-dependent section failure treats the stochastic closure of a Road Section ID as a modelled component state. It is not an engineering fragility curve. The nominal failure input is calibrated before the event-specific road mask, so mechanism comparisons are bounded stress-scenario checks rather than equal-net-damage effects. Expected overlap and effective added unavailable length are reported explicitly. Full-section closure and the upper tail of `Road Section Length (m)` remain interpretation boundaries.
- All records marked `Candidate Dispatch Base` are treated as nominally comparable dispatch origins. Station-level vehicles, staffing, simultaneous demand, dispatch queues, and suppression capacity are not observed, so leave-one-out criticality is accessibility-based rather than an operational capacity estimate.
- `Water Constraint Scenario` is a boundary condition. `Service Status`, `Observed Water Outage Households`, and `Evidence Tier` may locate affected contexts, but unobserved hydrant or network status is never coded as confirmed functionality or failure.
- Built-form screening uses observed geometry and planning attributes. Building material, interior fuel, fire-resistance performance, and wind fields are unavailable as final variables; consequently, the analysis does not model directional physical fire propagation.
- Exposure objectives are reported separately for population, older-population vulnerability, and critical facilities. No combined exposure objective is constructed, which avoids presenting a single normative weighting scheme as universal.
- Resource budgets are counts of comparable action units within response-base and water-support classes. Road-section restoration also reports `Road Restoration Cost Proxy` based on section length or event-exposed length because a short urban section and a long rural section are not equivalent actions. Cross-class combinations remain exploratory until commensurable cost, vehicle, staffing, and water-capacity information is available.

### Relationship to Planned Outputs

The built-form contrast supports the supplementary `Conditional Fire Susceptibility across Kumamoto` figure and the susceptibility fields reported in `Highest-Priority 125 m Cells`. The event-network and road-reliability contrasts jointly support `Post-Earthquake Fire-Service Accessibility`. The integrated consequence calculation supports `Conditional Fire Consequence and Vulnerable Exposure`, municipality and priority-cell summaries, and the critical-facility table. Fire-base removal contrasts support `Fire Base Accessibility Dependence under Road Disruption` and `Fire Base Leave-One-Out Criticality`. Intervention contrasts support `Intervention Priorities and Protection Gains` and `Intervention Performance by Budget`. Length-dependent, clustered, hazard-weighted, weight, threshold, and parameter changes support `Scenario and Parameter Robustness` and `Robustness and Sensitivity Summary`.

### Interpretation Limits

The design cannot establish that earthquake damage caused a particular fire, estimate the probability that a specific building ignites, forecast actual burned area, estimate engineering road-failure probability, or measure the causal effect of a station or intervention. The eight reported fires are not an estimation sample. Results describe internally consistent consequences, reliability, full-system dependence, and intervention contrasts within declared scenarios. A stable result is decision-relevant evidence under those assumptions, not proof of real-time firefighting or repair performance.

## 6. Main Estimation Framework

### 6.1 Units, Scenarios, and Normalization

Let \(j\) index populated 125 m analysis cells, \(i\) index candidate dispatch bases, \(e\) index routable road edges, \(s\) index junction-to-junction road sections, \(r\) index stochastic road-state replicates, \(d\) index expected failed-road-length severity, \(g\) index a declared road-failure mechanism, \(S\) denote an available subset of candidate dispatch bases, \(N\) denote the full eligible base set, \(a\) index an intervention, \(o\) index an exposure objective, and \(\omega\) index a declared event-specific scenario. Let \(\omega_0\) denote the normal-network, normal-water reference scenario. The primary reporting scenario set contains a reference case and bounded road-status, narrow-road, hazard-overlap, base-availability, water-constraint, and combined-stress cases. The stochastic robustness set contains Length-Dependent Independent, Spatially Clustered, and Hazard-Weighted road-section mechanisms. Event-specific cases are not assigned probabilities, and stochastic cases are not interpreted as reconstructions of observed 2026 road passability.

Continuous inputs with different units are placed on a common scale using the empirical percentile transform:

\[
R(x_j) = \frac{\operatorname{rank}(x_j)-1}{n-1}.
\]

Here, \(R(x_j)\) is the normalized value of input \(x_j\) for cell \(j\), \(\operatorname{rank}(x_j)\) is its average rank among non-missing analysis cells, and \(n\) is the number of non-missing cells for that input. The main analysis retains missingness flags and does not replace missing source values with zero. Alternative winsorized min-max scaling is a sensitivity specification.

### 6.2 Conditional Spread Susceptibility

The main susceptibility score is an equal-weight, directionally aligned combination of four built-form components:

\[
S_j(\omega) = \sum_{k=1}^{4} \alpha_k z_{jk}(\omega), \qquad \alpha_k \geq 0, \qquad \sum_{k=1}^{4} \alpha_k = 1.
\]

Here, \(S_j(\omega)\) is `Conditional Spread Susceptibility`; \(k\) indexes the four components; \(z_{j1}\) is the percentile of `Observed Building Footprint Coverage Ratio`; \(z_{j2}\) is the percentile of `Built Continuity Index`; \(z_{j3}\) is one minus the percentile of `Mean Building Separation (m)`; \(z_{j4}\) is one minus the percentile of `Firebreak Share`; and \(\alpha_k\) is the nonnegative component weight. The main specification sets every \(\alpha_k\) to \(1/4\). The scenario index captures alternative building-adjacency thresholds and firebreak definitions; it does not imply an estimated ignition or wind process.

`Building Count`, `Building Area (m2)`, `Permitted Building Coverage Ratio`, `Land Use Zone Name`, `Urban Land Use Code`, and `Fire Prevention Area Type` are used for stratification, face-validity checks, and sensitivity analysis rather than silently entering the main score. The permitted ratio is compared descriptively with observed footprint coverage but is not treated as realized built form. Component deletion, alternative weights, alternative adjacency thresholds, and alternative cell-assignment rules test whether cell rankings depend on one arbitrary definition. Because no final wind variable exists, no directional spread or building-specific propagation claim is made.

### 6.3 Road Accessibility and Redundancy

The road graph is explicitly noded from `Geometry`. A transparent speed lookup maps `Road Category`, `Width Category`, and `Road State` to normal travel speed. Declared disruption rules remove or penalize edges using `Emergency Road Service Status`, `Emergency Road Class`, `Hazard Type`, `Warning Zone Class`, and narrow-road categories. Each rule is reported in `Scenario Definitions and Interpretation Boundaries`.

For each base-to-cell pair, network travel time is:

\[
T_{ij}(\omega) = \min_{p \in \mathcal{P}_{ij}(\omega)} \sum_{e \in p} c_e(\omega).
\]

Here, \(T_{ij}(\omega)\) is travel time from base \(i\) to cell \(j\) in scenario \(\omega\); \(\mathcal{P}_{ij}(\omega)\) is the set of feasible network paths; \(p\) is one such path; and \(c_e(\omega)\) is the assumed travel time on retained edge \(e\). A disconnected pair receives a declared finite unmet-service cap rather than an infinite value so that system loss remains computable.

The minimum response time for an available base set is:

\[
T_j(S,\omega) = \min_{i \in S} T_{ij}(\omega).
\]

Here, \(T_j(S,\omega)\) is the minimum nominal response time for cell \(j\) from set \(S\). `Normal Response Time (min)` is \(T_j(N,\omega_0)\), while `Disrupted Response Time (min)` is \(T_j(N,\omega)\) for a disruption scenario.

Response redundancy is measured by:

\[
B_j(S,\omega) = \max\left\{0, \sum_{i \in S} \mathbf{1}\left[T_{ij}(\omega) \leq \tau\right]-1\right\}.
\]

Here, \(B_j(S,\omega)\) is `Backup Fire Base Count`; \(\mathbf{1}[\cdot]\) is the indicator function; and \(\tau\) is the response threshold. The main threshold is \(10\) minutes, with \(5\)- and \(15\)-minute sensitivity checks.

For cells with at least one qualifying route, route concentration is:

\[
D_j(S,\omega) = \max_{e \in \mathcal{E}(\omega)} \frac{\sum_{i \in S} \mathbf{1}\left[T_{ij}(\omega) \leq \tau\right]\mathbf{1}\left[e \in p_{ij}^{*}(\omega)\right]}{\sum_{i \in S} \mathbf{1}\left[T_{ij}(\omega) \leq \tau\right]}.
\]

Here, \(D_j(S,\omega)\) is `Single Route Dependence`; \(\mathcal{E}(\omega)\) is the retained edge set; and \(p_{ij}^{*}(\omega)\) is the selected shortest path from base \(i\) to cell \(j\). A value near one means that qualifying base routes share a common edge. Cells with no qualifying route are reported as unserved rather than assigned an artificial route-dependence value.

The primary accessibility penalty is:

\[
A_j(S,\omega) = \beta_T \min\left\{\frac{T_j(S,\omega)}{T_{\max}},1\right\} + \beta_B \frac{1}{1+B_j(S,\omega)}, \qquad \beta_T+\beta_B=1.
\]

Here, \(A_j(S,\omega)\) is the normalized accessibility penalty; \(T_{\max}\) is the declared unmet-service time cap; and \(\beta_T\) and \(\beta_B\) are nonnegative response-time and redundancy weights. The main specification uses equal weights. A sensitivity specification adds \(\beta_D D_j(S,\omega)\), where \(\beta_D\) is a nonnegative route-dependence weight and all accessibility weights are renormalized to sum to one.

### 6.4 Stochastic Road-Section Reliability

The accepted normal and bounded event-specific network contrasts remain primary. A separate stochastic reliability layer tests whether accessibility, station, and intervention conclusions depend on one deterministic road-removal rule. Road Section ID is the stochastic closure unit, while internal road edges retain travel impedance and connector positions.

For road section \(s\) with `Road Section Length (m)` \(L_s\), the Length-Dependent Independent mechanism assigns `Section Failure Probability`:

\[
q_s(\lambda_d)=1-\exp(-\lambda_d L_s).
\]

Here, \(q_s(\lambda_d)\) is the probability that section \(s\) is closed under severity \(d\), and \(\lambda_d\) is `Failure Intensity per Metre`. The intensity is calibrated so the length-weighted expected closure share equals `Expected Failed Road Length Share`:

\[
\frac{\sum_{s \in \mathcal{S}} L_s q_s(\lambda_d)}{\sum_{s \in \mathcal{S}} L_s}=d.
\]

Here, \(\mathcal{S}\) is the set of eligible road sections and \(d\) is the nominal target expected failed-road-length share over the pre-mask network. The main robustness levels are \(d \in \{0.01,0.03,0.05\}\); \(d=0.10\) is a stress case and \(d=0.005\) is a near-baseline calibration check.

To distinguish the nominal input from additional unavailability after the event-specific road mask, define:

\[
A_s=L_s-E_s,
\]

where \(E_s\) is `Event-Exposed Road Length (m)` and \(A_s\) is the event-available length within section \(s\). For failure mechanism \(g\), the expected overlap and effective added shares are:

\[
O_g(d)=\frac{\sum_s E_s q_s(d,g)}{\sum_s L_s q_s(d,g)}, \qquad
D_g^{pre}(d)=\frac{\sum_s A_s q_s(d,g)}{\sum_s L_s}, \qquad
D_g^{avail}(d)=\frac{\sum_s A_s q_s(d,g)}{\sum_s A_s}.
\]

Here, \(q_s(d,g)\) is the marginal closure probability for section \(s\) under mechanism \(g\); \(O_g(d)\) is the share of expected failed length already covered by the event mask; \(D_g^{pre}(d)\) is expected added unavailable length as a share of the pre-mask network; and \(D_g^{avail}(d)\) is the same expected added length relative to the event-available network. Under the nominal 3% input, Length-Dependent Independent and Spatially Clustered have an expected overlap of 22.96%, with added shares of 2.31% of the pre-mask network and 2.83% of the event-available network. Hazard-Weighted has an expected overlap of 36.71%, with corresponding added shares of 1.90% and 2.33%. These diagnostics are analytical summaries of the retained states and require no rerouting.

For each section and replicate, one seeded uniform score \(U_{sr}\) is reused across severities:

\[
Z_{srd}=\mathbf{1}\left[U_{sr}<q_s(\lambda_d)\right].
\]

Here, \(Z_{srd}\) is `Road Section Failure Indicator` for section \(s\), replicate \(r\), and severity \(d\), and \(U_{sr}\) is a reproducible uniform score. Reusing the score makes higher-severity failed-section sets nested within replicate. `Realized Failed Road Length Share` is reported for every state. Spatially Clustered and Hazard-Weighted mechanisms preserve the same nominal pre-mask target but use separately declared spatial assignment rules. Because their overlap with event-specific removal differs, they are mandatory sensitivity scenarios rather than equal-added-damage mechanism comparisons or empirical earthquake models.

Let \(T_{jr}(d,g)\) be the minimum nominal response time to cell \(j\) after full rerouting under replicate \(r\), severity \(d\), and failure model \(g\). Grid reliability at response threshold \(\tau\) is:

\[
\pi_j(d,g,\tau)=\frac{1}{M_R}\sum_{r=1}^{M_R}\mathbf{1}\left[T_{jr}(d,g)\leq \tau\right].
\]

Here, \(\pi_j(d,g,\tau)\) is `Timely Response Probability`, \(M_R\) is the executed replicate count, and \(\tau\) is evaluated at 5, 10, and 15 minutes. `P90 Response Time (min)` is defined over the complete replicate distribution, retaining disconnected outcomes as infinite. If at least 10% of states are disconnected, P90 is reported as unreachable rather than as an ordinary missing value; otherwise the unconditional empirical 90th percentile is reported. Any diagnostic calculated only among connected states must be labelled `Connected-State P90 Response Time (min)` and accompanied by disconnection probability.

The initial pilot uses 100 paired replicates. Formal reliability estimates target 1,000 paired replicates with checkpoints at 100, 250, 500, 750, and 1,000. Coverage means, grid probabilities, quantiles, top-base overlap, and intervention-rank stability must meet declared convergence criteria; unstable outcomes remain inconclusive. The upper tail of `Road Section Length (m)`, `Road Edge Count`, and connector behavior under full-section versus local-fragment closure are mandatory diagnostics because very long sections can otherwise dominate both failure probability and accessibility loss.

### 6.5 Exposure and Conditional Consequence

Critical-facility pressure is constructed from the retained `Medical Facility ID`, `School Facility ID`, `Welfare Facility ID`, `Shelter ID`, and `Evacuation Site ID` records:

\[
Q_j = \sum_{f \in \mathcal{F}} \nu_f \mathbf{1}\left[f \text{ is located in } j\right].
\]

Here, \(Q_j\) is critical-facility pressure in cell \(j\); \(\mathcal{F}\) is the set of retained critical-facility records; \(f\) indexes those records; and \(\nu_f\) is a declared facility weight. The main facility-only objective uses equal facility weights. Sensitivity specifications use `Bed Count`, `Emergency Hospital Designation`, `Disaster Base Hospital Class`, and facility classes without treating unavailable capacity as zero.

Separate exposure objectives are defined as:

\[
\begin{aligned}
E_j^{(P)} &= R\left(\log(1+P_j)\right), \\
E_j^{(V)} &= \frac{1}{2}E_j^{(P)} + \frac{1}{2}R(O_j), \\
E_j^{(F)} &= R(Q_j).
\end{aligned}
\]

Here, \(E_j^{(P)}\) is population exposure, \(E_j^{(V)}\) is older-population vulnerability exposure, and \(E_j^{(F)}\) is critical-facility exposure. \(P_j\) is `Total Population` and \(O_j\) is `Population Age 65+ Share`. The objective index \(o\) takes the values population, vulnerability, or facility. The facility objective uses all five declared classes in \(Q_j\), while the reader-facing map may display only medical, welfare, and designated-shelter points to preserve legibility. Alternative older-age thresholds, household-vulnerability shares, and facility weights are robustness specifications.

The bounded water penalty is:

\[
W_j(\omega) = \begin{cases}
0, & \text{normal-reliance boundary scenario}, \\
1, & \text{network-water-unavailable boundary scenario for the affected area}.
\end{cases}
\]

Here, \(W_j(\omega)\) is the penalty encoded by `Water Constraint Scenario`. The affected context may be bounded using `Service Status`, `Observed Water Outage Households`, `Municipality`, `Evidence Tier`, and `Verification Status`; it is not interpreted as observed hydrant failure.

The primary relative consequence score is multiplicative in susceptibility and exposure and increases with access and water penalties:

\[
C_j^{(o)}(S,\omega) = S_j(\omega)E_j^{(o)}\left[1+\lambda_A A_j(S,\omega)+\lambda_W W_j(\omega)\right].
\]

Here, \(C_j^{(o)}(S,\omega)\) is `Conditional Fire Consequence` for exposure objective \(o\); \(\lambda_A\) is the nonnegative accessibility-penalty multiplier; and \(\lambda_W\) is the nonnegative water-penalty multiplier. The main specification sets both multipliers to one. Alternative multiplier values, additive component forms, and objective-specific reporting test sensitivity. The score is relative and conditional on ignition; it is not a calibrated probability or expected loss in monetary units.

### 6.6 System Loss and Leave-One-Fire-Base-Out Criticality

For each objective and scenario, system loss is:

\[
J^{(o)}(S,\omega) = \sum_j q_j C_j^{(o)}(S,\omega).
\]

Here, \(J^{(o)}(S,\omega)\) is total modelled system loss and \(q_j\) is a declared reporting weight. The main specification sets every \(q_j\) to one because exposure is already represented in \(E_j^{(o)}\). A municipality-balanced sensitivity specification gives municipalities equal aggregate influence.

The primary fire-base criticality estimand is:

\[
L_i^{(o)}(\omega) = J^{(o)}(N\setminus\{i\},\omega)-J^{(o)}(N,\omega).
\]

Here, \(L_i^{(o)}(\omega)\) is `Leave-One-Out Fire Base Value` for base \(i\). It measures the additional system loss when that base is removed from the full eligible set and all other bases remain available. Nonnegative values are expected because removing a response option cannot improve the modelled objective; negative values trigger a routing or aggregation audit.

For within-scenario comparison, normalize removal losses as:

\[
l_i^{(o)}(\omega)=\frac{L_i^{(o)}(\omega)}{\sum_{k \in N}L_k^{(o)}(\omega)}.
\]

Here, \(l_i^{(o)}(\omega)\) is `Leave-One-Out Fire Base Value Share`, and \(k\) indexes eligible bases in the denominator. A zero denominator is reported as an unidentified scenario-objective pair. Shares support comparison within the same modelled objective; they are not probabilities, capacity shares, or transferable across objectives.

Normal-road and event-specific-road values are reported directly. Across stochastic road states, each base is summarized by the median, interquartile range, and frequency of membership in a predeclared high-criticality set. `Road-Scenario Leave-One-Out IQR` records instability without subtracting it from the central estimate. Stochastic robustness must use multiple predeclared road states from each retained failure mechanism rather than one median representative state. No universal composite station score and no coalition-allocation estimator are used.

The estimand is deterministic for a fixed road state and therefore has no permutation-sampling convergence problem. Monte Carlo uncertainty arises only when summarizing leave-one-out results across stochastic road states; replicate checkpoint stability is evaluated for the median removal-loss share, the 95th-percentile absolute share change, and high-criticality membership frequency. Results remain scenario-based because base vehicles, staffing, dispatch queues, and simultaneous incidents are not observed.

### 6.7 Intervention Evaluation

An intervention may add a candidate staging site drawn from mapped public or emergency facilities, restore a disrupted Road Section ID, or change the bounded water penalty for selected high-consequence cells. Intervention benefit is:

\[
Benefit_a^{(o)}(\omega) = J_0^{(o)}(\omega)-J_a^{(o)}(\omega).
\]

Here, \(Benefit_a^{(o)}(\omega)\) is `Intervention Benefit`; \(J_0^{(o)}(\omega)\) is baseline system loss; and \(J_a^{(o)}(\omega)\) is system loss after intervention \(a\). Candidate staging sites are restricted to mapped emergency evacuation sites, designated shelters, public facilities, schools, and named non-cemetery urban parks. Emergency evacuation sites are eligible only when designated for earthquake or large-scale-fire use. Each site retains `Candidate Staging Site ID`, `Candidate Staging Site Type`, `Candidate Staging Site Name`, and `Candidate Source Status`; it must match an `Access Mesh Code` within 250 m, use an accepted road-network connector, and lie in the central event graph. The screened set retains the 35 highest-consequence candidates subject to 2 km spacing. Routing begins at the matched demand node rather than an asserted facility driveway, and `Field Verification Required` remains true because operational deployability is not observed. Restoration candidates are disrupted road sections under the event-specific scenario; water-support candidates are high-consequence cells under the constrained-water boundary. Restoring a section reactivates its disrupted internal edges for routing, but does not imply that every metre required physical repair.

For a declared budget, the event-specific allocation target is:

\[
\mathcal{A}_{K}^{*}(\omega_{event}) = \arg\max_{\mathcal{A}' \subseteq \mathcal{A}} \left[J_0^{(o)}(\omega_{event})-J_{\mathcal{A}'}^{(o)}(\omega_{event})\right] \quad \text{subject to} \quad \sum_{a \in \mathcal{A}'} c_a \leq K.
\]

Here, \(\mathcal{A}\) is the candidate action set; \(\mathcal{A}'\) is a selected action bundle; \(\mathcal{A}_{K}^{*}(\omega_{event})\) is the selected event-specific bundle under budget \(K\); \(\omega_{event}\) is the declared event-specific road case; \(c_a\) is the declared resource requirement for action \(a\); and \(J_{\mathcal{A}'}^{(o)}(\omega_{event})\) is loss after the action bundle. Candidate-staging-site and water-support analyses first use within-class unit counts. Road restoration reports both a section-count screen and `Road Restoration Cost Proxy`, defined from `Road Section Length (m)`, event-exposed length, or a clearly labelled combination. Exact enumeration is used when feasible; otherwise forward selection is labeled as a heuristic. Results are compared with population-only candidate-site placement, nearest-base placement, highest-road-class restoration, and restoration-benefit-per-cost-proxy baselines. Cross-class bundles are not called cost-optimal without commensurable cost data.

Fixed-plan road-restoration robustness is evaluated as:

\[
R_{\mathcal{A}_{K}^{*}}^{(o)}(\omega_r)=\frac{Benefit_{\mathcal{A}_{K}^{*}}^{(o)}(\omega_r)}{Benefit_{\mathcal{A}_{K}^{*}}^{(o)}(\omega_{event})}.
\]

Here, \(R_{\mathcal{A}_{K}^{*}}^{(o)}(\omega_r)\) is `Retained Protection Gain Share`, and \(\omega_r\) is one predeclared stochastic road state under the nominal 3% pre-mask input. The section-count and length-aware bundles selected under \(\omega_{event}\) are each evaluated unchanged across 100 states from each of the Length-Dependent Independent, Spatially Clustered, and Hazard-Weighted mechanisms. The median, lower quartile, and minimum are reported. This tests whether a preselected plan remains useful under different declared stress scenarios; it does not compare equal net-added road damage, re-optimize by state, identify a robust-optimal bundle, or establish multi-state robustness for candidate staging sites or bounded water support.

### 6.8 Robustness, Heterogeneity, and Failure Modes

- **Built form:** vary component weights, building-adjacency thresholds, firebreak definitions, scaling method, component inclusion, and cell-assignment rules; use `Permitted Building Coverage Ratio` only for descriptive planning-context contrasts and do not infer building-specific propagation.
- **Accessibility:** vary road-speed lookup assumptions, disruption rules, snapping tolerance, unmet-service cap, and the \(5\)-, \(10\)-, and \(15\)-minute response thresholds.
- **Road reliability:** compare nominal pre-mask inputs of 1%, 3%, and 5% `Expected Failed Road Length Share`, the 10% stress case, Length-Dependent Independent, Spatially Clustered, and Hazard-Weighted failure models, and 100-1,000 replicate checkpoints. Report expected overlap with the event mask and effective added unavailable length; do not interpret mechanism differences as equal-net-damage effects. Complete junction-to-junction section unavailability is retained as a precautionary rescue-access rule: a closed section is not treated as a reliable through-route, but the model does not claim that every metre is physically damaged.
- **Exposure:** report population, older-population, and facility objectives separately; vary older-age and household-vulnerability measures and facility weights.
- **Fire-base criticality:** report `Leave-One-Out Fire Base Value` and `Leave-One-Out Fire Base Value Share` across normal roads, event-specific roads, exposure objectives, and multiple stochastic road states; report medians, interquartile ranges, rank correlation, high-criticality membership frequency, and replicate-checkpoint stability.
- **Interventions:** evaluate the fixed event-specific section-count and length-aware road-restoration bundles across 100 predeclared road states per retained failure mechanism under the nominal 3% pre-mask input; report the median, lower quartile, and minimum `Retained Protection Gain Share`. Candidate staging-site and bounded-water-support results remain event-specific screens.
- **Heterogeneity:** summarize by `Municipality Name`, `Land Use Zone Name`, `Urban Land Use Code`, `Fire Prevention Area Type`, critical-facility class, and normal versus disrupted accessibility.
- **Failure modes:** stop or downgrade claims when road topology yields implausible routes, large areas are disconnected under the normal network, reliability estimates do not converge, building rankings are driven by one component, leave-one-out criticality changes arbitrarily across modest specifications, or intervention rankings fail to outperform simple baselines and cost-proxy alternatives. Full-section operational unavailability is interpreted as a conservative safety boundary rather than evidence of continuous physical damage.

## 7. Analytical Workflow

The completed outputs document the cell-level built-form screen, event-specific accessibility, formal length-dependent reliability, conditional consequence, deterministic leave-one-fire-base-out criticality, multi-state fire-base stability, section-aware interventions, and fixed-plan road-restoration performance across multiple road states. Component-deletion and accessibility-multiplier sensitivities are also complete. Broader built-form sensitivity is deferred to future work, and complete road-section operational unavailability is retained deliberately as a conservative rescue-safety boundary. Candidate staging sites are restricted to traceable mapped public or emergency sites with accepted network access, while operational deployability remains explicitly subject to field verification. The fixed road-restoration bundles retain high median benefit but have weak lower-tail states, so they are not described as universally robust. Building footprints are inputs to the 125 m screen; no workflow step produces a building-level result.

| step | variables used | formula/model used | generated figure/table title | theory or claim evaluated | support status |
|---|---|---|---|---|---|
| 1. Freeze scope, units, scenarios, and evidence boundaries | `Disruption Type`; `Service Status`; `Emergency Road Service Status`; `Water Constraint Scenario`; `Candidate Dispatch Base`; `Verification Status` | Section 5 scenario-contrast design and Section 6.1 scenario set | `Integrated Fire Consequence and Response-System Dependence Framework`; `Scenario Definitions and Interpretation Boundaries` | The analysis distinguishes observed context from imposed scenarios and connects risk screening to resource decisions. | Supported as analysis documentation: the terminology-revised framework and scenario table are complete, with detailed data coverage and limitations retained in Sections 3-4. |
| 2. Construct prefecture-wide built-form components | `Observed Building Footprint Coverage Ratio`; `Permitted Building Coverage Ratio`; `Mean Building Separation (m)`; `Built Continuity Index`; `Firebreak Share`; `Land Use Zone Name`; `Urban Land Use Code` | Empirical percentile transform and conditional susceptibility score in Section 6.2 | `Conditional Fire Susceptibility across Kumamoto`; `Highest-Priority 125 m Cells`; `Robustness and Sensitivity Summary` | Supporting Point 1 at the grid level: dense, continuous development with fewer firebreaks has higher conditional spread susceptibility, while permitted intensity remains contextual rather than a realized morphology input. | Partially supported: the figure and component-deletion sensitivity are complete, but alternative weights, thresholds, scaling rules, firebreak definitions, and cell-assignment checks remain incomplete; no building-level claim is supported. |
| 3. Build and validate normal and event-disrupted accessibility | `Road Category`; `Width Category`; `Road State`; `Emergency Road Service Status`; `Hazard Type`; `Candidate Dispatch Base`; `Normal Response Time (min)`; `Disrupted Response Time (min)`; `Backup Fire Base Count`; `Single Route Dependence` | Shortest-path, redundancy, route-concentration, and accessibility-penalty formulas in Section 6.3 | `Post-Earthquake Fire-Service Accessibility`; `Municipality Fire Consequence and Accessibility Summary` | Supporting Point 2: bounded event-specific disruptions create reproducible response delays and redundancy losses at high-consequence locations. | Supported within the declared event-specific road rule; the accessibility figure and municipality summary are complete, while observed passability remains unavailable. |
| 4. Simulate road-section reliability | `Road Section ID`; `Road Section Length (m)`; `Road Edge Count`; `Road Failure Model`; `Expected Failed Road Length Share`; `Failure Intensity per Metre`; `Section Failure Probability`; `Road Section Failure Indicator`; `Simulation Replicate`; `Realized Failed Road Length Share`; `Timely Response Probability`; `P90 Response Time (min)` | Finalized length-dependent calibration inputs, nested paired failure assignment, full rerouting, reliability probability, overlap diagnostics, and convergence framework in Section 6.4 | `Post-Earthquake Fire-Service Accessibility`; `Scenario and Parameter Robustness`; `Scenario Definitions and Interpretation Boundaries`; `Robustness and Sensitivity Summary` | Supporting Point 2: event-specific accessibility patterns are not artifacts of one deterministic road-removal rule. | Partially supported: the formal 1,000-replicate nominal 3% length-dependent estimate and final checkpoint are complete, and 100-replicate severity, clustered, and hazard-weighted sensitivities are available. At the nominal 3% input, effective added shares differ across mechanisms, so alternatives support bounded stress-scenario sensitivity rather than equal-net-damage comparison. Whole-section closure remains conservative operational unavailability for rescue access, not continuous physical damage. |
| 5. Construct exposure objectives and conditional consequence | `Observed Building Footprint Coverage Ratio`; `Permitted Building Coverage Ratio`; `Total Population`; `Population Age 65+ Share`; `Medical Facility ID`; `School Facility ID`; `Welfare Facility ID`; `Shelter ID`; `Evacuation Site ID`; `Water Constraint Scenario`; `Conditional Spread Susceptibility`; `Disrupted Response Time (min)`; `Conditional Fire Consequence` | Exposure-objective and conditional-consequence formulas in Section 6.5 | `Conditional Fire Consequence and Vulnerable Exposure`; `Municipality Fire Consequence and Accessibility Summary`; `Highest-Priority 125 m Cells`; `Priority Critical Facilities` | Central question and Supporting Point 1 at the grid level: susceptibility, constrained response, water boundaries, and exposure jointly identify high-consequence locations; older-population results are retained in tables rather than a redundant map panel. | Partially supported: the planned figure and tables and two accessibility-multiplier sensitivities are complete, but broader consequence forms and exposure-definition checks remain incomplete. `Priority Critical Facilities` intentionally omits public-facing facility names and identifiers, so it supports class, municipality, and mesh-level screening rather than facility-specific action. |
| 6. Estimate fire-base removal criticality | `Fire Base Name`; `Fire Base Type`; `Candidate Dispatch Base`; `Leave-One-Out Fire Base Value`; `Leave-One-Out Fire Base Value Share`; `Road-Scenario Leave-One-Out IQR`; `Conditional Fire Consequence`; `Road Failure Model`; `Expected Failed Road Length Share` | Full-system loss and deterministic one-base removal framework in Section 6.6, repeated across declared road states and exposure objectives | `Fire Base Accessibility Dependence under Road Disruption`; `Fire Base Leave-One-Out Criticality`; `Scenario and Parameter Robustness` | Supporting Point 3: station criticality reflects loss of substitutability in the full represented response system. | Partially supported: deterministic leave-one-out values are complete for all 81 eligible bases under normal and event-specific roads, and multi-state stability is complete across declared nominal-input stress scenarios and objectives; the lower correlation under spatially clustered failure keeps the ranking scenario-sensitive. |
| 7. Evaluate resource interventions | `Mesh Code`; `Candidate Staging Site ID`; `Candidate Staging Site Type`; `Candidate Staging Site Name`; `Access Mesh Code`; `Staging-to-Mesh Distance (m)`; `Staging Access Network Snap Distance (m)`; `Field Verification Required`; `Road Section ID`; `Road Section Length (m)`; `Route Name`; `Event-Exposed Road Length (m)`; `Road Restoration Cost Proxy`; `Disrupted Response Time (min)`; `Backup Fire Base Count`; `Water Constraint Scenario`; `Conditional Fire Consequence`; `Intervention Benefit`; `Retained Protection Gain Share` | Event-specific intervention allocation and fixed-plan road-restoration robustness formulas in Section 6.7 | `Intervention Priorities and Protection Gains`; `Intervention Performance by Budget`; `Scenario and Parameter Robustness`; `Robustness and Sensitivity Summary` | Supporting Point 4: selected actions reduce conditional consequence relative to simple allocation and road-class baselines, and preselected road-restoration bundles remain useful across uncertain road states. | Partially supported: candidate staging sites are traceable and road selection uses the final consequence objective. Under the shared 30-minute unmet-service cap, the six mechanism-rule combinations have median retained road-restoration gains of 97.49%-99.94% and lower-quartile gains of 93.43%-98.42%, but minimum gains of 11.16%-24.97%. This supports typical-state usefulness, not universal robustness; staging-site and water-support results remain event-specific. |
| 8. Stress-test rankings and decisions | `Conditional Spread Susceptibility`; `Conditional Fire Consequence`; `Leave-One-Out Fire Base Value Share`; `Road-Scenario Leave-One-Out IQR`; `Intervention Benefit`; `Retained Protection Gain Share`; `Water Constraint Scenario`; `Road Failure Model`; `Expected Failed Road Length Share`; `Timely Response Probability`; `Road Restoration Cost Proxy` | Sensitivity, ablation, convergence, fixed-plan benefit distributions, rank-correlation, membership-frequency, and failure-mode checks in Sections 6.2-6.8 | `Scenario and Parameter Robustness`; `Robustness and Sensitivity Summary` | Central question: grid, station, and intervention priorities are not artifacts of one reasonable modelling choice. | Partially supported: road-response reliability, multi-state leave-one-out stability, fixed-plan road-restoration distributions, component deletion, and two accessibility multipliers are complete. Broader built-form/consequence sensitivity is deferred, and low minimum retained intervention gains reveal tail-state vulnerability. |

### Evidence Checkpoints

1. **Supporting Point 1:** supported at the 125 m grid level only if high-susceptibility cells remain comparatively high under alternative weights, thresholds, scaling, component definitions, and cell-assignment rules. If one component or grid definition controls the rankings, support is partial or absent. The streamlined plan does not support a building-level result.
2. **Supporting Point 2:** supported only if the normal network is credible, the bounded event-specific rule produces coherent response-time and redundancy losses, and section-aware reliability remains interpretable across length-dependent, spatially clustered, and hazard-weighted nominal-input stress scenarios. Expected overlap and effective added unavailability must accompany mechanism comparisons; no equal-net-damage effect is identified. Nonconvergence or implausible routing makes the stochastic part inconclusive. Whole-section closure is a conservative operational-availability rule for rescue safety and is not evidence that every metre is physically damaged.
3. **Supporting Point 3:** supported only if leave-one-fire-base-out losses are nonnegative and reproducible, remain interpretable across exposure objectives and normal/event-specific roads, and retain stable magnitude and high-criticality membership across multiple stochastic road states. Otherwise fire-base criticality remains scenario-specific or unidentified.
4. **Supporting Point 4:** partially supported because event-specific intervention bundles outperform stated simple baselines and fixed road-restoration plans retain high median and lower-quartile benefit across multiple road states. Under the shared 30-minute unmet-service cap, minimum retained gains of 11.16%-24.97% prevent a universal robustness claim. Without comparable action costs, the evidence supports within-class prioritization but not a cost-optimal mixed portfolio.
5. **Central Research Question:** fully supported only when the susceptibility, accessibility, fire-base criticality, and intervention checkpoints all pass. If one component fails, conclusions are restricted to the components that remain supported. The design never converts these checkpoints into causal, probability, or real-time-capacity claims.

## 8. Figure and Table Plan

This confirmed streamlined plan retains five main-text and two supplementary figures, plus five main-text and two supplementary tables. All planned artifacts have been generated and are marked `done`; this status records artifact completion, not passage of every evidence checkpoint in Section 7. The redundant building-scale cluster figure and data-coverage table remain removed. No time-series output is included. The eight observed fires are reserved for plausibility checking rather than model training. Fire-base importance is measured only as deterministic leave-one-fire-base-out loss in the full represented system; no Shapley or other coalition-allocation estimator is used.

### Figures

| title | what it expresses | figure type | subpanels | key variables | status |
|---|---|---|---:|---|---|
| Integrated Fire Consequence and Response-System Dependence Framework | Main: the complete analytical chain from built form, post-earthquake accessibility, water constraints, and exposure through conditional consequence, leave-one-fire-base-out system dependence, and intervention benefit. | conceptual flow diagram | 1 | `Conditional Spread Susceptibility`, `Disrupted Response Time (min)`, `Water Constraint Scenario`, `Conditional Fire Consequence`, `Leave-One-Out Fire Base Value`, `Intervention Benefit` | done |
| Conditional Fire Consequence and Vulnerable Exposure | Main: where population and essential services overlap with conditional spread susceptibility and constrained response to create the greatest conditional consequences. | choropleth and point-overlay maps | 2 | `Conditional Spread Susceptibility`, `Total Population`, `Medical Facility ID`, `Welfare Facility ID`, `Shelter ID`, `Conditional Fire Consequence`, `Geometry` | done |
| Post-Earthquake Fire-Service Accessibility | Main: how event-specific disruption and additional road-section uncertainty change response time, 10-minute backup coverage, and reliable timely arrival. | network-based gridded maps | 4 | `Normal Response Time (min)`, `Disrupted Response Time (min)`, `Backup Fire Base Count`, `Timely Response Probability`, `Geometry` | done |
| Fire Base Accessibility Dependence under Road Disruption | Main: how much modelled system loss increases when each eligible fire base is removed from the full response system, and how that dependence changes between normal and event-specific roads. | map and ranked dot plot | 2 | `Fire Base Name`, `Candidate Dispatch Base`, `Leave-One-Out Fire Base Value`, `Leave-One-Out Fire Base Value Share`, `Geometry` | done |
| Intervention Priorities and Protection Gains | Main: where traceable candidate staging-site selection, bounded water support, and junction-to-junction road-section restoration reduce weighted conditional consequence under the event-specific scenario, and how road priorities change between section-count and length-aware cost-proxy budgets. | map, comparative bar plot, and budget-benefit curve | 3 | `Candidate Staging Site ID`, `Candidate Staging Site Type`, `Field Verification Required`, `Intervention Benefit`, `Conditional Fire Consequence`, `Disrupted Response Time (min)`, `Backup Fire Base Count`, `Water Constraint Scenario`, `Road Section ID`, `Road Section Length (m)`, `Route Name`, `Road Restoration Cost Proxy`, `Geometry` | done |
| Conditional Fire Susceptibility across Kumamoto | Supplementary: how building coverage, built continuity, and mapped firebreak conditions combine into the conditional spread-susceptibility screen. | gridded maps | 3 | `Observed Building Footprint Coverage Ratio`, `Mean Building Separation (m)`, `Built Continuity Index`, `Firebreak Share`, `Conditional Spread Susceptibility`, `Geometry` | done |
| Scenario and Parameter Robustness | Supplementary: whether alternative road-section failure mechanisms change response reliability, high-criticality fire-base membership under the leave-one-out estimand, or the retained benefit of fixed event-specific road-restoration plans across 100 states per mechanism. | line, bar, and interval plots | 3 | `Road Failure Model`, `Expected Failed Road Length Share`, `Simulation Replicate`, `Realized Failed Road Length Share`, `Timely Response Probability`, `P90 Response Time (min)`, `Leave-One-Out Fire Base Value Share`, `Road-Scenario Leave-One-Out IQR`, `Intervention Benefit`, `Retained Protection Gain Share`, `Road Restoration Cost Proxy` | done |

### Tables

| title | what it expresses | rows | columns | row meaning | column meaning | status |
|---|---|---:|---:|---|---|---|
| Scenario Definitions and Interpretation Boundaries | Main: the common ignition-conditioned analysis, event-specific road disruption, stochastic road-section failure, water-availability, one-fire-base-removal, and intervention assumptions, analytical purposes, and interpretation boundaries. | 12 scenarios plus 1 symbol key | 8 | One declared baseline, event-specific, stochastic, stress, removal, or sensitivity scenario; the final row defines all codes and percentage values. | Scenario label; road state; Road Failure Model; Expected Failed Road Length Share; water constraint; available candidate bases; analytical purpose; interpretation boundary. | done |
| Municipality Fire Consequence and Accessibility Summary | Main: municipality-level differences in exposed population, older-population share, accessibility degradation, response redundancy, and aggregate conditional fire consequence. | 49 | 12 | One municipality or ward-level reporting unit. | Municipality identifiers; population and vulnerability; normal and disrupted response summaries; backup-base and route-dependence summaries; high-consequence-cell count; aggregate conditional consequence. | done |
| Priority Critical Facilities | Main: a compact, balanced screening summary of hospitals, welfare facilities, schools, shelters, and evacuation sites in cells with high conditional consequence or weak post-earthquake fire-service accessibility; public-facing facility names and identifiers are intentionally omitted. | 20 | 9 | One of the four highest-priority assigned records in each of five facility classes, interpreted at class, municipality, and mesh level rather than as a named action target. | Priority rank; facility class; municipality; relevant capacity or designation; mesh; surrounding conditional consequence; disrupted response time; backup-base count; priority score. | done |
| Fire Base Leave-One-Out Criticality | Main: the 20 eligible candidate dispatch bases with the largest event-road population-objective leave-one-out loss, with normal-road comparison and across-road instability; complete results for all 81 bases remain in derived data. | 20 | 9 | One of the 20 eligible candidate dispatch bases with the largest event-road `Leave-One-Out Fire Base Value Share`. | Event-road criticality order; English fire-base label and type; municipality; normal- and event-road leave-one-out loss and share; road-scenario difference; road-scenario IQR; interpretation flag. | done |
| Intervention Performance by Budget | Main: paired performance of prioritized and population-baseline candidate staging-site selection, bounded water support, and road-section restoration at representative unit-count and length-aware cost-proxy budgets. | 12 | 10 | One action class, budget definition, and displayed budget level; prioritized and baseline results are paired within the row. | Action type; budget definition and level; prioritized and baseline budget used; intervention benefit; consequence-reduction percentage; prioritized advantage over baseline. | done |
| Highest-Priority 125 m Cells | Supplementary: the complete cell-level list supporting priority verification, patrol, access protection, or resource pre-positioning; the main text reports only its geographic concentration and principal capability gaps. | 50 | 14 | One high-priority 125 m analysis cell. | Mesh and municipality identifiers; `Observed Building Footprint Coverage Ratio`; `Permitted Building Coverage Ratio`; separation, continuity, and firebreak indicators; exposure; disrupted accessibility; water scenario; conditional consequence; priority rank. | done |
| Robustness and Sensitivity Summary | Supplementary: exact nonredundant values supporting road-response reliability, multi-state leave-one-out fire-base stability, fixed-plan road-restoration benefit distributions, built-form/consequence sensitivity, and the final reliability-convergence checkpoint. | no more than 20 | no more than 10 | One selected severity, alternative failure mechanism, fire-base stability distribution, fixed-plan intervention distribution, built-form/consequence sensitivity, or convergence checkpoint. | Domain; specification; failure model or sensitivity; scenario level; primary and secondary results; assessment; interpretation. | done |
