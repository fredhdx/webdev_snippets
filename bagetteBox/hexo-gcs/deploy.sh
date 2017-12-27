#!/bin/bash
# a script to deploy hexo site online
# use _config.yml combined with deploy key to build sites
# make sure _config.yml is up-to-date
# recommened usage:
#     cat _config.yml ../key-PLACE.txt > source/_data/next.yml
#     hexo generate/deploy --config source/_data/next.yml

opt=$1
url_line="15s" # append number with s for sed replace command
default_url="www.mumu.coffee"
githome_url="fredhdx.github.io"


if [ "$opt" == "gcp" ]; then
    # back up config file
    cp source/_data/next.yml source/_data/next.bk
    # make sure the url is correct for gcp
    sed -i -e "$url_line/.*/url: $default_url/g" _config.yml 
    # renew config file
    cp _config.yml source/_data/next.yml

    hexo generate --config source/_data/next.yml

    cd public/
    gsutil -m rsync -d -r . gs://$default_url
    cd ..

elif [ "$opt" == "git" ]; then
    # back up config file
    cp source/_data/next.yml source/_data/next.bk
    # use githome url
    sed -i -e "$url_line/.*/url: $githome_url/g" _config.yml
    # renew config file
    cat _config.yml ../key-home.txt > source/_data/next.yml

    hexo generate --config source/_data/next.yml
    hexo deploy --config source/_data/next.yml

    # reset url to default gcp value
    sed -i -e "$url_line/.*/url: $default_url/g" _config.yml
else
    echo "invalid argument. specify: git or gcp"
fi
