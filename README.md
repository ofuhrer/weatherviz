# WeatherViz

This is a private, experimental project aimed at visualizing MeteoSwiss open weather model data. The viewer uses Leaflet to display these data on top of SwissTopo maps by default, while allowing alternative background layers to be selected.

The project now includes a lightweight backend script that uses the
`meteodata-lab` library to download forecast fields from the MeteoSwiss STAC
catalog and convert them into simple PNG images for display in the Leaflet
frontend.

## Usage

1. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Convert a forecast field to PNG:
   ```bash
   python backend/stac_converter.py \
       ch.meteoschweiz.ogd-forecasting-icon-ch2 T \
       --ref-time latest --horizon P0DT0H \
       output.png
   ```
   Adjust the collection ID, variable, reference time and horizon as needed.
   The script retrieves the data via `meteodata-lab`, rescales it to 8‑bit and
   writes `output.png`.

Open `index.html` in a web browser to see the map.
