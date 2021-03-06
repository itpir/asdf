#!/bin/bash

# compares head commit hash of local repo with remote repo

# source
# https://github.com/chrissimpkins/scriptacular/blob/master/version-control/gitupdate.sh
# http://sweetme.at/2013/10/08/keep-a-local-git-repository-synchronized-with-a-remote-git-repository/

# Scriptacular - gitupdate.sh
# Compare SHA-1 between local and remote repositories, git pull + FF merge in local if they differ
# Copyright 2013 Christopher Simpkins
# MIT License

# Default to working directory
# LOCAL_REPO="."

# Default to git pull with FF merge in quiet mode
# GIT_COMMAND="git pull --quiet"

# User messages
GU_ERROR_FETCH_FAIL="Unable to fetch the remote repository."
GU_ERROR_UPDATE_FAIL="Unable to update the local repository."
GU_ERROR_NO_GIT="This directory has not been initialized with Git."
GU_INFO_REPOS_EQUAL="The local repository is current. No update is needed."
GU_SUCCESS_REPORT="Update complete."


LOCAL_REPO="$1"
cd "$LOCAL_REPO"

branch="$2"

if [ -d ".git" ]; then
    # update remote tracking branch
    git remote update >&-
    if (( $? )); then
        echo $GU_ERROR_FETCH_FAIL >&2
        exit 1
    else
        if [[ ! $(git branch | grep "$branch") ]]; then
            echo 'branch ('"$branch"') does not exist. using master.'
            branch=master
        fi

        LOCAL_SHA=$(git rev-parse --verify HEAD)
        REMOTE_SHA=$(git rev-parse --verify origin/"$branch")

        if [ $LOCAL_SHA = $REMOTE_SHA ]; then
            echo $GU_INFO_REPOS_EQUAL
            exit 0
        else

            # $GIT_COMMAND
            git fetch
            git reset --hard origin/"$branch"
            git clean -f -d
            git pull --all

            if (( $? )); then
                echo $GU_ERROR_UPDATE_FAIL >&2
                exit 1
            else
                echo $GU_SUCCESS_REPORT
            fi
        fi
    fi
else
    echo $GU_ERROR_NO_GIT >&2
    exit 1
fi
exit 0
