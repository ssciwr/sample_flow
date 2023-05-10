# SampleFlow website

[![CI](https://github.com/ssciwr/sample_flow/actions/workflows/ci.yml/badge.svg)](https://github.com/ssciwr/sample_flow/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ssciwr/sample_flow/branch/main/graph/badge.svg?token=Z8fyKbjrHd)](https://codecov.io/gh/ssciwr/sample_flow)
[![sonar](https://sonarcloud.io/api/project_badges/measure?project=ssciwr_sample_flow&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ssciwr_sample_flow)

The source code for the [SampleFlow website](https://circuitseq.iwr.uni-heidelberg.de/).

## Implemented features

### Users

Users of the site can

- sign up with a valid email address
- request a sample, optionally providing a reference sequence
- see a list of their requested samples
- download their reference sequences
- download full analysis data
- automatically receive an email with their results

### Admins

Users with admin rights can additionally

- see a list of all users
- see a list of all requested samples and results
- change the site settings
  - set which day of the week sample submission closes
  - set number of plate rows/cols
  - add/remove running options
- download a zipped tsv of requests from the current week
  - this includes the reference sequences as fasta files
- upload a zipfile with successful analysis results to be sent to the user
- upload unsuccessful analysis result status to be sent to the user

### REST API

Admins can also generate an API token,
then do all of the above programatically using
the provided REST API:

- [api_examples.ipynb](https://github.com/ssciwr/sample_flow/blob/main/notebooks/api_examples.ipynb)

## Developer info

If you want to make changes to the code, see
[README_DEV](README_DEV.md)
for instructions on how to locally build make a test deployment of the website.

## Deployment info

For information on how to deploy the website see
[README_DEPLOYMENT](README_DEPLOYMENT.md).
