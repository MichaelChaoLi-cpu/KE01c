# AnaSOP
Analysis Standard Operating Procedure

## 1. Research Objective

### Central Research Question

- Research question: Under event-specific post-earthquake road and water-supply disruption scenarios, how do building- or grid-level conditional fire consequences and the marginal system value of fire stations vary across Kumamoto Prefecture, how stable are those results under length-dependent and spatially correlated road-section failures, and how can the combined evidence guide limited firefighting-resource placement after the earthquake beginning on 2026-07-28?
- Why it matters: A risk surface alone does not reveal which response bases are operationally irreplaceable or which intervention produces the largest protection gain. Joint estimation connects spatial screening to an explicit allocation decision.
- Data support currently visible: The current evidence covers building footprints, 125 m population exposure, a routable road-edge network, roads and emergency routes, nominal fire-service locations and jurisdictions, urban land use, fire-prevention and open-space features, critical facilities, secondary hazards, and event-specific damage and service-disruption context. A junction-to-junction road-section layer and its stochastic-failure variables remain pending final preprocessing in this project.
- Key readable variables or data scope: building coverage and continuity, building separation, land-use class, firebreak proximity, population and older-population exposure, critical-facility exposure, road class and width, station-to-demand travel time, backup-station count, route dependence, Road Section ID, Road Section Length (m), Timely Response Probability, and bounded water-availability scenarios.
- What would verify it: The analysis must produce spatially coherent conditional consequence estimates, stable station-value rankings across event-specific and documented stochastic sensitivity scenarios, and measurable reductions in weighted exposure or response penalties under at least one feasible intervention.
- What would falsify or weaken it: The central claim would be weakened if road topology cannot support credible routing, stochastic results are dominated by implausibly long road sections, station rankings are dominated by unverified facility records, building-level results are unstable across reasonable spread definitions, or intervention rankings reverse under modest scenario or cost-proxy changes.
- Required next feasibility check: Finalize the junction-to-junction road-section layer, verify connector-aware section closures, calibrate length-dependent failure severities, test spatially clustered and hazard-weighted alternatives, and rerun road-restoration interventions with length- or exposed-length-based cost proxies.

### Supporting Research Questions

#### Supporting Point 1

- Role relative to central point: mechanism
- Research question: Which 125 m cells and buildings have the greatest conditional fire-spread susceptibility and consequence when ignition locations are imposed rather than predicted?
- Why it matters: Separating conditional spread and consequence from ignition probability avoids presenting an unsupported probability of a specific building burning.
- Data support currently visible: Building geometry, population exposure, urban land use, roads, parks, water and other potential firebreaks, critical facilities, and event damage context support relative spatial screening.
- Key readable variables or data scope: building density, continuous built-up area, separation distance, building area, surrounding road and open-space width, dense-low-rise and industrial land use, exposed population, and exposed critical facilities.
- What would verify it: High-ranked locations should remain relatively high under alternative grid sizes, ignition seeds, firebreak definitions, and plausible wind assumptions.
- What would falsify or weaken it: Results that are primarily determined by one arbitrary weight or that cannot distinguish dense urban clusters from clearly separated development would undermine the measure.
- Required feasibility check: Determine which building and land-use attributes have adequate coverage and whether wind or building-material information can be added without delaying the minimum viable analysis.

#### Supporting Point 2

- Role relative to central point: mechanism and robustness
- Research question: How do event-specific bounded road disruptions change nominal response time, backup coverage, and single-route dependence for high-consequence locations, and how reliable are those outcomes under additional length-dependent and spatially correlated road-section failures?
- Why it matters: Normal-condition proximity can overstate response capability when bridges, narrow roads, landslide-prone links, or key emergency routes become unavailable.
- Data support currently visible: A prefecture-wide road network, emergency transport routes, fire-service locations, administrative coverage, and secondary-hazard zones support scenario-based accessibility analysis.
- Key readable variables or data scope: shortest travel time, number of stations within stated thresholds, second-best travel time, edge and route criticality, road class and width, emergency-route status, hazard-intersection indicators, Road Section ID, Road Section Length (m), Expected Failed Road Length Share, and Timely Response Probability.
- What would verify it: Event-specific disruption scenarios should identify reproducible increases in travel time and losses of backup coverage, while 1%, 3%, and 5% expected failed-road-length sensitivities and a 10% stress case should reveal whether conclusions remain stable under additional road uncertainty.
- What would falsify or weaken it: Poor network connectivity, excessive snapping error, or implausible normal-condition travel times would make the accessibility comparison unreliable.
- Required feasibility check: Preserve the accepted normal and bounded event-specific accessibility results, then add a section-aware stochastic reliability layer with nested seeded failures, spatially clustered or hazard-weighted sensitivity, and explicit upper-tail section-length diagnostics.

#### Supporting Point 3

- Role relative to central point: methodological application
- Research question: What is each fire station's accessibility-based marginal system value, and which stations remain valuable across alternative disruption and demand scenarios?
- Why it matters: Station proximity and jurisdiction size do not measure substitutability. A station may have modest normal coverage but become critical when neighboring routes or stations are unavailable.
- Data support currently visible: Nominal response-base locations, road accessibility, population and critical-facility demand, and scenario-specific conditional consequences can define a cooperative service network.
- Key readable variables or data scope: leave-one-station-out loss, coalition marginal coverage gain, weighted response-penalty reduction, population and critical facilities protected, redundancy gain, scenario-average Shapley value, and variation across scenarios.
- What would verify it: Sampled-permutation Shapley estimates should converge or retain an explicit convergence limitation, reproduce simple leave-one-out criticality patterns where expected, and preserve meaningful top-base membership across event-specific and selected stochastic road states.
- What would falsify or weaken it: Rankings that fail to converge, are entirely determined by one demand weight, or change arbitrarily with small routing perturbations would not support a stable station-value claim.
- Required feasibility check: Retain the accepted event-specific station-value figure, then test rank stability using representative or checkpointed stochastic road states without nesting a full Shapley experiment inside every road-failure replicate.

#### Supporting Point 4

