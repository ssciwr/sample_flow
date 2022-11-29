# CircuitSEQ website prototype

[![CI](https://github.com/ssciwr/circuit_seq/actions/workflows/ci.yml/badge.svg)](https://github.com/ssciwr/circuit_seq/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ssciwr/circuit_seq/branch/main/graph/badge.svg?token=Z8fyKbjrHd)](https://codecov.io/gh/ssciwr/circuit_seq)

A work-in-progress prototype of the CircuitSEQ website.

## Try it out online

It is now running on a heiCLOUD VM here: https://circuitseq.iwr.uni-heidelberg.de/

You can sign up for a user account using any valid heidelberg/embl/dkfz email address.

## Implemented features

- Users can
  - sign up with a valid email address
  - request a sample, optionally providing a reference sequence
  - see a list of their requested samples
  - download their reference sequences
  - download their results
- Admins can
  - see a list of all users
  - see a list of all requested samples
  - change the site settings
    - set which day of the week sample submission closes
    - set number of plate rows/cols
    - add/remove running options
  - download a zipped tsv of this weeks requests including reference sequences as fasta files
  - also do all of the above using a REST API

## Notes

- currently all uploaded samples and registered users may be deleted without warning as the prototype is updated!

## Developer info

If you want to make changes to the code, see [README_DEV.md](README_DEV.md) for instructions on how to locally build and deploy the website.
