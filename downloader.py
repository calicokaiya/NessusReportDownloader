import requests
import time
import json

# Uncomment these two lines if you want to disable annoying TLS error messages
#import urllib3
#urllib3.disable_warnings()

# HOW DOES THIS WORK?
# In order to download a report, the browser frontend send 3 requests
# POST /scans/SCANID/export?limit=2500 HTTP/1.1 gives us a file token
# GET /tokens/FILETOKEN/status HTTP/1.1 gives us the status of the file (ready/existent/not)
# GET /tokens/FILETOKEN/download HTTP/1.1 downloads the file if it is ready
# We can probably get by without verifying the validity of the file
# Sends a login request and returns the authentication token



# Will read from file config/connection.conf and get the Nessus URL
# from nessusURL field
def getNessusURL():
    url = None
    with open("config/connection.conf") as file:
        lines = [line.rstrip() for line in file]
    for line in lines:
        line = line.split(" ")
        # Gets the URL
        if "URL" in line[0].upper():
            url = line[-1]
            # Removes slashes at the end (usually there's only 1 slash
            # but we lose nothing in using a while over an if)
            while url[-1] == "/":
                url = url[:-1]
    return url


# Reads and loads the login credentials from config/connection.conf 
def getLoginCredentials():
    username = None
    password = None
    with open("config/connection.conf") as file:
        lines = [line.rstrip() for line in file]
    for line in lines:
        line = line.split(" ")
        # Gets the username
        if "USERNAME" in line[0].upper():
            username = line[-1]
        if "PASSWORD" in line[0].upper():
            password = line[-1]
    
    if username == None or password == None:
        print("Username or password is None.")
    else:
        data = {
            "username":username,
            "password":password
        }
        return data
    return None


# Sends a login request and returns the session token
def login(loginData):
    # Request data
    url = urlRoot + "/session"
    try:
        # Sends request
        x = requests.post(url, data = loginData, verify = False)
        # Gets login token from response
        token = x.json()["token"]
        return token
    except Exception as e:
        print("An error occurred: " + str(e))
        return None



# Checks the status of the report and return true if it is ready.
def reportStatus(loginToken, reportToken):
    # Request data
    url = urlRoot + "/tokens/" + reportToken + "/status"
    headers = {"X-Cookie": "token=" + loginToken}

    # Sends request
    x = requests.get(url, headers = headers, verify = False)
    # Gets report status from response
    status = x.json()["status"]

    # Only return true if it's ready
    if status == "ready":
        return True
    
    return False


# Will download a report when given a file token
def downloadReport(loginToken, reportToken):
    # Request data
    url = urlRoot + "/tokens/" + reportToken + "/download"
    headers = {"X-Cookie": "token=" + loginToken}
    

    # Sends report and gets intended filename
    x = requests.get(url, headers = headers, verify = False)
    filename = x.headers["Content-Disposition"]
    filename = filename[22:-1]
    
    # Saves report info to file
    open("./output/" + filename, "wb").write(x.content)
    print("Wrote data to " + filename)


# Gets the name of the report through an ID
def getReportName(loginToken, scanId):
    # Request data
    url = urlRoot + "/scans/" + str(scanId) + "?limit=2500&"
    headers = {"X-Cookie": "token=" + loginToken}

    # Sends request and filters the output
    response = requests.get(url, headers = headers, verify = False)
    name = response.json()["info"]["name"]
    return name


# Gets report file token, so we can download the file in the future
# Returns None if there is an error, otherwise returns the file token
def getReportToken(loginToken, scanId):
    # Request data
    url = urlRoot + "/scans/" + str(scanId) + "/export?limit=2500"
    headers = {"X-Cookie": "token=" + loginToken}

    # We use the json file "report_query.json" to control how the csv should be formatted.
    with open("./config/report_query.json") as json_file:
        data = json.load(json_file)
 
    # Makes the request and filters result
    try:
        x = requests.post(url, headers = headers, json = data, verify = False)
        fileToken = x.json()["token"]
        #print("fileToken: " + str(fileToken))
    except KeyError as e:
        name = getReportName(loginToken, scanId)
        print("Caught error for " + name + ": " + str(x.json()))
        fileToken = None
    return fileToken


# Gets the list of scans to download reports from config/scanlist.dat
def getScanList():
    scanList = []
    with open("config/scanlist.dat") as scanlist:
        for line in scanlist:
            line = line.rstrip()
            line = line.split(" ")[0]
            scanList.append(line)
    return scanList


# Start by getting connection info
urlRoot = getNessusURL()
if urlRoot == None:
    print("Expected a URL, but instead got None.")
else:
    print("Loaded URL: " + urlRoot)