- Role relative to central point: decision application
- Research question: Which combination of response-unit pre-positioning, temporary water support, and priority road restoration produces the largest robust reduction in weighted conditional fire consequence?
- Why it matters: The practical objective is not merely to rank risky places or stations, but to compare feasible actions under limited resources.
- Data support currently visible: The integrated risk, access, exposure, road, and station layers support counterfactual comparisons; water interventions can initially be represented only by explicit boundary scenarios.
- Key readable variables or data scope: population and critical facilities returned to response thresholds, reduction in response delay, redundancy restored, conditional consequence reduced, Road Section ID, Road Section Length (m), Road Restoration Cost Proxy, intervention unit count, and performance across scenarios.
- What would verify it: Recommended interventions should outperform simple baselines such as population-only placement, nearest-station placement, or restoration of the highest road class, and should remain useful across multiple scenarios.
- What would falsify or weaken it: Recommendations that depend on unavailable operational attributes or reverse under minor scenario changes should be reported as indeterminate rather than optimal.
- Required feasibility check: Replace edge-level road actions with junction-to-junction section actions, report section length and event-exposed length, compare unit-count and length-constrained budgets, and separate accessibility improvements from unobserved repair cost and operational capacity.

### Scope of Analysis

- Topics: post-earthquake conditional urban-fire consequence, response accessibility, fire-station marginal value, infrastructure redundancy, and resource-allocation robustness.
- Units of analysis: 125 m populated grids for prefecture-wide screening; individual buildings within selected high-priority urban clusters; fire stations as cooperative service units; routable road edges for deterministic event scenarios; and junction-to-junction road sections for stochastic failure and restoration sensitivity.
- Geographic scope: Kumamoto Prefecture, with building-level refinement limited to locations selected through the prefecture-wide screen.
- Event scope: The earthquake sequence beginning on 2026-07-28 provides the observed disruption context. The study is a spatial scenario assessment and does not analyze temporal ordering or disorder.
- Validation scope: The eight reported fires may be used only for limited external plausibility checks, not as a training sample or the study population.

### Study Design Declaration

- Research type: applied
- Study design: Event-specific spatial scenario analysis combining conditional fire-consequence screening, network accessibility, cooperative-game station valuation, and counterfactual intervention comparison, with a separate nested Monte Carlo road-section reliability layer for robustness.
- Interpretation limit: Results are not causal estimates, specific-building ignition probabilities, forecasts of actual burned area, or measurements of real-time dispatch capacity. Until station-level vehicles and staffing, hydrant functionality, water-network performance, building materials, and observed road passability are verified, results must be described as conditional, nominal, accessibility-based, or scenario-based.

## 2. Theoretical Background  /  Conceptual Framework  /  Problem Formulation

- Research type: applied
- Section focus: Empirical context, operational interdependence, and cautious decision support under incomplete post-event information.

### Research Gap

- Existing spatial fire-risk screening can identify dense or exposed urban areas, while accessibility studies can identify nominal service gaps. Neither output alone measures how the contribution of a response base depends on the availability of other stations and roads, nor directly connects that contribution to resource-allocation choices.
- The applied gap is therefore an integrated, event-specific framework that links conditional fire consequences, disrupted network accessibility, cooperative station value, and intervention benefit while explicitly distinguishing observed conditions from imposed scenarios.
- This gap statement is provisional and requires a later primary-literature review; it is not yet a claim of novelty.

### Conceptual Framework

- Earthquake-related shaking and secondary hazards define the event context and plausible disruption scenarios. They do not determine a building-specific ignition probability in the current design.
- Built-form continuity, separation, land use, and firebreaks determine conditional spread susceptibility once an ignition is imposed. Population and critical facilities determine consequence weights.
- Roads connect response bases to demand locations. Link disruption can increase travel time, remove backup coverage, and change the marginal value of a station even when the station itself remains operational.
- The event-specific network state remains the primary planning contrast. Length-dependent independent failures, spatially clustered failures, and hazard-weighted failures are separate robustness mechanisms; none is interpreted as the observed probability that a 2026 road section failed.
- Fire stations are treated as cooperative service units. Their contribution is the reduction in a stated system loss when they join different feasible station coalitions under a scenario.
- Resource interventions modify the station set, effective access network, or bounded water-support condition. Their value is measured by the reduction in weighted conditional consequence relative to explicit baselines. Road restoration is evaluated at the road-section level, while section length or event-exposed length is retained as a cost proxy rather than treating every section as operationally equivalent.
- SHAP may be used later to explain a justified nonlinear predictive or simulation-surrogate model. It will not generate the primary risk measure, establish causality, or compensate for the lack of observed-fire labels.
- Scope boundary: The framework estimates spatial susceptibility, nominal accessibility, stochastic reliability under declared failure mechanisms, and counterfactual planning value; it does not estimate engineering fragility, actual real-time suppression capacity, repair duration, or temporal fire evolution.

### Problem Formulation

- Let \(b\) denote a building or screening grid, \(S\) a set of available fire stations, and \(\omega\) a stated earthquake-disruption and ignition scenario. Conditional consequence is represented as

\[
C_b(S, \omega) = g(Spread_b(\omega), Access_b(S, \omega), Water_b(\omega), Exposure_b),
\]

  where the functional form \(g\) and all normalizations remain subject to feasibility and robustness testing.
- Define the scenario-specific system value of a station coalition as

\[
v_{\omega}(S) = -\sum_b w_b C_b(S, \omega),
\]

  where \(w_b\) states the population, vulnerability, or critical-facility priority assigned to location \(b\).
- For station \(i\), the scenario-specific Shapley value is

\[
\phi_i(\omega) = \sum_{A \subseteq N \setminus \{i\}} \frac{|A|!(|N|-|A|-1)!}{|N|!} [v_{\omega}(A \cup \{i\}) - v_{\omega}(A)].
\]

  The current source contains 94 facility records but only 81 records marked as candidate dispatch bases; headquarters records that are not dispatch candidates and co-located duplicates will not be treated as independent players. For the retained candidate set, \(\phi_i(\omega)\) will be approximated by sampled station permutations and checked for convergence. Robust station value will summarize both the central tendency and variability of \(\phi_i(\omega)\) across scenarios.
- A leave-one-station-out measure will be reported as a transparent complement to Shapley value. Alternative system objectives, including population coverage, critical-facility protection, redundancy, and equity-sensitive weighting, will be compared rather than collapsed into an unexplained universal station-value score.
- Interpretation limit: The eight reported fires are insufficient for supervised fire-risk training. Building-level outputs are conditional scores or simulated consequences, not calibrated probabilities. Shapley values allocate the chosen modelled system value and therefore inherit its assumptions; they do not measure intrinsic station quality or causal impact.

## 3. Data Overview

### Data Scope

- Files reviewed: 43, comprising 19 immutable source inputs and 24 standardized analysis components. Source and standardized representations were both inspected, so the file count is not the number of independent evidence sources.
- Standardized records reviewed: 2,012,516 across the 24 analysis components. Component sizes range from 1 to 1,036,590 rows and from 3 to 20 retained columns.
- Variables summarized: 474 variable-file combinations.
- Distribution plots generated in the current run: 80.
- Files skipped during briefing: 0.
- Geographic scope: Kumamoto Prefecture. Prefecture-wide screening uses populated 125 m cells; building-level refinement is limited to selected priority urban clusters.

