"""
Max Deng
05/21/2022
RIT CSEC Junior
dengmax6@gmail.com (Contact for Inquiries and Phone Number)
"""

"""Imported Packages"""
import time #utilized to time abstract downloads
from Bio import Entrez #Python Bio Package includes NCBI search and fetch API functionality
import pandas as pd #Pandas utilzed to create and manipulate dataframes aswell as export to .csv files
import re #regular expression package cleans extraneous punctuation that may interfere with csv delimiters and corpus processing
try: 
    from lxml import etree as ET #lxml to manipulate NCBI fetch pipeline xml data
except ImportError:
    try: import xml.etree.ElementTree as ET #xml etree to convert data into python tangible objects
    except ImportError:
        print("Failed to import ElementTree Package")

"""getPMID Function utilizes BioPython NCBI Entrez esearch api functionality to retrieve
   a list of PMIDs/DOIs related to releveant keywords and search terms"""
def getPMID(email, searchterm, mindate, maxdate, recordlimit, database="pubmed"):
    Entrez.email = email #Email is a required functionality of the Entrez Esearch API
    if mindate == "": #specifying use cases of published date range of desired papers
        """retmax refers to maximum number of documents that will be pulled.
           idtype refers to the APIs output type, 'acc' refers to accession type"""
        handle = Entrez.esearch(db=database, retmax=recordlimit, term=searchterm, idtype="acc")
    else:
        handle = Entrez.esearch(db=database, retmax=recordlimit, term=searchterm, idtype="acc", mindate=mindate, maxdate=maxdate) #else case includes date parameters
    rec = Entrez.read(handle) #Taking collected data and creating python list of Article PMIDs
    handle.close() #Closing handle for posterity and to prevent memory leaks
    idlist = rec["IdList"] #Variable stores IDList for further use
    idlen = len(idlist) #Utilizng list length to determine success of request
    if idlen > 0:
        with open (str(searchterm) + "_pmidList.txt", "w") as output: #creating text file of pmid List for crediting purposes and later use
            output.write(str(idlist)) #using standard system output to write text file (Unlikely, but may present potential security risks.)
        return idlist #returns idlist for use in next function
    else:
        print("No PMIDs matching search term") #Request failure warning
        return idlist #returning empty list


"""fetchAbstracts function utilizes BioPython NCBI Entrez efetch functionality to retrieve
   Abstracts from articles contained within the IDlist"""
def fetchAbstracts(idlist): 
    abstracts = [] #Initiating list to store pulled abstracts, will be used to create a pandas dataframe
    dois = [] #Initiating list to store pulled PMID/DOI info, will be used to create pandas dataframe
    authors = [] #Initiating list to store author name and information, will be used to create pandas dataframe
    counter = 1 #Counter for user transparency and error checking
    for uid in idlist: #Iterating over list of ids
        start = time.time() #Timer for user transparency and error checking
        abs_constructor = "" #Initializing constructor string, as articles may have xml tags separating article
        """BioPython NCBI Entrez efetch api is utilized as an xml pipeline to retrieve articles
           with the list of collected IDs"""
        fetch_handle = Entrez.efetch(db="pubmed", id= uid, retmode="xml") #Retmode specifies that retrieved data is in xml format
        fetch_data = ET.parse(fetch_handle) #Creating an ElementTree out of xml data
        fetch_handle.close() #Closing handle for posterity and to prevent memory leak
        root = fetch_data.getroot() #creating ElementTree root
        Abstract_Element = list(root.iter('Abstract')) #Finding all Elements with the Abstract Tag
        Author_Element = list(root.iter('Author')) #Finding all Elements with the Author Tag
        au_list = "" #author list string initiation
        dois.append(uid) #Appending the current PMID into the corresponding index so all information matches up

        for author in Author_Element: #Iterating over all Elements within current article that contain the author tag
            au_name = ET.tostring(author, encoding='utf8', method='text').decode() #Converting Element values to utf8 ascii text (removes xml tags and formating)
            au_list += str(au_name) + " " #Building author string
        authors.append(au_list) #Appending string of authors to authors list


        if len(Abstract_Element) < 1: #In the event that the current article contains no abstract
            abs_constructor += "No Abstract" #Fill in No Abstract
        else:
            Abstract_Children = list(Abstract_Element[0].iter('AbstractText')) #Iterate over all elements within Abstract Element that contain AuthorText Tag
            for child in Abstract_Children: #Case handles italics, comments, labels, formatted newlines
                ab_text = ET.tostring(child, encoding='utf8', method='text').decode() #Converting Element values to utf8 acscii text (removes xml tags and formating)
                ab_text = re.sub(r'[^\w\s]', '', ab_text) #Regular expression to remove punctuation that can interfere with csv delimiters
                abs_constructor += str(ab_text) #Building Abstract string


        abstracts.append(abs_constructor) #Appending string of constructed abstract to abstracts list
        end = time.time() #Collecting the time it took to complete extracting desired data from xml pipeline
        runtime = (end - start) #Calculating total runtime
        print("Downloaded Article: " + str(counter) + "/" + str(len(idlist)) + " in: " + str(runtime) + " seconds.") #Used for user transparency and error checking
        counter +=1 #Counter keeps track of which article in list of ID's is currently being processed
    return abstracts, dois, authors #returning list values to be used in constructing pandas dataframe


