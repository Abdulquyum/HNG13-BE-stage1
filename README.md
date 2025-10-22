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

### Natural filter
curl -XGET "localhost:3000/strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings"