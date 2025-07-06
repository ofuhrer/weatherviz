"""Utilities to download MeteoSwiss STAC data and save it as PNG."""

import logging
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from meteodatalab import ogd_api

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def fetch_variable(
    collection: str,
    variable: str,
    ref_time: str,
    horizon: str,
    perturbed: bool,
) -> "xarray.DataArray":
    """Retrieve a forecast field as an ``xarray.DataArray``."""

    request = ogd_api.Request(
        collection=ogd_api.Collection(collection),
        variable=variable,
        reference_datetime=ref_time,
        perturbed=perturbed,
        horizon=horizon,
    )
    return ogd_api.get_from_ogd(request)


def array_to_png(data: np.ndarray, output_path: Path) -> None:
    """Save a 2D NumPy array as an 8-bit grayscale PNG."""

    logger.info("Saving PNG to %s", output_path)
    data_min = np.nanmin(data)
    data_max = np.nanmax(data)
    if data_max == data_min:
        scaled = np.zeros_like(data, dtype=np.uint8)
    else:
        scaled = 255 * (data - data_min) / (data_max - data_min)
    img = Image.fromarray(scaled.astype(np.uint8))
    img.save(output_path)


def variable_to_png(
    collection: str,
    variable: str,
    ref_time: str,
    horizon: str,
    perturbed: bool,
    output_path: str,
) -> None:
    """Download a forecast field and save it as a PNG image."""

    da = fetch_variable(collection, variable, ref_time, horizon, perturbed)
    array_to_png(da.values.squeeze(), Path(output_path))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Download an OGD forecast variable and save it as a PNG"
    )
    parser.add_argument(
        "collection",
        help="STAC collection ID, e.g. ch.meteoschweiz.ogd-forecasting-icon-ch2",
    )
    parser.add_argument("variable", help="Variable short name, e.g. T or U_10M")
    parser.add_argument(
        "--ref-time",
        default="latest",
        help="Reference time (default: latest)",
    )
    parser.add_argument(
        "--horizon",
        default="P0DT0H",
        help="Forecast horizon as ISO-8601 duration",
    )
    parser.add_argument(
        "--perturbed",
        action="store_true",
        help="Retrieve ensemble member instead of deterministic field",
    )
    parser.add_argument("output", help="Output PNG path")
    args = parser.parse_args()

    variable_to_png(
        args.collection,
        args.variable,
        args.ref_time,
        args.horizon,
        args.perturbed,
        args.output,
    )