| Analysis component | Observation or geometry unit | Standardized rows | Reference period | Coverage and analytical role |
|---|---|---:|---|---|
| Administrative reporting | municipality or ward polygon | 49 | mixed boundary vintage | Prefecture-wide clipping, aggregation, and reporting |
| Building form | building footprint polygon | 1,036,590 | pre-event static reference | Coverage, separation, and continuity; no material, age, occupancy, or damage status |
| Population exposure | populated 125 m cell and disclosure-group polygon | 62,945 cells and 36,657 groups | 2020 | Population and older-population exposure; disclosure protection limits household precision |
| Road accessibility | source road segment, routable edge, emergency-route segment, and planned junction-to-junction section | 430,201 source segments, 390,234 current routed edges, and 264 emergency-route segments; section count pending final preprocessing | 2024 | Nominal routing and bounded event-specific scenarios are available; section-aware stochastic failure and restoration variables remain pending final transfer and validation |
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
| Candidate Dispatch Base | Candidate Dispatch Base | response supply | Boolean source classification used to retain eligible Shapley players. | Retain source Boolean; 81 of 94 facility records are eligible candidate dispatch bases. | yes |
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
| Road Section Failure Indicator | Replicate-Specific Road-Section Closure Indicator | robustness treatment | \(Z_{srd}=\mathbf{1}[U_{sr}<q_s(\lambda_d)]\) for road section \(s\), replicate \(r\), and severity \(d\). | Planned from one seeded uniform score per section and replicate, reused across severities to preserve nested failures. | no |
| Simulation Replicate | Stochastic Road-State Replicate Identifier | robustness identifier | Integer index for one reproducible stochastic road-state draw. | Planned deterministic-seed generation with convergence checkpoints. | no |
| Realized Failed Road Length Share | Realized Unavailable Road-Length Share | robustness diagnostic | Total Road Section Length (m) over failed sections divided by total eligible section length in one replicate. | Planned diagnostic for comparing realized and target severity. | no |
| Timely Response Probability | Probability of Nominal Fire-Service Response within Threshold | accessibility reliability outcome | Monte Carlo mean of the indicator that minimum fire-service response time does not exceed a declared threshold. | Planned separately by Road Failure Model, Expected Failed Road Length Share, and response threshold. | no |
| P90 Response Time (min) | Ninetieth-Percentile Nominal Fire-Service Response Time | accessibility reliability outcome | Empirical 90th percentile of minimum response time across stochastic road states, with disconnection reported separately. | Planned grid-level reliability summary; it is not an observed response-time percentile. | no |
| Event-Exposed Road Length (m) | Event-Hazard-Exposed Length within Road Section | intervention exposure | Sum of internal Road Length (m) assigned to Warning Zone or Special Warning Zone exposure classes within one Road Section ID. | Constructed from edge-level event exposure and set to zero where no internal edge is event-exposed. | yes |
| Event-Exposed Road Length Share | Share of Road Section Length with Event-Hazard Exposure | intervention diagnostic | Event-Exposed Road Length (m) divided by Road Section Length (m). | Constructed without imputation; values are bounded from zero to one. | yes |
| Road Restoration Cost Proxy | Relative Road-Section Restoration Resource Requirement | intervention cost proxy | Event-Exposed Road Length (m) divided by the median positive event-exposed road-section length. | Constructed only for the 42,068 event-exposed sections; unaffected sections remain missing because observed repair duration and monetary cost are unavailable. | yes |
| Building Count | Building Count per Analysis Cell | spread explanatory | \(N_j = \sum_b 1(c_b \in j)\), where \(c_b\) is the building centroid; robustness to area-weighted allocation is required. | Planned from building geometry on the 125 m analysis grid. | yes |
| Observed Building Footprint Coverage Ratio | Observed Building Footprint Coverage Ratio | spread explanatory | \(BCR_j = \sum_b Area(b \cap j) / Area(j)\). | Planned area-weighted overlay of building footprints and analysis cells. | yes |
| Mean Building Separation (m) | Mean Nearest-Building Boundary Separation | spread explanatory | Mean nearest-neighbor boundary distance among buildings assigned to or neighboring cell \(j\). | Planned in projected coordinates; neighborhood buffer is TBD. | yes |
| Built Continuity Index | Local Built-Form Continuity Index | spread explanatory | Relative connectivity of buildings under a separation threshold \(d\); the final graph statistic and \(d\) are TBD. | Planned building-adjacency sensitivity measure. | yes |
| Firebreak Share | Road, Park, Water, and Open-Space Firebreak Share | spread protective | \(F_j = Area(Firebreak \cap j) / Area(j)\); road-buffer definitions are TBD. | Planned overlay of roads, parks, water/open-space land use, and relevant planning polygons. | yes |
| Conditional Spread Susceptibility | Conditional Fire-Spread Susceptibility | intermediate outcome | \(S_j(\omega) = f(Density_j, Separation_j, Continuity_j, LandUse_j, Firebreak_j, \omega)\); function \(f\) is TBD. | Scenario score conditional on imposed ignition; not an ignition probability. | yes |
| Normal Response Time (min) | Normal-Scenario Minimum Fire-Service Travel Time | accessibility outcome | \(T_j^0 = \min_{i \in N} t_{ij}^0\). | Planned shortest-path time from candidate dispatch bases under the normal network scenario. | yes |
| Disrupted Response Time (min) | Disruption-Scenario Minimum Fire-Service Travel Time | accessibility outcome | \(T_j(\omega) = \min_{i \in N(\omega)} t_{ij}(\omega)\). | Planned shortest-path time after stated link or base disruptions. | yes |
| Backup Fire Base Count | Number of Alternative Candidate Dispatch Bases | accessibility redundancy | \(B_j(\omega) = \sum_i 1(t_{ij}(\omega) \leq \tau) - 1\); threshold \(\tau\) is TBD. | Planned count of bases beyond the nearest base that meet a stated response threshold. | yes |
| Single Route Dependence | Single-Route Dependence Indicator | accessibility vulnerability | TBD: indicator or proportion based on loss of feasible alternatives after removal of a critical route segment. | Planned from the explicitly noded road graph. | yes |
| Water Constraint Scenario | Bounded Firefighting Water-Availability Scenario | scenario input | Categorical boundary scenario; location-specific hydrant functionality is not observed. | At minimum: normal reliance and affected-area network-water-unavailable scenarios. | yes |
| Conditional Fire Consequence | Weighted Conditional Fire Consequence | main outcome | \(C_j(S, \omega) = g(Spread_j(\omega), Access_j(S, \omega), Water_j(\omega), Exposure_j)\); function \(g\) is TBD. | Scenario-based consequence conditional on ignition, not calibrated building fire probability. | yes |
| Leave-One-Out Fire Base Value | Leave-One-Out Candidate Dispatch-Base Value | station value outcome | \(V_i^{LOO}(\omega) = J(N \setminus \{i\}, \omega) - J(N, \omega)\). | Planned transparent criticality benchmark under each scenario and system objective. | yes |
| Scenario Shapley Value | Scenario-Specific Candidate Dispatch-Base Shapley Value | station value outcome | Average marginal system-value contribution of base \(i\) across feasible base coalitions under scenario \(\omega\). | Planned sampled-permutation estimate with convergence checks. | yes |
| Robust Fire Base Value | Scenario-Robust Candidate Dispatch-Base Value | station value outcome | Central tendency and variability of \(\phi_i(\omega)\) across the declared scenario set. | Planned multi-scenario summary; no universal single-objective value is assumed. | yes |
| Intervention Benefit | Weighted Conditional-Consequence Reduction from Intervention | decision outcome | \(Benefit_a(\omega) = J_0(\omega) - J_a(\omega)\). | Planned comparison with population-only, nearest-base, and road-class baselines. | yes |
## 5. Identification Strategy

