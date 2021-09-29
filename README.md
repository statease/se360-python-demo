# Stat-Ease 360 and Python demo

This is a collection of a few Python programs that interact with Stat-Ease 360,
initially demonstrated at the 2021 DOE Summit by Hank Anderson. The slides
from that talk are included in this repository as well.

## Multi-response Graph

This uses the `examples\multiresponse-graph.py` script. Open Stat-Ease 360 and
load this script from the Script Window, then click File -> Run.

It will retrieve the two Analysis objects from SE360 and make predictions for
both of them while varying the A factor. These predictions are plotted on the
same Matplotlib plot.

## Streamflow

This example uses the `examples\streamflow.py` script.

It demonstrates fetching data from a cloud API and inserting it into
Stat-Ease 360. It has a flag in the script to toggle between live data and
a csv file.

The data retrieval and manipulation code are in `se360demo\__init__.py`.
To use the live data you'll need to set an environment variable called
`NOAA_TOKEN` with a token generated from https://www.ncdc.noaa.gov/cdo-web/token.
