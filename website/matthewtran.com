server {
    listen 80;
    listen [::]:80;

    server_name matthewtran.com www.matthewtran.com;

    root /var/www/matthewtran.com/html;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