### Design Principle

The study uses model-based scenario contrasts rather than causal identification or supervised prediction. It holds the mapped built environment and exposed population fixed, varies explicitly declared road, fire-base, and water-support conditions, and measures the resulting change in conditional consequence. The event-specific bounded road and water conditions are the primary planning scenarios. Stochastic road-section failures form a separate robustness layer and are never used to assign an empirical probability to the 2026 event.

The primary consequence and accessibility unit is the populated 125 m cell. Individual building footprints contribute to cell-level coverage, separation, and continuity measures but are not a reporting or prediction unit in the streamlined output plan. Candidate dispatch bases are the cooperative service units. Routable road edges retain travel impedance and connector positions, while junction-to-junction Road Section ID values define stochastic closures and section-level restoration sensitivity. The scenario set combines imposed ignition conditioning, event-specific network disruption rules, bounded water-availability assumptions, fire-base availability, and separately labelled stochastic road states. No event scenario is assigned an empirical occurrence probability.

### Identifying Contrasts

The evidence chain is based on five within-model contrasts:

1. **Built-form contrast:** compare cells with different `Observed Building Footprint Coverage Ratio`, `Mean Building Separation (m)`, `Built Continuity Index`, and `Firebreak Share` while treating ignition as imposed; use `Permitted Building Coverage Ratio` only as planning context. This identifies relative `Conditional Spread Susceptibility`, not ignition probability or burned area.
2. **Event-network contrast:** compare `Normal Response Time (min)` with `Disrupted Response Time (min)` under transparent event-specific link-removal or link-penalty rules, then examine changes in `Backup Fire Base Count` and `Single Route Dependence`.
3. **Road-reliability contrast:** hold demand and response bases fixed while repeatedly varying Road Section ID availability under nested `Expected Failed Road Length Share` levels. This produces `Timely Response Probability`, `P90 Response Time (min)`, and stability diagnostics under Length-Dependent Independent, Spatially Clustered, and Hazard-Weighted failure mechanisms.
4. **Coalition contrast:** compare system loss with and without each `Candidate Dispatch Base`, and across sampled orders in which bases join a service coalition. This produces `Leave-One-Out Fire Base Value` and `Scenario Shapley Value`. Selected stochastic states or checkpoint summaries test rank stability without nesting a full Shapley calculation inside every road replicate.
5. **Intervention contrast:** compare the same event-specific scenario before and after a response-unit pre-positioning, bounded water-support, or road-section restoration action. This produces `Intervention Benefit` under both unit-count and clearly labelled cost-proxy budgets.

### Assumptions Required for Interpretation

- Road travel speeds are fixed lookup assumptions based on `Road Category`, `Width Category`, and `Road State`; they are not observed post-earthquake speeds. `Emergency Road Service Status`, `Hazard Type`, `Warning Zone Class`, and `Special Warning Zone Pending` define bounded disruption rules rather than verified passability for every segment.
- Length-dependent section failure treats the stochastic closure of a Road Section ID as a modelled component state. It is not an engineering fragility curve. Full-section closure, connector-aware local closure, spatial clustering, hazard weighting, and the upper tail of `Road Section Length (m)` must be compared before road-reliability claims are finalized.
- All records marked `Candidate Dispatch Base` are treated as nominally comparable dispatch origins. Station-level vehicles, staffing, simultaneous demand, dispatch queues, and suppression capacity are not observed, so station values are accessibility-based rather than operational capacity estimates.
- `Water Constraint Scenario` is a boundary condition. `Service Status`, `Observed Water Outage Households`, and `Evidence Tier` may locate affected contexts, but unobserved hydrant or network status is never coded as confirmed functionality or failure.
- Built-form screening uses observed geometry and planning attributes. Building material, interior fuel, fire-resistance performance, and wind fields are unavailable as final variables; consequently, the analysis does not model directional physical fire propagation.
- Exposure objectives are reported separately for population, older-population vulnerability, and critical facilities before any combined score is interpreted. This avoids presenting a single normative weighting scheme as universal.
- Resource budgets are counts of comparable action units within response-base and water-support classes. Road-section restoration also reports `Road Restoration Cost Proxy` based on section length or event-exposed length because a short urban section and a long rural section are not equivalent actions. Cross-class combinations remain exploratory until commensurable cost, vehicle, staffing, and water-capacity information is available.

### Relationship to Planned Outputs

The built-form contrast supports the supplementary `Conditional Fire Susceptibility across Kumamoto` figure and the susceptibility fields reported in `Highest-Priority 125 m Cells`. The event-network and road-reliability contrasts jointly support `Post-Earthquake Fire-Service Accessibility`. The integrated consequence calculation supports `Conditional Fire Consequence and Vulnerable Exposure`, municipality and priority-cell summaries, and the critical-facility table. Coalition contrasts support `Fire Base Marginal Value and Robustness` and `Fire Base Value Ranking`. Intervention contrasts support `Intervention Priorities and Protection Gains` and `Intervention Performance by Budget`. Length-dependent, clustered, hazard-weighted, weight, threshold, and parameter changes support `Scenario and Parameter Robustness` and `Robustness and Sensitivity Summary`.

### Interpretation Limits

