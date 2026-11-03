# Zonnedael daily dataset

## What this data is

Smart-meter data from Liander, a Dutch grid operator. Liander describes it as 2012-2014, but the files used here only cover 2013. About 80 anonymised addresses, shared by the residents for research.

| Raw file | Content | Resolution | Unit | Period |
|---|---|---|---|---|
| Slimme meter | Gas use | hourly | m³ per hour | 1-1-2013 – 31-12-2013 |
| Levering | Electricity taken from the grid | 15 min | Wh per 15 min | 1-1-2013 – 31-12-2013 |
| Teruglevering | Electricity fed back to the grid | 15 min | Wh per 15 min | 1-1-2013 – 31-1-2014 |
| Klanttypering | House type, year built, household type | per home | categories | n/a |

The files are semicolon-separated with a decimal comma. Timestamps look like 31-1-2014 23:15, no zero padding. Households are anonymous (Klant 1 … Klant 82) and some numbers don't appear in the data. Levering has about 35,000 empty rows after the data and Teruglevering has an extra totals row above the header. Both are ignored.

Liander says it already corrected the data. Missing or unrealistic values were replaced, in places by averages, and incomplete series were removed. It isn't visible which values were corrected.

## Changes made

Everything is summed to daily totals, since the app works on data that arrives the next day (T+1). Gas is the 24 hourly values added up, in m³. Electricity is the 96 quarter-hour values added up and divided by 1000, so kWh.

20 of the 78 households are out, 58 are left. Nine have solar panels (more than 20 kWh fed back in 2013). For them Levering is net use, use minus their own production, so it isn't real consumption. Most tenants in Heerlen-Noord have no solar panels anyway. Six use less than 100 m³ of gas a year, so they probably don't heat with gas. Five miss more than 5% of their gas hours, twelve miss more than 5% of their electricity intervals, and one has no electricity data. Some homes fail more than one check. The reason per home is in household_summary.csv.

Each day also has quality columns: how many gas hours (should be 24), how many electricity intervals (should be 96), and a flag that says ok, partial or missing. On partial days the value is empty, so a total that's too low doesn't get used by mistake. House type, build year band and household type come from Klanttypering, where it has them.

No values were interpolated, imputed or smoothed, and no outliers were removed.

## Result

58 households and 21,170 daily rows. 21,064 are ok, 89 are partial and 17 are missing. Only 30 homes have their house info filled in. Median daily gas per home is about 7.9 m³ in Jan-Mar and 0.6 m³ in Jul-Aug, which is what you'd expect. Median electricity is about 8.6 kWh a day.

The output is zonnedael_daily_weather.csv (one row per household per day, with weather) and household_summary.csv (per household, included or not and why). Columns in the daily file: household_id, date, electricity_kwh, gas_m3, n_elec_intervals, n_gas_hours, quality_flag, woning_type, bouwjaar_band, gezinssituatie, temp_mean_c, temp_min_c, temp_max_c, hdd18. The three house columns (woning_type, bouwjaar_band, gezinssituatie) can be empty.

## Limitations

Zonnedael is a fictional name and the real location isn't given. So the closest weather station can't be picked. KNMI station 260 (De Bilt), which is central in the Netherlands, is used instead and joined by date. That adds temp_mean_c, temp_min_c, temp_max_c and hdd18 (degrees below 18 °C). Local weather in the real place will differ a bit. The data is only 2013, so Jan-Mar 2013 is used as the winter. Flat stretches might be values Liander filled in.

Liander says local Dutch time. On 31 March 2013, when the clocks went forward, every home still has 24 gas hours and 96 electricity intervals. On 27 October 2013, when the clocks went back, every home has only 22 gas hours, while electricity still has 96 intervals. So that day is partial for all 58 homes and its gas value is empty. This is 58 of the 89 partial days. The 20 kWh solar limit is a chosen threshold, not a standard. Klant 1 fed back 25 kWh and is out as a borderline case. A few homes feed back under 2 kWh, which looks like noise, so they stay in. A full day of zero gas in winter isn't flagged.

It's 2013 data, so heating habits and prices are different now. It isn't P4 data either. It is treated as a development dataset. It's real smart-meter data in the same daily T+1 format as P4. In the pilot, P4 data replaces it once the tenant gives consent.

## Source

Liander open data, "Verbruiksdata slimme meter 2012-2014" (Zonnedael), https://www.liander.nl/over-ons/open-data
