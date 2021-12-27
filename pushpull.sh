#! /bin/bash

# Script used to pull and push to and from the repo

array=( $@ )
len=${#array[@]}
if [ $len != 1 ]; then
	echo "Needs exactly one argument, which is the name of the repository"
	exit 1
fi

git push $!
git pull $1 Rewrite
