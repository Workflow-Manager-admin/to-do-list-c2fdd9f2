#!/bin/bash
cd /home/kavia/workspace/code-generation/to-do-list-c2fdd9f2/BackendAPIServer
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

