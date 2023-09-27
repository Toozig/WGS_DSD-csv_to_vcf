# CSV to VCF Converter

## Overview

The **CSV to VCF Converter** is a Python script designed to transform CSV (Comma-Separated Values) files into VCF (Variant Call Format) files. This tool is particularly useful for users who have generated CSV files as output from Roni's pipeline and need to convert them into VCF format for further analysis or integration with other bioinformatics tools.

## Prerequisites

Before using this script, ensure that you have the following Python modules imported and installed:

- `sys` (System-specific parameters and functions)
- `pandas` (Data manipulation and analysis library)
- `datetime` (Date and time handling)
- `concurrent.futures` (High-level interface for asynchronously executing functions)
- `pandarallel` (Parallel processing for Pandas DataFrames)

You can install the required Python packages using `pip`:

```bash
pip install pandas pandarallel
```

## Usage

To use the **CSV to VCF Converter**, follow the provided usage instructions:

```bash
csv_to_vcf.sh <csv_file> <col_info_file> <output_file>
```

- `csv_file`: The input CSV file containing your data. This should be the output of Roni's pipeline.

- `cols_info_file`: A file specifying column information needed for the VCF conversion. can be found in the git as well

- `output_file_name`: The name of the output VCF file where the converted data will be saved.

### Output

The following output files will be generated:

1. `<output_file>.gz`: The VCF file in compressed format.

2. `<output_file>.gz.tbi`: The index file for the VCF. This file is necessary to view the VCF data in an IGV (Integrative Genomics Viewer) browser.

## License

This script is provided under the [MIT License](LICENSE). Feel free to modify and distribute it as needed, but please retain the original license text.

## Contact

If you have any questions, suggestions, or encounter any issues with the **CSV to VCF Converter**, please feel free to contact the author at [ido.blass@mail.huji.ac.il].

**Happy converting!**