# PLEASE READ THE README FILE #
# This program will attempt to do the following:
# It will log into Nessus and get a login token
# It will grab a list of Nessus Scan IDs from the config file
# It will send a request to create a report for each of those Scan IDs
# It will send a request to validate the status of the report
# If the report is ready, it will send a request to download the report
# All files will be downloaded into the ./output/ folder
# It will then iterate all of the files in the output folder.
# For each file in the output folder, it will check if the name...
# corresponds to a filter set in ./config/strings.conf, and if so,
# rename the file like so:
# REPLACEMENT_YEAR-wWEEK.csv
import file_handler 
import downloader
import concurrent.futures


# Removes all None types from a list
def filterNones(valueList):
    newList = []
    for value in valueList:
        if value != None:
            newList.append(value)
    return newList

# This executes everything.
def main():
    # Making sure the user knows what they are getting into
    print("Running this script will delete everything in the output folder.")
    userContinue = input("Are you sure you want to continue? (y/N) ")
    if str(userContinue.lower()) != "y":
        print("Exiting...")
        exit()
    
    # Logs into Nessus
    print("Logging into Nessus...")
    loginData = downloader.getLoginCredentials()
    loginToken = downloader.login(loginData)
    if loginToken == None:
        exit()
    print("Successfully logged in!")

    # Delete all files in output folder
    file_handler.cleanOutputFolder()
    
    # Lists for asynchronous downloading of files
    try:
        scanIDs = downloader.getScanList()
        futures = []
        reportTokens = []
    except Exception as e:
        print("An error occurred:")
        print(e)
        exit()

    print("Getting report tokens...")
    # Iterate through every scan
    # The executor executes asynchronous tasks
    # We execute all requests at once to exponentially speed up the program
    # We get all the tokens for all of the requests first
    for ID in scanIDs:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            reportToken = executor.submit(downloader.getReportToken, loginToken, ID)
            futures.append(reportToken)
            reportTokens.append(reportToken.result())

    # Wait to for all of the report tokens to be obtained before proceeding
    concurrent.futures.wait(futures)
    print("Obtained report tokens!")

    # Remove all of the reports that returned "None"
    reportTokens = filterNones(reportTokens) 

    # We need to know how many reports we are going to download
    print("Got " + str(len(reportTokens)) + " reports to download.")

    print("Downloading reports...")
    downloadedReports = []
    for report in reportTokens:
        # Check validity of all reports
        with concurrent.futures.ThreadPoolExecutor() as executor:
            status = executor.submit(
                     downloader.reportStatus, loginToken, report)
            # If the report is ready, the program will download it
            if status:
                with concurrent.futures.ThreadPoolExecutor() as executor2:
                    downloadedReports.append(executor.submit(
                    downloader.downloadReport, loginToken, report))

main()
