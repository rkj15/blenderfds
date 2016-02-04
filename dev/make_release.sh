#!/bin/bash

version=v4.0.1
echo "Making BlenderFDS version $version release..."

short_version=${version:1}

if wget https://github.com/firetools/blenderfds/archive/$version.zip
then
    echo "Version $version downloaded!"
else
    echo "Cannot download version $version"
    exit 1
fi

unzip $version.zip
rm -rf $version.zip
mv blenderfds-$short_version BlenderFDS-$version

cd BlenderFDS-$version
zip -r blenderfds.zip zzz_blenderfds
rm -rf zzz_blenderfds dev .gitignore

cd ..
zip -r BlenderFDS-$version.zip BlenderFDS-$version
rm -rf BlenderFDS-$version
mv BlenderFDS-$version.zip ~/

echo
echo "Release BlenderFDS-$version.zip is ready!"

