#!/bin/bash
# Make BlenderFDS release <http://blenderfds.org/>.
# Copyright (C) 2016 Emanuele Gissi

# Setup

tag="v4.0.4"
short_tag=${tag:1}
release_name="BlenderFDS-$tag"

github_url="https://github.com/firetools/blenderfds/archive"
github_file="blenderfds-$short_tag.zip"
github_unzip_dir="blenderfds-$short_tag"

git_local="/home/egissi/Documenti/Argomenti/BlenderFDS/git"

destination_path="/home/egissi/Documenti/Argomenti/BlenderFDS/BlenderFDS_releases"

# Main

source colors.sh
echo_title "Making <$release_name> release..."

# Download from GitHub

#echo_msg "Downloading <$github_file> from GitHub..."
#cd /tmp
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
    rm -rf dev .gitignore
    cd ..
    zip -r $release_name.zip $release_name && rm -rf $release_name
    mv $release_name.zip $destination_path
); then echo_ok "Done."
else
    echo_err "Cannot prepare release. Aborted."
    exit 1
fi
