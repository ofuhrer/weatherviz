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
    """Save a 2D NumPy array as an 8-bit grayscale PNG with transparency for NaN values."""
    logger.info("Saving PNG to %s", output_path)

    # Create an alpha channel where NaN values are transparent
    alpha_channel = np.where(np.isnan(data), 0, 255).astype(np.uint8)

    # Replace NaN values with the minimum value in the array for scaling
    if np.isnan(data).any():
        logger.warning("Array contains NaN values. Replacing NaNs with the minimum value for scaling.")
        data = np.nan_to_num(data, nan=np.nanmin(data))

    # Compute the minimum and maximum values
    data_min = np.min(data)
    data_max = np.max(data)

    # Handle the case where all values are the same
    if data_max == data_min:
        logger.warning("Array has constant values. Generating a blank image.")
        grayscale = np.zeros_like(data, dtype=np.uint8)
    else:
        # Scale the data to the range [0, 255]
        grayscale = 255 * (data - data_min) / (data_max - data_min)

    # Ensure the data type is uint8
    grayscale = grayscale.astype(np.uint8)

    # Combine the grayscale data with the alpha channel to create an RGBA image
    rgba_image = np.dstack((grayscale, grayscale, grayscale, alpha_channel))

    # Save the array as a PNG
    img = Image.fromarray(rgba_image)
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
        help="STAC collection ID, e.g. ogd-forecasting-icon-ch2",
    )
    parser.add_argument("variable", help="Variable short name, e.g. T_2M or U_10M")
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
