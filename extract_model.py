"""
    EgoSoft X-Game File Converter | RPINerd, 09/06/25

    Description for program
"""

import argparse
import logging
import sys
from pathlib import Path

import pyconverter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """"""
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "-iac",
        dest="action",
        action="store_const",
        const="iac",
        help="Import animation format"
    )
    action.add_argument(
        "-eac",
        dest="action",
        action="store_const",
        const="eac",
        help="Export animation format"
    )
    action.add_argument(
        "-imf",
        dest="action",
        action="store_const",
        const="imf",
        help="Import mesh format"
    )
    action.add_argument(
        "-emf",
        dest="action",
        action="store_const",
        const="emf",
        help="Export mesh format"
    )

    parser.add_argument("file", type=Path, required=True, help="File to process")

    parser.add_argument("data", type=Path, required=True, help="Extracted game data folder")

    parser.add_argument("-o", "--output", type=Path, required=False, help="Path to the output folder, if desired")

    parser.add_argument("-v", "--verbose", type=bool, action="store_true", help="Verbose output")

    return parser.parse_args()


def main(action: str, game_data: Path, input_file: Path, output_dir: Path) -> None:
    """Main entry point for the script."""
    if action == "iac":
        logger.debug("Action 'iac' selected")
        pyconverter.convert_dae_to_xac(game_data, input_file, output_dir / (input_file.stem + ".xac"))
    elif action == "eac":
        logger.debug("Action 'eac' selected")
        pyconverter.convert_xac_to_dae(game_data, input_file, output_dir / (input_file.stem + ".dae"))
    elif action == "imf":
        logger.debug("Action 'imf' selected")
        pyconverter.convert_dae_to_xml(game_data, input_file, output_dir / (input_file.stem + ".xml"))
    elif action == "emf":
        logger.debug("Action 'emf' selected")
        pyconverter.convert_xml_to_dae(game_data, input_file, output_dir / (input_file.stem + ".dae"))
        logger.warning("This feature is not yet implemented.")
    else:
        logger.error(f"Unknown action {action} specified. This shouldn't be possible??")
        sys.exit(1)


if __name__ == "__main__":
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if not args.data.exists():
        logger.error("The specified game data folder does not exist.")
        sys.exit(1)
    if not args.data.is_dir():
        logger.error("The specified game data folder is not a directory.")
        sys.exit(1)
    if not args.file.exists():
        logger.error("The specified input file does not exist.")
        sys.exit(1)
    if not args.file.is_file():
        logger.error("The specified input file is not a regular file.")
        sys.exit(1)

    output_dir = None
    if args.output:
        output_dir = args.output
        if not output_dir.exists():
            logger.info("The specified output folder does not exist, creating it...")
            output_dir.mkdir(parents=True)
        if not output_dir.is_dir():
            logger.error("The specified output folder is not a directory.")
            sys.exit(1)
    else:
        output_dir = args.file.parent

    main(args.action, args.data, args.file, output_dir)
