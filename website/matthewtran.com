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

server {
    listen 80;
    listen [::]:80;

    server_name git.matthewtran.com;

    location / {
        client_max_body_size 512M;
        proxy_pass http://gitea:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
