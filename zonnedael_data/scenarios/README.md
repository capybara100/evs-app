# Test scenarios

Four test files, all for one real home: Klant 34, 1 January to 31 March 2013. It's a terraced house (rijtjeswoning) from 1940-1979 with a family with children, and its data is complete for the whole period. The columns are the same as in zonnedael_daily_weather.csv.

Only high_use and missing have fake changes in them. Those rows are marked with an extra column, so you can always tell what's real.

## normal.csv

90 days of real data, nothing changed.

**What should happen:** nothing special. Gas goes up on cold days and down on mild days. No events, no data problems.

## high_use.csv

Same as normal, but gas was bumped up on four cold days. Those rows have synthetic_event = true.

| Date | Temp (°C) | Real gas (m³) | Fake gas (m³) | Extra |
|---|---|---|---|---|
| 2013-01-16 | -7.2 | 10.6 | 14.9 | +40% |
| 2013-01-25 | -5.3 | 12.0 | 18.6 | +55% |
| 2013-02-22 | -2.0 | 10.8 | 17.2 | +60% |
| 2013-03-12 | -2.5 | 9.5 | 13.8 | +45% |

**What should happen:** event detection flags these four days and nothing else. They're all cold days, so it only works if you compare gas with the temperature, not with a flat average. A tip for these days shouldn't tell people to heat less than they need.

## incomplete.csv

Only the last 10 days (22-31 March), with the house columns (woning_type, bouwjaar_band, gezinssituatie) left empty. The meter data itself is real.

**What should happen:** the app still runs, but it should say there isn't enough history for a proper profile yet. It shouldn't guess the house type.

## missing.csv

Same as normal, with some days broken on purpose. Those rows have synthetic_gap = true.

| Date | What was changed | quality_flag |
|---|---|---|
| 2013-01-09 | Emptied the whole day | missing |
| 2013-01-21 | Only 19 of 24 gas hours, gas empty | partial |
| 2013-02-05 | Only 84 of 96 quarter-hours, electricity empty | partial |
| 2013-02-13 | Emptied the whole day | missing |
| 2013-02-27 | Removed the row completely | (no row) |
| 2013-02-28 | Removed the row completely | (no row) |
| 2013-03-06 | Emptied the whole day | missing |
| 2013-03-18 | Some gas hours and quarter-hours missing, both empty | partial |

**What should happen:** these eight days show up as data problems, not as low use or weird use. The two removed days have no row at all, so you can only find them by spotting the gap in the dates. Everything else should look the same as in normal.csv.
