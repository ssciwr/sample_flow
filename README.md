# CircuitSEQ website prototype

[![CI](https://github.com/ssciwr/circuit_seq/actions/workflows/ci.yml/badge.svg)](https://github.com/ssciwr/circuit_seq/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ssciwr/circuit_seq/branch/main/graph/badge.svg?token=Z8fyKbjrHd)](https://codecov.io/gh/ssciwr/circuit_seq)

A work-in-progress prototype of the CircuitSEQ website.

## Try it out online

It is now running on a heiCLOUD VM here: http://129.206.7.129/

### Testing accounts

There are currently two built-in accounts for testing purposes:

- admin account
  - email: `admin@embl.de`
  - password: `admin`
- user account
  - email: `user@embl.de`
  - password: `user`

You can also signup for a new account on the site (there is not yet an email account activation step, you can login straightaway after signup)

### Implemented features

- Users can
  - sign up with a valid email address
  - request a sample, optionally providing a fasta reference sequence
  - see a list of their requested samples & download the reference sequences
- Admins can
  - see a list of all requested samples & download reference sequences
  - see a list of all users

### Notes

- all uploaded samples and registered users will be deleted without warning as the prototype is updated!

## Developer info

If you want to make changes to the code, see [README_DEV.md](README_DEV.md) for instructions on how to locally build and deploy the website.
