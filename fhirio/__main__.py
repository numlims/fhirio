# automatically generated, DON'T EDIT. please edit main.ct from where this file stems.
import argparse
import versionflag
import sys
def main():
    """
     main adds a version flag.
    """
    parser = argparse.ArgumentParser(description="read and write fhir resources.")
    versionflag.flag(parser, "fhirio")
    args = parser.parse_args()
sys.exit(main())
