"""
Sources utilized in the program:
Server:
https://docs.python.org/3/library/xmlrpc.server.html#simplexmlrpcserver-example

Client:
https://docs.python.org/3/library/xmlrpc.client.html#module-xmlrpc.client

Multithreading:
https://docs.python.org/3/library/socketserver.html

"""
import random
import xmlrpc.client
from datetime import datetime as d
try:
    with xmlrpc.client.ServerProxy("http://localhost:8000/ripc") as proxy:
        
        ## Ping server to ensure the connection is okay before trying to add or fetch stuff
        isConnected = proxy.ping()
        if not isConnected:
            print("Cannot connect to server, aborting...")
            
        while isConnected:
            print()
            print("########  MENU  #########")
            print("Available Options:")
            print("[1] Add New Topic")
            print("[2] Search Based on Topic")
            print("[3] Test Server add / get")
            print("[0] Exit Program")
            usrInput = input("Your choice: ")
            print()
            if usrInput == '1':
                ## REQUIRED INFORMATION FOR NOTE
                topic = input("Give note topic: ")
                while not topic.strip():
                    topic = input("Note topic required: ")    
                
                note = input("Give note name: ")
                while not note.strip():
                    note = input("Note name required: ")
                
                text = input("Give note text: ")
                while not text.strip():
                    text = input("Note text required: ")
                
                ## As this is done automatically, user can not mess this up
                ts = d.now().strftime("%d/%m/%Y %H:%M:%S")
                print("Current Timestamp:", str(ts))
                if proxy.addNote(topic, note, text, str(ts)):
                    print("\nInformation stored successfully")
                    continue
                print("\nCould not store information, sorry")
            
            elif usrInput == '2':
                topic = input("Topic to search for: ")
                while not topic.strip():
                    topic = input("Topic Reguired: ")
                    
                notes = proxy.getNotes(topic)

                if not notes:
                    print("No information found... moving on")
                    continue
                print()
                print("Found information:")    
                for k, v in notes.items():
                    print("note :", k)
                    print("text :", v['text'])
                    print("Timestamp :", v['timestamp'])
                    print()


            #################################################################################################
            ## This option is purely for testing purposes of the server with multiple connecting clients   ##
            ##     which try to write and access data from the server database                             ##
            ## NOTE: as this function can delete specific data from database, if two clients have the same ##
            ##  ID ( random generated ) all data associated with that ID can be lost                       ##
            ##   if client decides to remove test data, all other clients lose access to that data aswell. ##
            #################################################################################################
            elif usrInput == '3':
                ## This way we can delete only client specific data (based on probability)
                rInt = random.randint(0,1000)
                topic = f"Server Test {rInt}"

                for i in range(500):
                    print()
                    print()
                    print(i, ") Server insert operation....")
                    note = f"ID:{rInt} Test Note {i}"
                    text = f"This is server testing note text {2**i}"
                    ts = str(d.now().strftime("%d/%m/%Y %H:%M:%S"))
                    proxy.addNote(topic, note, text, ts)

                    print("Server fetch operation....")
                    notes = proxy.getNotes(topic)
                    if not notes:
                        print("No information found... moving on")
                        continue
                    
                    print()
                    print("Found information:")    
                    for k, v in notes.items():
                        print("Note :", k)
                        print("Text :", v['text'])
                        print("Timestamp :", v['timestamp'])
                        print()
                uInp = input("Do you wish to delete testing data [y/n]: ")
                if 'n' in uInp or '0' in uInp:
                    continue
                if proxy.deleteTopic(topic):
                    print("Data deleted")
                    continue
                print("No more data to be deleted")
                
            elif usrInput == '0':
                print("Kiitos Ohjelman Käytöstä.")
                break
            else:
                print("Try again.")

except xmlrpc.client.Fault as e:
    print("A fault occured")
    print("Code:", e.faultCode)
    print("Fault string:", e.faultString)
    print("Abort!")
except Exception as e:
    print("Exception occured")
    print(e)
