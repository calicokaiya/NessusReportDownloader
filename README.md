# Documentation Structure
This file contains all the information one might need about the usage of this program. It is divided for your convenience as so:
  - Using the program
    - General function
    - Dependencies
    - Usage
    - Configuration
      - Setting up connection info
      - Setting up login info
      - Setting up list of scans
      - Changing report format
  - Understanding the program
    - Program structure
    - Detailed function of downloader.py
    - Detailed function of file_handler.py
    - NESSUS requests
      - Logging in
      - Creating a report
      - Validating a report
      - Downloading a report
  - Contributing
  - Licensing


# Using the program
## General function
This program downloads a report for a list of Nessus scan jobs.
The login information should be filled into the `config/connection.cfg` file. Given that this script has secret information, make sure that only administrators can read it, and that it is secure.
The program reads the configuration files to know which scans to download, and it also reads the configuration files to know what filters to look for in file names and what to replace them with.

## Dependencies
In order to run this, you need Python3 installed, and all of the dependencies mentioned in `REQUIREMENTS.txt`.
You can install all of these requirements using pip with `pip install -r REQUIREMENTS.txt`. The command syntax may change depending on your environment (it may be, per example, `python3 -m pip install -r REQUIREMENTS.txt`)
It is recommended that you create VIRTUAL ENVIRONMENTS to ensure that the program runs as expected.


## Usage
In order to use the script you will have to specify what jobs you want the program to get a report for. You can do this by changing `config/scanlist.dat`.
After starting the script, it will tell you that all files in the output folder will be deleted. This is to clean up for last execution. If you do not want this, please create a back up of the output folder and let the program delete the contents of the output folder as intended.
All of the downloaded files are saved in the `output` folder.
Detailed explanations below:


## Configuration
This program ships with configuration examples. If you think the examples are enough for you, go ahead and only use this section as a reference guide.


### Setting up connection info
All of the connection info is set in `config/connection.conf`. You should edit the URL line and make it whatever corresponds to your setup. You should specify the protocol, IP or hostname of the machine, as well as port. The last slash is not required but there's no harm in putting it in for neatness. Make sure you respect the spaces before and after "=".


### Setting up login info
Your login credentials also go in `config/connection.conf`. You should edit the `Username` and the `Password` lines to correspond to your Nessus username and password. Make sure that you respect the spaces before and after "=". 


### Setting up a list of scans
Your scan list goes in `config/scanlist.dat`. The file is structured as so:
```[Scan ID] [Title (optional)]```
Please make sure that there's a space after your scan ID.
You can get your scan ID by clicking on your scan in Nessus, and looking at the URL. Whatever number you find that is not part of the scan name will be its ID.


### Changing report format
When sending the request for Nessus to create the report, the file `report_query.json` is loaded, and it contains information about how the report should be structured. In it you can change parameters such as file format and fields. By default, the generated report will be of CSV type. Please look at the Nessus API docs to figure out how to change your query, or use a proxy such as BurpSuite to figure out what you need to insert in this file.


# Understanding the program
If you have read the previous chapters, you already have a decent idea of how the program handles the configuration files. This chapter has information about Nessus's API, and how the program handles it, as well as the structure of the program itself and how to tweak it to your liking.


## Program structure
This program is structured like so:
  - main.py
  - file_handler.py
  - downloader.py
  - config/
    - report_query.json
    - scanlist.dat
    - strings.conf
  - output/


### file_handler.py
This file is used as a python module. Inside it you find code related to the process of dealing with the Output folder. If you would like to edit the code to make it save files somewhere else, you can do so in this file.


### downloader.py
This file is used as a python module. Inside it you find code related to the process of communicating with the NESSUS server. It has functions and methods related to sending requests to the server to do various different actions such as getting a File Token (more info on tokens on the "NESSUS Requests" chapter)


### main.py
This file is the spine of the whole program. It connects all of the functions from `file_handler.py` and `downloader.py` and calls them in order to complete its objective.


### config
This folder stores all of the main configurations for the program.

`report_query.json` is the json file that is sent to the server, and contains information for the format of the report we are downloading. By default, this was obtained by analysing a packet sent by clicking on the "Generate report" button on NESSUS's interface. You can get this information however you want, such as using a proxy (BurpSuite, ZaProxy), or your browser's built in tools.

`scanlist.dat` contains a list of scan IDs that will be sent to NESSUS's report generation API. In order to obtain the ID, the program splits every line at the space bar and only uses the first one, so you can type whatever you want in this file as long as the first thing on each line is a valid scan id and a space. For examples check out the previous chapters.

`strings.conf` This file contains all filters to look for in the filename, as well as the intended replacements. For more info check out the previous chapters.


### output/
This folder stores the result of the program's execution. Everything that outputs files will be stored in here, and this is the folder that you should be checking after runnning the program.


## NESSUS Requests
In order to interact with NESSUS, this script uses the NESSUS built in API.
This chapter and following subchapters contain only information about how this program utilizes the NESSUS API. If you want more detailed information about the NESSUS API, please go look at their official documentation.


### Logging in
Sending a POST request to /session, with a `{"username":"username", "password":"password"}` data object in the request will return a session token, which will be used in future requests in the `X-Cookie` header to validate authentication. The X-Cookie header should look like so:
`X-Cookie: token=[TOKEN]`
In `downloader.py`, this process is handled in the `login` function.


### Creating a report
Sending a GET request to `/scans/[scanid]/export?limit=2500&` with a valid X-Cookie set will cause NESSUS to respond with a File Token, and to start preparing the report. This token uniquely represents a file in the server. After the file is downloaded, NESSUS gets rid of this token.
It is possible to upload JSON data to manipulate the format of this report.
This program loads `config/report_query.json` into this request to determine the intended report format.
In `downloader.py`, this process is handled in the `getReportToken` function.


### Validating a report
Sending a GET request to /tokens/[REPORT TOKEN]/status with a valid X-Cookie set will cause NESSUS to respond with "status", which represents the status of the requested report. If the report is ready to be downloaded, status will be `ready`. If status is ready, we know we can download the report.
In `downloader.py`, this process is handled in the `reportStatus` function.


### Downloading a report
Sending a GET request to /tokens/[REPORT TOKEN]/download with a valid X-Cookie set will cause Nessus to respond with the file contents, IF the report is ready for download. Read the previous subchapter to understand how we validate a report's validity.
In `downloader.py`, this process is handled in the `downloadReport` function.


# Contributing 
If you would like to contribute with bug fixes and improvements, go ahead and make a PR.
Make sure you follow through and respect the current code syntax (camelCase, two spaces between each function...), make sure you comment and document your code and that it is as readable as possible without any comments, and then submit a pull request. Make sure you're respecting the license in your PR.
If you would like to add a new big feature, please create a ticket so we can discuss it.



## Licensing
This script is licensed under the Apache 2.0 license. For more info, read the "LICENSE" file.
