#!/bin/bash
trap 'rm -f $tmp' EXIT
tmp=$(mktemp)

echo
echo "Compiling templates .."
pwd=$(pwd)
cd ..
python -m mutemplate compile -o $pwd/templates.py examples
cd $pwd

echo
echo "Running tests .."
# NOTE assumes that python and micropython are in your PATH
for p in python micropython; do
	echo
	echo "Testing $p .."
	$p test_main.py > $tmp
	if diff $tmp test_main.out; then
		echo ".. $p test passed"
	else
		echo ".. $p test FAILED" >&2
	fi
done
