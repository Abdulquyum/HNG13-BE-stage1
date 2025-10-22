HNG Internship cohort 13 stage 1 project repository to build a standard string analyzer

### Create a Virtual enviroment
-  python3 -m venv hng-venv
- source hng-venv/Scripts/activate

### Installation
- pip3 install flask
- 

### Run code locally
- cd string-Analyzer
- chmod +x app.py
- ./app.py

##### On another Terminal POST REQUEST
- curl -XPOST localhost:3000/strings -H "Content-Type: application/json" -d '{"value":"Abdulquyum"}'

##### On another terminal GET REQUEST, get all strings from the dict
- curl -XGET localhost:300/strings

##### On another terminal GET REQUEST, get a specific string from the dict
- curl -XGET localhost:300/strings/Abdulquyum

##### On another terminal GET REQUEST, get some specific with filter
- curl -XGET "localhost:3000/strings?is_palindrome=false&min_length=5&max_length=20&word_count=1&contains_character=o"

##### Natural filter
curl -XGET "localhost:3000/strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings"

##### DELETE ENDPOINT
curl -XDELETE "localhost:3000/strings/your_string_value"


### DEPLOYMENT ON AWS EC2 Instance SERVER
- sudo apt update -y
- sudo apt upgrade -y
- sudo apt install nginx -y
- sudo systemctl enable nginx
- sudo systemctl start nginx
- git clone https://github.com/Abdulquyum/HNG13-BE-stage1.git
- sudo apt install python3
- sudo apt install pip -y
- sudo apt install python3-flask
- sudo apt install gunicorn

## Create systemd service
sudo cat > /etc/systemd/system/flask-app.service << EOF
[Unit]
Description=Flask Profile App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/HNG13-BE-stage1/string-Analyzer
ExecStart=/usr/bin/gunicorn --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

- sudo rm -f /etc/nginx/sites-enabled/default

## Configure Nginx
sudo cat > /etc/nginx/sites-available/flask-app << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/flask-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Start Flask app
sudo systemctl daemon-reload
sudo systemctl enable flask-app
sudo systemctl start flask-app