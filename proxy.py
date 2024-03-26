from socket import *
from urllib.parse import urlparse
import os
import sys
import json

cache_dir = "cache"
filename_detail = "" # Store branches of index url
response_cache = "" # Store data read from cache
response_buffer = "" # Store server response


# When executing py file input IP address: 127.0.0.1
if len(sys.argv) <= 1:
    print('Usage: "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address of the Proxy Server')
    sys.exit(2)

# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)

tcpSerPort = 8888 # Bind to certain port
tcpSerSock.bind(('127.0.0.1', tcpSerPort))
tcpSerSock.listen(5) # 5: maximum number of queued connections.

while True:
    # Start receiving data from the client
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept() # Wait and Accept when connection occured
    print('Received a connection from: ', addr)

    # Decode received client's HTTP request
    message = tcpCliSock.recv(4096).decode()
    print(message)

    # Get format: GET /www.yahoo.com HTTP/1.1
    # Post format: POST http://httpbin.org/forms/post HTTP/1.0
    parts = message.split() # Split request by space

    if "GET" in message:
        if len(parts) >= 2:
            # Extract the filename from the given message
            filename = parts[1].partition("/")[2]
            filename = filename.replace("http://", "")
            print("filename: "+filename)
            if not filename.startswith('www.') and not filename.startswith('http:'): # For example: wikipedia(en.wikipedia.org/wiki/Computer_securi)
                filename_parts = filename.split('/')
                filename = filename_parts[0]
                print("filename: "+filename)
                filename_detail = filename_parts[1:]
                print("filename_detail: " + '/'.join(filename_detail))
            filetouse = "/" + filename
            print("filetouse: "+filetouse)
            
            fileExist = False

            # Prevrnting from favicon.ico mess up
            if filename == 'favicon.ico' or filetouse == 'favicon.ico':
                continue

            try:
                # Check if the file exists in the cache
                f = open(cache_dir + "/" + filetouse, "rb")
                outputdata = f.read()

                fileExist = True
                print('File Exists')

                response_cache += outputdata.decode('utf-8')
                print(response_cache)
                tcpCliSock.send(response_cache.encode()) # Send response(cache content) to client
                print('Read from cache')

                # Another way by using content type
                # content_type = ""  # Defult set empty
                # if filetouse.endswith(".jpeg") or filetouse.endswith(".jpg"):
                #     content_type = "image/jpeg"
                #     print('Content Type: image/jpeg')
                # elif filetouse.endswith(".png"):
                #     content_type = "image/png"
                #     print('Content Type: image/png')
                # elif filetouse.endswith(".html"):
                #     content_type = "text/html"
                #     print('Content Type: text/html')
                # elif filetouse.endswith(".text"):
                #     content_type = "text/plain"
                #     print('Content Type: text/plain')
                # # HTTP response
                # response = "HTTP/1.0 200 OK\r\n"
                # response += "Content-Type:" + content_type + "\r\n"
                # response += "\r\n"  

            # When file does not exist in cache
            except IOError as e: 
                print('File Exist: ', fileExist)
                if fileExist is False:
                    # Create a socket on the proxyserver
                    print('Creating socket on proxyserver')
                    c = socket(AF_INET, SOCK_STREAM)
                    hostn = filename.replace("http://", "")
                    hostn = hostn.replace("www.", "", 1)
                    print('Host Name: ', hostn)
                    print("Cache Directory:", cache_dir)
                    print("Cache File Path:", cache_dir + "\\" + filename)

                    try: # In case connect failure(wrong hostn)
                        # Connect to the socket to port 80 (address, port)
                        print(f"HOST name, {hostn}")
                        c.connect((hostn, 80)) 
                        print("connect success")
                        fileobj = c.makefile('wb', 0) # write binary mode sending request to server
                        
                        filename_detail = '/'.join(filename_detail) # filename_detail = ['wiki', 'Computer_security']
                        request = f"GET /{filename_detail} HTTP/1.1\r\nHost: {hostn}\r\nConnection: close\r\n\r\n" # {filename}
                        print(f'request={request}')

                        fileobj.write(request.encode()) # Write down the request
                        fileobj.flush()  # Immediately send data to server
        
                        # Read the response into buffer
                        fileobj = c.makefile('rb', 0) # reading response from server(1 line/time)
                        while True:
                            buffer = fileobj.readline()
                            if not buffer: # When no contents haven't been read in buffer = '' or None
                                break
                            response_buffer += buffer.decode()

                        # HTTP response message for file not found
                        if '404' in response_buffer:
                            not_found_response = "HTTP/1.1 404 Not Found\r\n"
                            not_found_response += "Content-Type: text/html\r\n\r\n"
                            not_found_response += "<html><body><h1>404 Not Found</h1></body></html>"
                            tcpCliSock.send(not_found_response.encode())
                            tcpCliSock.close()
                            print('File not found')
                        else:
                            tmpFile = open(cache_dir + "/" + filename, "wb") # Create a new file in the cache of requested content
                            tmpFile.write(response_buffer.encode())
                            tmpFile.close()
                            print("Saved Successfully")
                            tcpCliSock.send(response_buffer.encode()) # Send the response to the client socket
                            print(response_buffer.encode())
                    except Exception as e:
                        print("Illegal Request in get", e)
                        
    elif "POST" in message:
        url = parts[1]

        # Parse the URL to extract the hostname and path
        parsed_url = urlparse(url)
        
        # Extract the hostname and path
        hostn = parsed_url.netloc
        hostn = hostn.replace("https://", "")
        hostn = hostn.replace("www.", "", 1)
        filename_detail = parsed_url.path
        print(f'hostn: {hostn}')
        print(f'filename_detail: {filename_detail}')

        response_data = {
        "status": "POST Success",
        "data": '456'  # Include your JSON data here
        }

        json_string = json.dumps(response_data) # Covert json to string
        content_length = len(json_string)
        content_type = "application/json" # Default type for post
        try: # In case connect failure(wrong hostn)
            c = socket(AF_INET, SOCK_STREAM)
            c.connect((hostn, 80))

            fileobj = c.makefile('wb', 0)

            request = f"POST {filename_detail} HTTP/1.1\r\nHost: {hostn}\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\nConnection: close\r\n\r\n{json_string}"

            fileobj.write(request.encode()) # Write down the request
            fileobj.flush() # Immediately send data to server
            fileobj = c.makefile('rb', 0) # reading response from server(1 line/time)

            while True:
                buffer = fileobj.readline()
                if not buffer: # When no contents haven't been read in buffer = '' or None
                    break
                response_buffer += buffer.decode()
            tcpCliSock.send(response_buffer.encode()) # Send server response, post data to client
            print(response_buffer.encode())

            if '200 OK' in response_buffer: 
                # if success
                success_response = f"The data {json_string} has successfully post!"
                print(success_response.encode())
        except Exception as e:
                print("Illegal Request in post", e)
        c.close() # Close the connection

    # else:
    #     # Wrong request method or url
    #     error_response = "HTTP/1.1 400 Bad Request\r\n"
    #     error_response += "Content-Type: text/html\r\n\r\n"
    #     error_response += "<html><body><h1>400 Bad Request</h1></body></html>"
    #     tcpCliSock.send(error_response.encode())
    #     tcpCliSock.close()
    #     print("Illegal Request")

    # Close the socket and the server sockets
    tcpCliSock.close()