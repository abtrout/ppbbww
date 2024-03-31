#!/usr/bin/env bash

# https://github.com/jekyll/jekyll/issues/9066#issuecomment-1422379047
VERSION="4.2.0"

docker run --rm \
  --volume="$PWD:/srv/jekyll" \
  -p 8080:4000 \
  -it jekyll/jekyll:$VERSION \
  jekyll serve --incremental --watch --drafts
