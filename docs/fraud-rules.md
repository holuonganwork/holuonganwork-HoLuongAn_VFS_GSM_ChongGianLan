# Explainable fraud rules

All thresholds below are **demonstration settings for synthetic data**. A signal means that an
investigator should inspect the records; it does not establish intent or authorize punishment.
Defaults and validated overrides are centralized in `app/core/config.py` (`FRAUD_RULES` JSON).
All time intervals are UTC; location distances use the haversine formula with Earth radius
6,371.0088 km. Detection compares full precision values and rounds only displayed evidence.

## GPS: impossible speed

- **Rule name:** `impossible_speed`, category `gps_spoofing`, high severity.
- **Reason:** A consecutive GPS segment implies implausible vehicle speed.
- **Inputs:** Adjacent GPS events in ingestion-ID order within the same trip, their timestamps,
  coordinates, and original trip ID.
- **Condition:** Movement distance is at least `gps_min_distance_km` (0.1 km), elapsed time is
  positive, and `distance_km / elapsed_seconds * 3600 > gps_max_speed_kmh` (180 km/h).
  Segments satisfying the large-jump rule below receive its more specific name instead.
- **Score:** GPS category contributes 30 once, regardless of the number of GPS signals.
- **Evidence:** Both coordinates, timestamps and GPS event IDs, calculated distance, elapsed
  seconds, calculated speed, threshold settings, trip ID, and relational links to the three records.
- **Limitations:** GPS error, tunnels and timestamp defects may explain a signal. This is a straight-line
  lower bound, without road matching or sensor accuracy. No between-trip movement is evaluated.

## GPS: sudden location jump

- **Rule name:** `gps_location_jump`, category `gps_spoofing`, high severity.
- **Reason:** A substantial location change in very little time warrants inspection.
- **Inputs:** The same consecutive within-trip observations as the speed rule.
- **Condition:** Positive elapsed time is at most `gps_jump_seconds` (60), and distance is at least
  `gps_jump_distance_km` (5), after applying the minimum-movement floor.
- **Score:** Shares the same single 30-point GPS category contribution.
- **Evidence:** Full coordinate/time pair, GPS IDs, trip ID, measured distance/time/speed and limits.
- **Limitations:** A location fix after signal loss can resemble teleportation. Different jump and
  speed settings can flag different segments. One rule name is emitted per segment; a teleport
  followed by a return to the original area can produce two evidence items.

## GPS: inconsistent sequence

