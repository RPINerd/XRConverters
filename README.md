# XRConverters

Primary function at this moment is a public archive of these extraction tools and source code since the original dropbox link is no longer available.

Possible upgrade/reimplementation of the extraction tools is being considered.

## Installation

Not yet implemented.

## Planned Usage

```sh
python xrconverters.convert --input path/to/ship_01.xml --output path/to/ship_01.dae
```

## Proposed Project Structure

```text
xrconverters/
├── __init__.py
├── convert.py
├── utils.py
├── formats/
│   ├── __init__.py
│   ├── format_a.py
│   └── format_b.py
tests/
├── test_convert.py
├── test_utils.py
README.md
requirements.txt
```

## Contributing

Contributions are welcome! Please ensure code follows the repository's style guidelines and includes appropriate documentation and tests.

## License

Licence files can be found in the respective directory.

## Contact

For questions or support, please open an issue on GitHub.
