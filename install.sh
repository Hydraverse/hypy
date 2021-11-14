#!/usr/bin/bash -e

# shellcheck disable=SC2016
d=$(dirname "$(readlink -f '$0')")

cd "$d";

pip install .;
