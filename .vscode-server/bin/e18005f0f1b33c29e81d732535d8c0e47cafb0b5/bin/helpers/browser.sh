#!/usr/bin/env sh
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
ROOT=$(dirname "$(dirname "$(dirname "$0")")")

APP_NAME="code"
VERSION="1.66.0"
COMMIT="e18005f0f1b33c29e81d732535d8c0e47cafb0b5"
EXEC_NAME="code"
CLI_SCRIPT="$ROOT/out/server-cli.js"
"$ROOT/node" "$CLI_SCRIPT" "$APP_NAME" "$VERSION" "$COMMIT" "$EXEC_NAME" "--openExternal" "$@"