The design cannot establish that earthquake damage caused a particular fire, estimate the probability that a specific building ignites, forecast actual burned area, estimate engineering road-failure probability, or measure the causal effect of a station or intervention. The eight reported fires are not an estimation sample. Results describe internally consistent consequences, reliability, and marginal contributions within declared scenarios. A stable result is decision-relevant evidence under those assumptions, not proof of real-time firefighting or repair performance.

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

Here, \(\mathcal{S}\) is the set of eligible road sections and \(d\) is the target expected failed-road-length share. The main robustness levels are \(d \in \{0.01,0.03,0.05\}\); \(d=0.10\) is a stress case and \(d=0.005\) is a near-baseline calibration check.

For each section and replicate, one seeded uniform score \(U_{sr}\) is reused across severities:

\[
Z_{srd}=\mathbf{1}\left[U_{sr}<q_s(\lambda_d)\right].
\]

Here, \(Z_{srd}\) is `Road Section Failure Indicator` for section \(s\), replicate \(r\), and severity \(d\), and \(U_{sr}\) is a reproducible uniform score. Reusing the score makes higher-severity failed-section sets nested within replicate. `Realized Failed Road Length Share` is reported for every state. Spatially Clustered and Hazard-Weighted mechanisms preserve the same target failed length but use separately declared spatial assignment rules; they are mandatory sensitivity mechanisms rather than empirical earthquake models.

Let \(T_{jr}(d,g)\) be the minimum nominal response time to cell \(j\) after full rerouting under replicate \(r\), severity \(d\), and failure model \(g\). Grid reliability at response threshold \(\tau\) is:

\[
\pi_j(d,g,\tau)=\frac{1}{M_R}\sum_{r=1}^{M_R}\mathbf{1}\left[T_{jr}(d,g)\leq \tau\right].
\]

Here, \(\pi_j(d,g,\tau)\) is `Timely Response Probability`, \(M_R\) is the executed replicate count, and \(\tau\) is evaluated at 5, 10, and 15 minutes. `P90 Response Time (min)` is the empirical 90th percentile of \(T_{jr}(d,g)\), while the probability of disconnection is reported separately rather than replaced by a finite travel time.

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
E_j^{(F)} &= R(Q_j), \\
E_j^{(C)} &= \frac{1}{3}\left[E_j^{(P)}+R(O_j)+E_j^{(F)}\right].
\end{aligned}
\]

Here, \(E_j^{(P)}\) is population exposure, \(E_j^{(V)}\) is older-population vulnerability exposure, \(E_j^{(F)}\) is critical-facility exposure, and \(E_j^{(C)}\) is the equal-component combined screen. \(P_j\) is `Total Population` and \(O_j\) is `Population Age 65+ Share`. The objective index \(o\) takes the values population, vulnerability, facility, or combined. Alternative older-age thresholds and household-vulnerability shares are robustness specifications.

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

### 6.6 System Loss and Fire-Base Value

For each objective and scenario, system loss is:

\[
J^{(o)}(S,\omega) = \sum_j q_j C_j^{(o)}(S,\omega).
\]

Here, \(J^{(o)}(S,\omega)\) is total modelled system loss and \(q_j\) is a declared reporting weight. The main specification sets every \(q_j\) to one because exposure is already represented in \(E_j^{(o)}\). A municipality-balanced sensitivity specification gives municipalities equal aggregate influence.

The positive coalition value is the reduction in loss from a finite no-service reference:

\[
v_{\omega}^{(o)}(S) = J^{(o)}(\emptyset,\omega)-J^{(o)}(S,\omega).
\]

Here, \(v_{\omega}^{(o)}(S)\) is the accessibility-based value of coalition \(S\), and \(\emptyset\) is the no-available-base reference evaluated using \(T_{\max}\).

The transparent leave-one-out benchmark is:

\[
L_i^{(o)}(\omega) = J^{(o)}(N\setminus\{i\},\omega)-J^{(o)}(N,\omega).
\]

Here, \(L_i^{(o)}(\omega)\) is `Leave-One-Out Fire Base Value` for base \(i\). It measures the additional system loss when that base is removed from the full eligible set.

For the 81 eligible bases, sampled-permutation Shapley value is:

\[
\widehat{\phi}_i^{(o)}(\omega) = \frac{1}{M}\sum_{m=1}^{M}\left[v_{\omega}^{(o)}\left(P_i^{m}\cup\{i\}\right)-v_{\omega}^{(o)}\left(P_i^{m}\right)\right].
\]

Here, \(\widehat{\phi}_i^{(o)}(\omega)\) is `Scenario Shapley Value`; \(M\) is the number of sampled random station permutations; \(m\) indexes a permutation; and \(P_i^{m}\) is the set of bases preceding base \(i\) in permutation \(m\). Estimation proceeds in batches and reports Monte Carlo uncertainty. Convergence requires stable top-base membership, high rank correlation between successive batches, and sufficiently narrow Monte Carlo intervals; failure to meet the declared criteria by the computation cap is reported rather than hidden.

Scenario contributions are normalized before constructing a robust score:

\[
u_i^{(o)}(\omega) = \frac{\widehat{\phi}_i^{(o)}(\omega)}{\sum_{\ell \in N}\widehat{\phi}_{\ell}^{(o)}(\omega)}, \qquad R_i^{(o)} = \operatorname{median}_{\omega}u_i^{(o)}(\omega)-\kappa\operatorname{IQR}_{\omega}u_i^{(o)}(\omega).
\]

Here, \(u_i^{(o)}(\omega)\) is base \(i\)'s share of total coalition value; \(\ell\) indexes eligible bases in the denominator; \(R_i^{(o)}\) is `Robust Fire Base Value`; \(\operatorname{IQR}\) is the interquartile range across declared scenarios; and \(\kappa\) is the instability penalty. The main specification sets \(\kappa\) to \(1/2\), with zero, one, median-only, and worst-case rankings reported as sensitivity checks. A zero total coalition value is reported as an unidentified station-value scenario. The accepted station-value figure retains normal and bounded event-specific road scenarios. Broader robustness uses representative seeded stochastic states or checkpoint summaries to measure rank correlation and top-base overlap; a complete sampled-permutation Shapley experiment is not repeated inside every road-failure replicate unless computational feasibility and convergence are demonstrated.

### 6.7 Intervention Evaluation

An intervention may add a temporary dispatch origin at a screened candidate location, restore a disrupted Road Section ID, or change the bounded water penalty for selected high-consequence cells. Intervention benefit is:

\[
Benefit_a^{(o)}(\omega) = J_0^{(o)}(\omega)-J_a^{(o)}(\omega).
\]

