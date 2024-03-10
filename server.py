"""
Sources utilized in the program:
Server:
https://docs.python.org/3/library/xmlrpc.server.html#simplexmlrpcserver-example

Client:
https://docs.python.org/3/library/xmlrpc.client.html#module-xmlrpc.client

Multithreading:
https://docs.python.org/3/library/socketserver.html

"""

import xml.etree.ElementTree as T
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.server import SimpleXMLRPCServer
import socketserver as ss
import socket

dbFile = "db.xml"
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/ripc',)

## Initialization for multithreading for multiple requests
class ThreadedXMLRPCServer(ss.ThreadingMixIn, SimpleXMLRPCServer):
    pass
"""
This function could be used to find a free port for each server to use
but I am not actually utilizing this function as I am not doing the additional part due to
schedule
"""
def findFreePort():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

"""
For multithreaded use the ThreadedMixIn class of socketserver library is used to allow multiple client
requests to be handles asynchronously
src: https://docs.python.org/3/library/socketserver.html
"""
try:
    with ThreadedXMLRPCServer(("localhost", 8000), requestHandler=RequestHandler) as server:
        server.register_introspection_functions()
        try:
            db = T.parse(dbFile)
        except FileNotFoundError:
            print(f"File '{dbFile}' not found.")

        except T.ParseError:
            print(f"Error while parsing '{dbFile}'.")
        
        def ping():
            return True
        
        def addNote(topic, note, text, ts):
            root = db.getroot()
            try:
                ## Searching through the xml to find topic and add note to it.
                for c in root:
                    if 'name' in c.attrib and c.attrib['name'] == topic:
                        newNote = T.SubElement(c, 'note', {'name': note})
                        T.SubElement(newNote, 'text').text = text
                        T.SubElement(newNote, 'timestamp').text = ts
                        ## Used to format .xml file to multiple lines
                        T.indent(db.getroot(), space="    ")
                        ## encoding is used to ensure that chars such as ö,ä,å are properly handled
                        db.write(dbFile, encoding='utf-8', xml_declaration=True)
                        return True
            
                ## If the topic does not exist, it is created and  
                ### this function is called again to add note to it
                topic_element = T.SubElement(root, 'topic', {'name': topic})
                T.indent(db.getroot(), space="    ")
                ## encoding is used to ensure that chars such as ö,ä,å are properly handled
                db.write(dbFile, encoding='utf-8', xml_declaration=True)
                return addNote(topic, note, text, ts)

            except AttributeError:
                print("Could not find expected attribute")
                return False

        def getNotes(topic):
            root = db.getroot()
            try:
                for c in root:
                    if c.attrib['name'] == topic:
                        ## Information is stored to dict for easier reading format on client side
                        notes = {}
                        for n in c:
                            nName = n.attrib['name']
                            nName = nName.strip().replace('\n', '')
                            nText = n.find('text').text
                            nText = nText.strip().replace('\n', '')
                            nTS = n.find('timestamp').text
                            nTS = nTS.strip().replace('\n', '')
                            notes[nName] = {'text': nText, 'timestamp': nTS}
                        return notes
                ## If the information the user is trying to find, cannot be found the function return empty
                ## dictionary which is checked at clients side and informed to the user.
                print("Information not found returning empty dict")
                return {}
            except AttributeError:
                print("Could not find expected attribute")
                return {}

        """
        This function is purely made for testing the server and should not be used for anything else
        """
        def deleteTopic(topic):
            root = db.getroot()
            for c in root:
                if 'name' in c.attrib and c.attrib['name'] == topic:
                    root.remove(c)
                    db.write(dbFile, encoding="utf-8", xml_declaration=True)
                    return True
            print("Information not found")
            return False


        ## Server functions
        server.register_function(addNote, 'addNote')
        server.register_function(getNotes, 'getNotes')
        server.register_function(deleteTopic, 'deleteTopic')
        server.register_function(ping, 'ping')

        ## Server runs until killed
        server.serve_forever()
except socket.error as e:
    print(f"Socket error:{e}")
