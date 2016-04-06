#!/bin/bash
# Make BlenderFDS release <http://blenderfds.org/>.
# Copyright (C) 2016 Emanuele Gissi

# Setup

tag="v4.0.7"
short_tag=${tag:1}
release_name="BlenderFDS-$tag"

github_url="https://github.com/firetools/blenderfds/archive"
github_file="$tag.zip"
github_unzip_dir="blenderfds-$short_tag"

git_local="/home/egissi/Documenti/Argomenti/BlenderFDS/git"

destination_path="/home/egissi/Documenti/Argomenti/BlenderFDS/BlenderFDS_releases"

# Main

source colors.sh
echo_title "Making <$release_name> release..."

# Run tests

#echo_msg "Running auto-tests..."
#if (
#    python3 ./make_test.py
#); then echo_ok "Done."
#else
#    echo_err "Test error reported. Aborted."
#    exit 1
#fi

# Commit and push latest changes (gitg)

#echo_msg "Committing and pushing latest changes..."
#if (
#    gitg
#    git push
#); then echo_ok "Done."
#else
#    echo_err "Cannot commit and push. Aborted."
#    exit 1
#fi

# Write release notes

#echo_msg "Writing release notes..."
#google-chrome "https://github.com/firetools/blenderfds/wiki/Release-notes/_edit"
#echo_ok "Done."

# Tag pre-release

#git tag -a $tag -m "Release $tag"
#git push --tags

# Download from GitHub

#echo_msg "Downloading <$github_file> from GitHub..."
cd /tmp
#if wget $github_url/$github_file; then echo_ok "Done."
#else
#    echo_err "Cannot download <$github_file> from GitHub. Aborted."
#    exit 1
#fi

# Unzipping and renaming

echo_msg "Unzipping and renaming <$github_file>..."
if (
    unzip $github_file && rm -rf $github_file
    mv $github_unzip_dir $release_name
); then echo_ok "Done."
else
    echo_err "Cannot unzip <$github_file>. Aborted."
    exit 1
fi

# Preparing release

echo_msg "Preparing release <$release_name.zip> in <$destination_path>..."
if (
    cd $release_name
    zip -r blenderfds.zip zzz_blenderfds && rm -rf zzz_blenderfds
    rm -rf dev
    cd ..
    zip -r $release_name.zip $release_name && rm -rf $release_name
    mv $release_name.zip $destination_path
); then echo_ok "Done."
else
    echo_err "Cannot prepare release. Aborted."
    exit 1
fi

# Setup release

echo_msg "Edit release page..."
google-chrome "https://github.com/firetools/blenderfds/releases"
echo_ok "Done."

# Bump version

echo_msg "Do not forget to bump version!"

