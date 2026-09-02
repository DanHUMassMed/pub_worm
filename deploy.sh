#!/bin/bash
set -e

VERSION_FILE="pub_worm/__init__.py"

# Get current version
VERSION=$(grep "__version__" $VERSION_FILE | cut -d'"' -f2)

IFS='.' read -r -a PARTS <<< "$VERSION"
MAJOR=${PARTS[0]}
MINOR=${PARTS[1]}
PATCH=${PARTS[2]}

# Increment patch
NEW_VERSION="$MAJOR.$MINOR.$((PATCH + 1))"

echo "Bumping version: $VERSION → $NEW_VERSION"

# Update __init__.py
sed -i '' "s/__version__ = .*/__version__ = \"$NEW_VERSION\"/" "$VERSION_FILE"

# Clean previous build artifacts
rm -rf ./dist ./pub_worm.egg-info

# Build distributions with uv
echo "Building distribution packages with uv..."
uv build

# Upload to PyPI using PYPI_API_TOKEN environment variable
if [ -z "$PYPI_API_TOKEN" ]; then
    echo "Error: PYPI_API_TOKEN environment variable is not set." >&2
    exit 1
fi

echo "Uploading to PyPI with uv publish..."
uv publish --token "$PYPI_API_TOKEN"

# Only if upload succeeds, commit and tag git
echo "Committing and tagging git release..."
git add "$VERSION_FILE" pyproject.toml
git commit -m "Bump version to $NEW_VERSION"
git tag "v$NEW_VERSION"
git push
git push --tags

echo "Successfully deployed v$NEW_VERSION to PyPI and GitHub!"