Here, \(Benefit_a^{(o)}(\omega)\) is `Intervention Benefit`; \(J_0^{(o)}(\omega)\) is baseline system loss; and \(J_a^{(o)}(\omega)\) is system loss after intervention \(a\). Candidate temporary origins are screened from high-priority `Mesh Code` locations and feasible public or response facilities; restoration candidates are disrupted road sections under the event-specific scenario; water-support candidates are high-consequence cells under the constrained-water boundary. Restoring a section reactivates its disrupted internal edges for routing, but does not imply that every metre required physical repair.

For a unit-count budget, the robust allocation target is:

\[
\mathcal{A}_{K}^{*} = \arg\max_{\mathcal{A}' \subseteq \mathcal{A}} \operatorname{median}_{\omega}\left[J_0^{(o)}(\omega)-J_{\mathcal{A}'}^{(o)}(\omega)\right] \quad \text{subject to} \quad \sum_{a \in \mathcal{A}'} c_a \leq K.
\]

Here, \(\mathcal{A}\) is the candidate action set; \(\mathcal{A}'\) is a selected action bundle; \(\mathcal{A}_{K}^{*}\) is the best robust bundle under budget \(K\); \(c_a\) is the declared resource requirement for action \(a\); and \(J_{\mathcal{A}'}^{(o)}(\omega)\) is loss after the action bundle. Response-base and water-support analyses first use within-class unit counts. Road restoration reports both a section-count screen and `Road Restoration Cost Proxy`, defined from `Road Section Length (m)`, event-exposed length, or a clearly labelled combination. Exact enumeration is used when feasible; otherwise forward selection is labeled as a heuristic. Results are compared with population-only placement, nearest-base placement, highest-road-class restoration, and restoration-benefit-per-cost-proxy baselines. Cross-class bundles are not called cost-optimal without commensurable cost data.

### 6.8 Robustness, Heterogeneity, and Failure Modes

- **Built form:** vary component weights, building-adjacency thresholds, firebreak definitions, scaling method, component inclusion, and cell-assignment rules; use `Permitted Building Coverage Ratio` only for descriptive planning-context contrasts and do not infer building-specific propagation.
- **Accessibility:** vary road-speed lookup assumptions, disruption rules, snapping tolerance, unmet-service cap, and the \(5\)-, \(10\)-, and \(15\)-minute response thresholds.
- **Road reliability:** compare 1%, 3%, and 5% `Expected Failed Road Length Share`, the 10% stress case, Length-Dependent Independent, Spatially Clustered, and Hazard-Weighted failure models, full-section versus connector-aware local-fragment closure, and 100-1,000 replicate checkpoints.
- **Exposure:** report population, older-population, facility, and combined objectives separately; vary older-age and household-vulnerability measures and facility weights.
- **Station value:** compare `Leave-One-Out Fire Base Value` with `Scenario Shapley Value`; report sampled-permutation convergence, Monte Carlo uncertainty, scenario rank correlation, and top-base overlap.
- **Interventions:** compare median, lower-quartile, and worst-case benefit; test unit-count, section-length, and event-exposed-length budgets and baseline allocation rules; report whether conclusions reverse under modest changes.
- **Heterogeneity:** summarize by `Municipality Name`, `Land Use Zone Name`, `Urban Land Use Code`, `Fire Prevention Area Type`, critical-facility class, and normal versus disrupted accessibility.
- **Failure modes:** stop or downgrade claims when road topology yields implausible routes, large areas are disconnected under the normal network, stochastic results are dominated by the upper tail of `Road Section Length (m)`, reliability estimates do not converge, building rankings are driven by one component, Shapley estimates do not converge, robust rankings collapse across minor specifications, or intervention rankings fail to outperform simple baselines and cost-proxy alternatives.

## 7. Analytical Workflow

The accepted framework and supplementary susceptibility figure document the study logic and cell-level built-form screen. All result claims that depend on the streamlined pending figures, stochastic road reliability, tables, or section-aware intervention re-estimation remain inconclusive until the corresponding output is generated and reviewed. Building footprints are inputs to the 125 m screen; no workflow step produces a building-level result.

