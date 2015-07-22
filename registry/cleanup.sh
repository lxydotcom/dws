#!/bin/sh

cd `dirname $0`

. ./env
. ./lib

cd - > /dev/null

[ -z ${1} ] && echo "Usage $0 MTIME" && exit 1

echo "Start Cleaning Work `date "+%Y-%m-%d %H:%M:%S"`"
for f in `find ${HOST_REGISTRY_DIR}/repositories/library/devtest/ -type f -name 'tag_*' -mtime ${1}`
do
    echo "Cleaning `basename $f`"
    rm -rf ${HOST_REGISTRY_DIR}/images/`cat ${f}`
    rm -r ${f}
    rm -r `dirname $f`/`basename $f | tr -d '_'`_json
done
echo "[Done] Cleaning Finished"
