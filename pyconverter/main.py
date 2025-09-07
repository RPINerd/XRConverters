""""""

import logging
from pathlib import Path

import pygltflib

logger = logging.getLogger()


def convert_xml_to_dae(game_data: Path, input_file: Path, output_file: Path) -> None:
    """Convert an XML file to DAE format."""
    logger.info(f"Converting {input_file} to {output_file}...")
    obj = pygltflib.GLTF2().load(str(input_file))
    if obj is None:
        logger.error(f"Failed to load GLTF from {input_file}")
        return
    obj.save_json(str(output_file))


def convert_dae_to_xml(game_data: Path, input_file: Path, output_file: Path) -> None:
    """Convert a DAE file to XML format."""
    logger.info(f"Converting {input_file} to {output_file}...")
    # TODO: Implement conversion logic
    logger.warning("This feature is not yet implemented.")


def convert_xac_to_dae(game_data: Path, input_file: Path, output_file: Path) -> None:
    """Convert a XAC file to DAE format."""
    logger.info(f"Converting {input_file} to {output_file}...")
    # TODO: Implement conversion logic
    logger.warning("This feature is not yet implemented.")


def convert_dae_to_xac(game_data: Path, input_file: Path, output_file: Path) -> None:
    """Convert a DAE file to XAC format."""
    logger.info(f"Converting {input_file} to {output_file}...")
    # TODO: Implement conversion logic
    logger.warning("This feature is not yet implemented.")
