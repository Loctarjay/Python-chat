import socket
import configparser
import threading

conf = configparser.ConfigParser()
conf.read('conf.ini')

server_connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverName = 'localhost'
serverPort = 11000
runSystem = True
runClient = False
heartbeater = None
overload = False

# Handshake with input
def handshake():
    conCount = 0
    server_connection.connect((serverName, serverPort))
    while conCount <= 1:
        if conCount == 0:
            SYNMessage = "com-0"
            server_connection.send(SYNMessage.encode())
        elif conCount == 1:
            temp, serverAddress = server_connection.recvfrom(2048)
            message = temp.decode()
            # Testing if rejected or accepted
            if " " in message.lower():
                if message.lower() == "com-0 accept":
                    server_connection.send("com-0 accept".encode())
                    con = server_connection.recv(2048)
                    message = con.decode()

                    runSystem = True

                    # Server rejected client
                    if message.lower() == "false":
                        runClient = not bool(message)
                    else:
                        runClient = True
                    return (runSystem, runClient), server_connection

            # Server rejected client
            else:
                if message.lower() == "false":
                    # Problem when message = False
                    # bool(message) changed into True
                    # so IF message = false, then bool(message) must be not bool(message)
                    runClient = not bool(message)
                    conCount = 3
                return (runSystem, runClient), server_connection
        conCount += 1



# Test if client is using "exit" for client or system
# method use for less redundancy
def conTest(message):
    # Client disconnection
    if message.lower() == "exit client" or message.lower() == "client exit":
        print("Client disconnected")
        return True, False

    # System and client disconnection
    elif message.lower() == "exit system" or message.lower() == "system exit":
        print("System EXIT !!!!!!!!")
        return False, False

    # All good
    else:
        return True, True

# Used for sending
# method use for less redundancy
def sendMessage(message, counter):
    # See conTest-method
    runSystem, runClient = conTest(message)

    # Constructing counter: message
    # where counter is 1 higher than recieved
    counter += 1
    currentMessage = "msg-" + str(counter) + ": " + message
    clientCon.send(currentMessage.encode())

    return runSystem, runClient

def heartbeat():
    server_connection.send("con-h 0x00".encode())
    heartbeater = threading.Timer(3, heartbeat)
    heartbeater.start()




# System itself
while runSystem:


    # Running if client is connected
    if runClient:

        if firstCon:
            message = input("Write to the server: ")
            counter = -1
            runSystem, runClient = sendMessage(message, counter)
            firstCon = False
        else:
            temp = clientCon.recv(2048).decode()
            if temp.lower() == "skip":
                overload = True
            if overload:
                print("to many messages")
                waiting = clientCon.recv(2048).decode()
                if waiting == "ready":
                    print("ready again.")
                    overload = False
                    continue
                else:
                    continue

            else:
                if temp.startswith("con-"):
                    print("Server Resetting Connection")
                    firstCon = True
                    clientCon.send("con-res 0xFF")
                else:
                    tempCounter = temp[4:]
                    findInt = tempCounter.split(": ")
                    counter = int(findInt[0])

                    print(temp)
                    message = input("Write to the server: ")

                    runSystem, runClient = sendMessage(message, counter)


    else:
        run, clientCon = handshake()

        runSystem, runClient = run
        if runClient:
            if conf["Client"]["KeepAlive"] == "yes":
                heartbeat()
            firstCon = True