| step | variables used | formula/model used | generated figure/table title | theory or claim evaluated | support status |
|---|---|---|---|---|---|
| 1. Freeze scope, units, scenarios, and evidence boundaries | `Disruption Type`; `Service Status`; `Emergency Road Service Status`; `Water Constraint Scenario`; `Candidate Dispatch Base`; `Verification Status` | Section 5 scenario-contrast design and Section 6.1 scenario set | `Integrated Fire Consequence and Station Value Framework`; `Scenario Definitions and Interpretation Boundaries` | The analysis distinguishes observed context from imposed scenarios and connects risk screening to resource decisions. | Supported by the accepted framework and scenario definitions; detailed data coverage and limitations remain documented in Sections 3-4 rather than a redundant result table. |
| 2. Construct prefecture-wide built-form components | `Observed Building Footprint Coverage Ratio`; `Permitted Building Coverage Ratio`; `Mean Building Separation (m)`; `Built Continuity Index`; `Firebreak Share`; `Land Use Zone Name`; `Urban Land Use Code` | Empirical percentile transform and conditional susceptibility score in Section 6.2 | `Conditional Fire Susceptibility across Kumamoto`; `Highest-Priority 125 m Cells`; `Robustness and Sensitivity Summary` | Supporting Point 1 at the grid level: dense, continuous development with fewer firebreaks has higher conditional spread susceptibility, while permitted intensity remains contextual rather than a realized morphology input. | Partially supported by the accepted supplementary figure; ablations and rank-stability checks remain pending, and no building-level claim is supported. |
| 3. Build and validate normal and event-disrupted accessibility | `Road Category`; `Width Category`; `Road State`; `Emergency Road Service Status`; `Hazard Type`; `Candidate Dispatch Base`; `Normal Response Time (min)`; `Disrupted Response Time (min)`; `Backup Fire Base Count`; `Single Route Dependence` | Shortest-path, redundancy, route-concentration, and accessibility-penalty formulas in Section 6.3 | `Post-Earthquake Fire-Service Accessibility`; `Municipality Fire Consequence and Accessibility Summary` | Supporting Point 2: bounded event-specific disruptions create reproducible response delays and redundancy losses at high-consequence locations. | Inconclusive until the streamlined accessibility figure and municipality summary are regenerated; observed passability remains unavailable. |
| 4. Simulate road-section reliability | `Road Section ID`; `Road Section Length (m)`; `Road Edge Count`; `Road Failure Model`; `Expected Failed Road Length Share`; `Failure Intensity per Metre`; `Section Failure Probability`; `Road Section Failure Indicator`; `Simulation Replicate`; `Realized Failed Road Length Share`; `Timely Response Probability`; `P90 Response Time (min)` | Finalized length-dependent calibration inputs, nested paired failure assignment, full rerouting, reliability probability, and convergence framework in Section 6.4 | `Post-Earthquake Fire-Service Accessibility`; `Scenario and Parameter Robustness`; `Scenario Definitions and Interpretation Boundaries`; `Robustness and Sensitivity Summary` | Supporting Point 2: event-specific accessibility patterns are not artifacts of one deterministic road-removal rule. | Inconclusive: static section and probability inputs are finalized, but replicate-specific states, clustered and hazard-weighted alternatives, reliability outputs, convergence, and long-section checks remain pending. |
| 5. Construct exposure objectives and conditional consequence | `Observed Building Footprint Coverage Ratio`; `Permitted Building Coverage Ratio`; `Total Population`; `Population Age 65+ Share`; `Medical Facility ID`; `School Facility ID`; `Welfare Facility ID`; `Shelter ID`; `Evacuation Site ID`; `Water Constraint Scenario`; `Conditional Spread Susceptibility`; `Disrupted Response Time (min)`; `Conditional Fire Consequence` | Exposure-objective and conditional-consequence formulas in Section 6.5 | `Conditional Fire Consequence and Vulnerable Exposure`; `Municipality Fire Consequence and Accessibility Summary`; `Highest-Priority 125 m Cells`; `Priority Critical Facilities` | Central question and Supporting Point 1 at the grid level: susceptibility, constrained response, water boundaries, and exposure jointly identify high-consequence locations; older-population results are retained in tables rather than a redundant map panel. | Inconclusive until the streamlined two-panel figure and reporting tables are generated and sensitivity specifications are reviewed. |
| 6. Estimate base marginal contribution | `Fire Base Name`; `Fire Base Type`; `Candidate Dispatch Base`; `Leave-One-Out Fire Base Value`; `Scenario Shapley Value`; `Robust Fire Base Value`; `Conditional Fire Consequence`; `Road Failure Model`; `Expected Failed Road Length Share` | System-loss, leave-one-out, sampled Shapley, robust-value, and selected stochastic-state rank-stability framework in Section 6.6 | `Fire Base Marginal Value and Robustness`; `Fire Base Value Ranking`; `Scenario and Parameter Robustness` | Supporting Point 3: station value depends on substitutability and remains interpretable across disruption and demand scenarios. | Partially supported by existing event-specific estimates with a recorded convergence limitation; the streamlined two-panel figure and stochastic-state stability checks remain pending. |
| 7. Evaluate resource interventions | `Mesh Code`; `Candidate Dispatch Base`; `Road Section ID`; `Road Section Length (m)`; `Route Name`; `Event-Exposed Road Length (m)`; `Road Restoration Cost Proxy`; `Disrupted Response Time (min)`; `Backup Fire Base Count`; `Water Constraint Scenario`; `Conditional Fire Consequence`; `Intervention Benefit`; `Robust Fire Base Value` | Intervention-benefit, section-count, cost-proxy, and heuristic allocation formulas in Section 6.7 | `Intervention Priorities and Protection Gains`; `Intervention Performance by Budget` | Supporting Point 4: selected actions reduce conditional consequence more robustly than simple allocation and road-class baselines. | Inconclusive until the superseded edge-level analysis is replaced by section-level actions and gains exceed both simple and cost-proxy baselines. |
| 8. Stress-test rankings and decisions | `Conditional Spread Susceptibility`; `Conditional Fire Consequence`; `Scenario Shapley Value`; `Robust Fire Base Value`; `Intervention Benefit`; `Water Constraint Scenario`; `Road Failure Model`; `Expected Failed Road Length Share`; `Timely Response Probability`; `Road Restoration Cost Proxy` | Sensitivity, ablation, convergence, rank-correlation, overlap, and failure-mode checks in Sections 6.2-6.8 | `Scenario and Parameter Robustness`; `Robustness and Sensitivity Summary` | Central question: grid, station, and intervention priorities are not artifacts of one reasonable modelling choice. | Inconclusive until robustness thresholds are met; otherwise claims are partially supported or not supported. |

### Evidence Checkpoints

1. **Supporting Point 1:** supported at the 125 m grid level only if high-susceptibility cells remain comparatively high under alternative weights, thresholds, scaling, component definitions, and cell-assignment rules. If one component or grid definition controls the rankings, support is partial or absent. The streamlined plan does not support a building-level result.
2. **Supporting Point 2:** supported only if the normal network is credible, the bounded event-specific rule produces coherent response-time and redundancy losses, and section-aware reliability remains interpretable across length-dependent, spatially clustered, and hazard-weighted failures. Dominance by implausibly long sections, connector artifacts, or nonconvergence makes the stochastic part inconclusive.
3. **Supporting Point 3:** supported only if sampled Shapley estimates converge or retain an explicit limitation, broadly agree with transparent leave-one-out patterns where expected, and retain meaningful rank stability across exposure, event-specific disruption, and selected stochastic road states. Otherwise station value is scenario-specific or unidentified.
4. **Supporting Point 4:** supported only if intervention bundles outperform the stated simple baselines across multiple scenarios and road restoration remains useful under section-count and length- or exposed-length-based cost proxies. Without comparable action costs, the evidence supports within-class prioritization but not a cost-optimal mixed portfolio.
5. **Central Research Question:** fully supported only when the susceptibility, accessibility, station-value, and intervention checkpoints all pass. If one component fails, conclusions are restricted to the components that remain supported. The design never converts these checkpoints into causal, probability, or real-time-capacity claims.

## 8. Figure and Table Plan

This confirmed streamlined plan retains five main-text and two supplementary figures, plus five main-text and two supplementary tables. The redundant building-scale cluster figure and the redundant data-coverage table are removed. Existing figures that require a changed panel structure or the new road-section analysis return to `pending`; the accepted framework and susceptibility-component figure remain `done`. No time-series output is included. The eight observed fires are reserved for plausibility checking rather than model training. `Scenario Shapley Value` denotes cooperative-game marginal station value and is not a machine-learning SHAP explanation.

### Figures

