FROM nginx:1.23.1-alpine

RUN mkdir -p /var/www/webapp/static
RUN mkdir /var/www/webapp/frontend

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
