#!/bin/sh -e

export SOURCE="viper"

export PREFIX=""
if [ -d 'venv' ] ; then
    export PREFIX="venv/bin/"
fi

set -x

${PREFIX}autoflake --in-place --recursive --exclude venv ${SOURCE}
${PREFIX}isort ${SOURCE}
${PREFIX}black --exclude venv ${SOURCE}