| title | what it expresses | figure type | subpanels | key variables | status |
|---|---|---|---:|---|---|
| Integrated Fire Consequence and Station Value Framework | Main: the complete analytical chain from built form, post-earthquake accessibility, water constraints, and exposure through conditional consequence, fire-base marginal value, and intervention benefit. | conceptual flow diagram | 1 | `Conditional Spread Susceptibility`, `Disrupted Response Time (min)`, `Water Constraint Scenario`, `Conditional Fire Consequence`, `Scenario Shapley Value`, `Intervention Benefit` | done |
| Conditional Fire Consequence and Vulnerable Exposure | Main: where population and essential services overlap with conditional spread susceptibility and constrained response to create the greatest conditional consequences. | choropleth and point-overlay maps | 2 | `Conditional Spread Susceptibility`, `Total Population`, `Medical Facility ID`, `Welfare Facility ID`, `Shelter ID`, `Conditional Fire Consequence`, `Geometry` | done |
| Post-Earthquake Fire-Service Accessibility | Main: how event-specific disruption and additional road-section uncertainty change response time, 10-minute backup coverage, and reliable timely arrival. | network-based gridded maps | 4 | `Normal Response Time (min)`, `Disrupted Response Time (min)`, `Backup Fire Base Count`, `Timely Response Probability`, `Geometry` | done |
| Fire Base Marginal Value and Robustness | Main: where accessibility-based fire-base value is concentrated and which candidate bases retain high marginal value across declared scenarios. | map and ranked dot plot | 2 | `Fire Base Name`, `Candidate Dispatch Base`, `Scenario Shapley Value`, `Robust Fire Base Value`, `Geometry` | done |
| Intervention Priorities and Protection Gains | Main: where pre-positioning, bounded water support, and junction-to-junction road-section restoration reduce weighted conditional consequence under the event-specific scenario, and how road priorities change between section-count and length-aware cost-proxy budgets. | map, comparative bar plot, and budget-benefit curve | 3 | `Intervention Benefit`, `Conditional Fire Consequence`, `Disrupted Response Time (min)`, `Backup Fire Base Count`, `Water Constraint Scenario`, `Road Section ID`, `Road Section Length (m)`, `Route Name`, `Road Restoration Cost Proxy`, `Geometry` | done |
| Conditional Fire Susceptibility across Kumamoto | Supplementary: how building coverage, built continuity, and mapped firebreak conditions combine into the conditional spread-susceptibility screen. | gridded maps | 3 | `Observed Building Footprint Coverage Ratio`, `Mean Building Separation (m)`, `Built Continuity Index`, `Firebreak Share`, `Conditional Spread Susceptibility`, `Geometry` | done |
| Scenario and Parameter Robustness | Supplementary: whether alternative road-section failure mechanisms change response reliability, high-value-fire-base membership, or intervention priorities relative to the event-specific main scenario. | diagnostic plot and heatmaps | 3 | `Road Failure Model`, `Expected Failed Road Length Share`, `Simulation Replicate`, `Realized Failed Road Length Share`, `Timely Response Probability`, `P90 Response Time (min)`, `Scenario Shapley Value`, `Robust Fire Base Value`, `Intervention Benefit`, `Road Restoration Cost Proxy` | done |

### Tables

| title | what it expresses | rows | columns | row meaning | column meaning | status |
|---|---|---:|---:|---|---|---|
| Scenario Definitions and Interpretation Boundaries | Main: the common ignition-conditioned analysis, event-specific road disruption, stochastic road-section failure, water-availability, and fire-base-availability assumptions, analytical purposes, and interpretation boundaries. | 12 scenarios plus 1 symbol key | 8 | One declared baseline, event-specific, stochastic, stress, or sensitivity scenario; the final row defines all codes and percentage values. | Scenario label; road state; Road Failure Model; Expected Failed Road Length Share; water constraint; available candidate bases; analytical purpose; interpretation boundary. | done |
| Municipality Fire Consequence and Accessibility Summary | Main: municipality-level differences in exposed population, older-population share, accessibility degradation, response redundancy, and aggregate conditional fire consequence. | 49 | 12 | One municipality or ward-level reporting unit. | Municipality identifiers; population and vulnerability; normal and disrupted response summaries; backup-base and route-dependence summaries; high-consequence-cell count; aggregate conditional consequence. | done |
| Priority Critical Facilities | Main: a balanced reader-facing selection of hospitals, welfare facilities, schools, shelters, and evacuation sites located in cells with high conditional consequence or weak post-earthquake fire-service accessibility. | 20 | 9 | One of the four highest-priority assigned facilities in each of five facility classes. | Priority rank; facility class; municipality; relevant capacity or designation; mesh; surrounding conditional consequence; disrupted response time; backup-base count; priority score. | done |
| Fire Base Value Ranking | Main: the transparent and coalition-based marginal value of the 20 highest-ranked eligible candidate dispatch bases and the robustness of their value across road scenarios; the full 81-base result remains in the derived data. | 20 | 9 | One of the 20 eligible candidate dispatch bases with the largest population-objective robust value. | Robust rank; English fire-base label and type; municipality; event leave-one-out share; normal- and event-road Shapley shares; robust value share; road-scenario IQR. | done |
| Intervention Performance by Budget | Main: paired performance of greedy and simple-baseline fire-resource pre-positioning, bounded water support, and road-section restoration at representative unit-count and length-aware cost-proxy budgets. | 12 | 10 | One action class, budget definition, and displayed budget level; greedy and baseline results are paired within the row. | Action type; budget definition and level; greedy and baseline budget used; intervention benefit; consequence-reduction percentage; greedy advantage over baseline. | done |
| Highest-Priority 125 m Cells | Supplementary: the complete cell-level list supporting priority verification, patrol, access protection, or resource pre-positioning; the main text reports only its geographic concentration and principal capability gaps. | 50 | 14 | One high-priority 125 m analysis cell. | Mesh and municipality identifiers; `Observed Building Footprint Coverage Ratio`; `Permitted Building Coverage Ratio`; separation, continuity, and firebreak indicators; exposure; disrupted accessibility; water scenario; conditional consequence; priority rank. | done |
| Robustness and Sensitivity Summary | Supplementary: exact nonredundant values supporting road-response reliability, fire-base priority stability, road-intervention stability, and the final reliability-convergence checkpoint. | 16 | 8 | One selected severity, alternative failure mechanism, fire-base stability test, intervention stability test, or convergence checkpoint. | Domain; specification; Road Failure Model; Expected Failed Road Length Share; primary and secondary results; assessment; interpretation. | done |

⚠️ 警告：以下 Section 8 变量在 Section 4 中仍标记为非最终分析变量，必须完成随机道路状态生成和可达性可靠性分析后才能生成对应输出：

- `Road Section Failure Indicator`, `Simulation Replicate`, and `Realized Failed Road Length Share` for replicate-specific stochastic road states.
- `Timely Response Probability` and `P90 Response Time (min)` for accessibility reliability reporting.
