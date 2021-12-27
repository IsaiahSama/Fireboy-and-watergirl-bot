#! /bin/bash

# Script used to pull and push to and from the repo

array=( $@ )
len=${#array[@]}
if [ $len -lt 2 ]; then
	echo "Needs a commit message, followed by the name of the repository"
	exit 1
fi

repo=${array[$len-1]}
msg=${array[@]:0:$len-1}

echo "The commit message is '$msg' and the repo name is '$repo'. Is this ok? y/n"
read resp

if [ $resp == 'y' ]; then
	echo "Adding all files"
	git add `pwd`/*
	echo "Commiting with the accepted commit message"
	git commit -m "$msg"
	echo "Pushing the repository to $repo"
	git push $repo Rewrite
	echo "Successful"
else
	echo "Aborting operation"
fi