- **Rule name:** `inconsistent_gps_sequence`, category `gps_spoofing`, high severity.
- **Reason:** Recorded times should progress in ingestion order for a trip.
- **Inputs:** Consecutive GPS events ordered by ID (the milestone's ingestion sequence).
- **Condition:** Elapsed time is negative, or elapsed time is zero with movement of at least
  `gps_min_distance_km` (0.1). Identical stationary duplicates and sub-threshold jitter are ignored.
- **Score:** Shares the same single 30-point GPS category contribution.
- **Evidence:** Original coordinate/time pair, IDs, distance and signed elapsed seconds. Speed is
  `null` for nonpositive intervals; the engine never divides by zero or stores infinity.
- **Limitations:** Out-of-order network arrival or clock correction can trigger this rule.
  IDs must represent ingestion order; future ingest APIs should record sequence explicitly.

## Repeated short route

- **Rule name:** `repeated_short_route`, category `repeated_trips`, high severity.
- **Reason:** Numerous very short rides repeating the same route can indicate artificial activity.
- **Inputs:** A driver's trip start/end times, pickup/drop-off coordinates, reported distance and IDs.
- **Condition:** At least `repeat_min_trips` (8) short trips in a rolling `repeat_window_hours` (24)
  window. Each is at most `repeat_max_distance_km` (1 km) and has duration in
  `(0, repeat_max_duration_seconds]` (300 seconds). Each pickup and drop-off must be within
  `repeat_radius_km` (0.2 km) of the respective anchor coordinates. Windows include their start
  and exclude their end; they cross midnight. A route direction matters.
- **Score:** Repeated-trip category contributes 25 once.
- **Evidence:** All matched trip IDs and source links; count, actual time span, window bounds,
  anchor coordinates, maximum pickup/drop-off deviations, and all thresholds.
- **Limitations:** Legitimate shuttle/queue work can repeat routes. Coordinates are compared to
  one anchor, not a complex spatial cluster; this is quadratic for a driver's candidate trips.
  Only the largest qualifying group is emitted (earliest anchor wins ties). Long repeated routes
  and purely high-volume behavior are not detected by this initial rule.

## Shared device across accounts

- **Rule name:** `device_shared_by_accounts`, category `shared_device`, medium severity.
- **Reason:** A device observed on several accounts creates a useful investigation link.
- **Inputs:** Device identifier, distinct driver-device associations, first/last use times,
  driver database IDs and external IDs.
- **Condition:** At least `shared_device_min_drivers` (3) distinct drivers have used the device.
  A signal is generated for every linked driver, including D027, D028 and D029 in the fixture.
- **Score:** Shared-device category contributes 25 once, even if several devices qualify.
- **Evidence:** Device ID/identifier, all account IDs, other accounts' external IDs, distinct count,
  first/last-seen association snapshots, and FKs to the device and all drivers.
- **Limitations:** Fleet hardware, loaned/recycled phones and account recovery may explain sharing.
  Historical association is sufficient; overlap or simultaneous login is not required. This rule
  does not establish that a device identifier is resistant to spoofing.

## Promotion short-trip burst

- **Rule name:** `promotion_short_trip_burst`, category `promotion_abuse`, high severity.
- **Reason:** A dense window of rewarded short trips reaching an incentive threshold warrants review.
- **Inputs:** Promotion validity period, trip threshold/reward amount, and all of the driver's trips
  wholly inside the period, including trips without promotion usage.
- **Condition:** Consider rolling 24-hour windows anchored at eligible trip starts. A promoted trip
  references this promotion and has positive promotion amount. Its window must have at least
  `max(promotion_min_trips, promotion.trip_threshold)` promoted trips (default minimum 10),
  promoted count / **all trips in the window** at least `promotion_min_ratio` (0.8), and
  short promoted count / promoted count at least `promotion_min_short_ratio` (0.8).
  Short-trip limits are shared with the repeated-trip rule. Trip starts use an exclusive window end;
  trips must start on/after promotion start and finish on/before promotion end.
- **Score:** Promotion category contributes 20 once; other categories remain independent.
- **Evidence:** Promotion ID/code/threshold/reward, measured counts and both ratios, total promotion
  amount, window bounds, all denominator trip IDs, promoted/short subsets, threshold settings,
  and FKs to the promotion and every trip used in the comparison.
- **Limitations:** There is no real payout integration or eligibility ledger: a threshold is observed,
  not proof a bonus was paid. The rule does not model baseline volume growth or sophisticated
  threshold gaming. Only the qualifying window with most promoted trips per promotion is retained;
  earliest anchor wins ties. Promotions may overlap, and each is evaluated independently.

## Score interpretation

```text
risk = min(100, sum(weight for each distinct signaled category))
```

Default contributions are GPS 30, repeated trips 25, shared device 25, promotion abuse 20.
Weights are nonnegative integers up to 100; all categories must be present when weights are
overridden. A zero-weight signal still has evidence and can form a zero-risk case. Scores are
an investigation ordering aid, not calibrated fraud probabilities.

Every case stores its overall score, all pre-cap category contributions, complete rule settings,
and every emitted signal. Evidence `score` repeats a category's configured weight for readability;
reviewers should use `score_breakdown`, not sum evidence weights. For D050, repeated-trip evidence
and promotion evidence yield 25 + 20 = 45. No rule decides the final case status or driver status.
