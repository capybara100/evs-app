# Zonnedael daily data

Here's the data for the demo. The weather is already joined in, so you don't need to do anything with the KNMI files.

## What's in here

**zonnedael_daily_weather.csv** is the main file. It has one row per household per day: 58 homes, all of 2013, 21,170 rows. The data is daily and comes in the next day (T+1).

**household_summary.csv** lists every home, whether it was kept, and why not if it wasn't (solar panels, almost no gas, too many gaps).

**scenarios/** has four small test files for one home (Klant 34, Jan-Mar 2013). They're good for testing your stuff. The README in there explains them.

**data_note_zonnedael.md** has the background, if you want to know where the data comes from and what was changed.

## Columns

| Column | What it is |
|---|---|
| household_id | Anonymous home code, like Klant 34 |
| date | YYYY-MM-DD |
| electricity_kwh | Electricity used that day, in kWh. Can be empty |
| gas_m3 | Gas used that day, in m³. Can be empty |
| n_elec_intervals | How many quarter-hours came in (96 = full day) |
| n_gas_hours | How many hours came in (24 = full day) |
| quality_flag | ok, partial (some data came in) or missing (none came in) |
| woning_type, bouwjaar_band, gezinssituatie | House type, build year, household type. Empty for about half the homes |
| temp_mean_c, temp_min_c, temp_max_c | Temperature that day in °C (KNMI De Bilt) |
| hdd18 | Heating degree days: how far the mean temp was below 18 °C |

## Watch out for

**Empty means the data didn't come in, not zero use.** Check quality_flag, and don't count those days as weird use.

**Compare gas with the temperature or hdd18.** Cold days use more gas, and that's normal.

**Your code should still work when the house columns are empty.** incomplete.csv tests this.

**27 October 2013 is partial for every home.** 2 gas hours are missing that day (the clocks went back). It's a data thing, not behaviour.
