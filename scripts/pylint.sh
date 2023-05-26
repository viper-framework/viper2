#!/bin/sh -e

export SOURCE="viper2"

export PREFIX=""
if [ -d 'venv' ] ; then
    export PREFIX="venv/bin/"
fi

set -x

${PREFIX}pylint --rcfile=setup.cfg ${SOURCE}
