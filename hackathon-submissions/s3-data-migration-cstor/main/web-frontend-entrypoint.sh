#!/bin/sh

set -x

echo "VUE_APP_WEB_API=$VUE_APP_WEB_API" >> .env.production
echo "VUE_APP_WEB_WS=$VUE_APP_WEB_WS" >> .env.production

npm run build

cp -R /app/dist/* /var/www/webapp/frontend
