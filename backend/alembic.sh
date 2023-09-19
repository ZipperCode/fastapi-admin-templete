#!/bin/bash

msg=$1
echo "commit msg = ${msg}"
echo "exec autogenerate"
if [ -z "${msg}"];then
  alembic revision --autogenerate
else
  alembic revision --autogenerate -m "${msg}"
fi;

echo "exec upgrade"
alembic upgrade head