"""Simple csv/file exporting function that utilizes Pandas DataFrame packages and utilities"""
def createCSV(abstracts, dois, authors, filename):

    pdcols = [ #Identifying DataFrame header column values
        'Abstract', #Abstract Column
        'DOIS', #PMID/DOI Column
        'Authors' #Author Column
    ]

    data = { #Dictionary of data values
            'Abstract': abstracts, #Abstracts list collected in fetchAbstracts() function
            'DOIS': dois, #PMID list collected in fetchAbstracts() function
            'Authors':authors} #Authors list collected in fetchAbstracts() function


    df = pd.DataFrame(data) #Creating DataFrame utilizing Pandas package

    search_csv_output_filename = str(filename) + ".csv" #Constructing filename
    df.to_csv(str(search_csv_output_filename), index= False) #Converting DataFrame to .csv file utilzing Pandas functionality

"""Main Function For Terminal Use"""

if __name__ == "__main__":
    run = True
    while run == True:
        print("\n \n \n \n \n")
        print("Welcome! the purpose of this program is to fetch and download large batches of text from the NCBI pubmed library. \nIf at any point the program halts, utilize unix command line function ctrl-z to interrupt the program \n")
        email = input("Please Enter Work or NCBI registered email: \n")
        if email == "":
            print("Sorry, an Email is required to utilize this program" +"\n")
        else:
            confirmation = input("Email recieved, Confirm? (y/n): " + str(email) + "\n")
            if confirmation.lower() == ("n"):
                run = True
            else:
                searching = True
                while searching == True:
                    searchterms = input("Input desired Keywords and Search term: ")
                    print("Search term is: '" + str(searchterms) + "'\n")
                    date_range = input("Input date range (YYYY/MM/DD space YYYY/MM/DD) [Optional]: \n")
                    if date_range != "":
                        print("\nStart date is: " + str(date_range[0:10]))
                        search_mindate = str(date_range[0:10])
                        print("\nEnd date is: " + str(date_range[11:21]))
                        search_maxdate = str(date_range[11:21])
                    else:
                        print("No date range \n")
                        search_mindate = ""
                        search_maxdate = ""
                    
                    record_limit = input("Maximum number of records to search? (Suggested 2000-50000): \n")
                    print("Max Records = " + (str(record_limit)))
                    
                    pmid_list =  getPMID(email, searchterms, search_mindate, search_maxdate, record_limit)
                    if len(pmid_list) == 0:
                        print("Restarting query \n")
                        searching = True
                    else:
                        searching = False
                print("\nPMIDs collected, .txt file created, would you like to continue? (y/n) \n")
                
                fetch_continue = input()
                if fetch_continue.lower() == "n":
                    run = False
                else:
                    abstracts, dois, authors = fetchAbstracts(pmid_list)
                    download_continue = input("\nArticles are fetched, create a csv file?: (y/n)")
                    if download_continue.lower == "n":
                        print("\nCSV file NOT created, Goodbye! ")
                        run = False
                    else:
                        csv_filename = input("\nName your csv file (do not include .csv): ")
                        createCSV(abstracts, dois, authors, csv_filename)
                        print("\nFinished, csv file created. Thank you and Goodbye! \n")
                        run = False



    

