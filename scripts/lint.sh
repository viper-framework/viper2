#!/bin/sh -e

export SOURCE="viper2"

export PREFIX=""
if [ -d 'venv' ] ; then
    export PREFIX="venv/bin/"
fi

set -x

${PREFIX}autoflake --in-place --recursive --exclude venv ${SOURCE}
${PREFIX}isort --profile black ${SOURCE}
${PREFIX}black --exclude venv ${SOURCE}
${PREFIX}pylint --rcfile=setup.cfg ${SOURCE}
