# copy fastapi.service to /etc/systemd/system
sudo cp ./fastapi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi

# copy fastapi.conf to /etc/nginx/sites-available
sudo cp ./fastapi.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/fastapi.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# install certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d shapez2-tools.com
sudo certbot renew --dry-run