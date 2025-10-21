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

##### On another Terminal
- curl -XPOST localhost:3000/strings -H "Content-Type: application/json" -d '{"value":"Abdulquyum"}'