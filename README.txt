Please create a folder named "cache" on the same layer as proxy.py.
Run the program by input 'python proxy.py 127.0.0.1:8080' in terminal.
GET:
1. Open browser input '127.0.0.1:8080/www.yahoo.com' to GET index page or '127.0.0.1:8080/en.wikipedia.org/wiki/Computer_security' to GET arbitrary pag.
2. When first time open the website, terminal will display "Saved Successfully". The new created file under cache is the website's url.
3. When open the website for more than one time, terminal will display "Read from cache". Get all the website information from cache.
4. While running the code, the buffer information get from server response will be printed in the terminal.

POST:
1. Post json content is 
response_data = {
    "status": "POST Success",
    "data": '456'  # Include your JSON data here
}
2. When testing, open terminal and enter 'curl -v -X POST -x 127.0.0.1:8080 httpbin.org/anything'. It will display the detailed information of the website. Also, in the json column, you can see the post data send back to client.
