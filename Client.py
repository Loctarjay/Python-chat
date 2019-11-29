import socket
import configparser
import threading

conf = configparser.ConfigParser()
conf.read('conf.ini')
server_connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverName = 'localhost'
serverPort = 13000
runSystem = True
runClient = False
heartbeater = None

# Handshake with input
def handshake():
    conCount = 0
    server_connection.connect((serverName, serverPort))
    while conCount <= 1:
        if conCount == 0:
            # To connect, write: com-0
            SYN = input("Send your request: ")
            # See conTest-method
            runProgram, runClient = conTest(SYN)
            if runProgram and runClient:
                SYNMessage = SYN + " done"
                server_connection.send(SYNMessage.encode())
        elif conCount == 1:
            temp, serverAddress = server_connection.recvfrom(2048)
            message = temp.decode()
            # Testing if rejected or accepted
            if " " in message.lower():
                if message.lower() == "com-0 accept":

                    # To connect, write: com-0 accept
                    ACK = input("Send your ack.: ")
                    # See conTest-method
                    runProgram, runClient = conTest(ACK)

                    if runProgram and runClient:
                        server_connection.send(ACK.encode())
                        con = server_connection.recv(2048)
                        message = con.decode()

                        # Server rejected client
                        if message.lower() == "false":
                            runClient = not bool(message)
                        return (runProgram, runClient), server_connection

                    # Client used "exit"
                    else:
                        server_connection.send(ACK.encode())
                        conCount = 3
                        return (runProgram, runClient), server_connection

            # Server rejected client
            else:
                if message.lower() == "false":
                    # Problem when message = False
                    # bool(message) changed into True
                    # so IF message = false, then bool(message) must be not bool(message)
                    runClient = not bool(message)
                    conCount = 3
                return (runProgram, runClient), server_connection
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
    program, client = conTest(message)

    # Constructing counter: message
    # where counter is 1 higher than recieved
    counter += 1
    currentMessage = str(counter) + ": " + message
    clientCon.send(currentMessage.encode())

    return program, client

def heartbeat(clientCon):
    server_connection.send("con-h 0x00".encode())
    heartbeater = threading.Timer(3, heartbeat, [clientCon])
    heartbeater.start()




# System itself
while runSystem:


    # Running if client is connected
    if runClient:

        if conf["Client"]["KeepAlive"] == "yes":
            heartbeat(clientCon)

        if firstCon:
            message = input("Write to the server: ")
            counter = -1
            runSystem, runClient = sendMessage(message, counter)
            firstCon = False
        else:
            temp = clientCon.recv(2048).decode()
            if temp == "con-res 0xFE":
                print("server response")
            else:
                findInt = temp.split(": ")
                counter = int(findInt[0])

                print(f"res-{temp}")
                message = input("Write to the server: ")

                runSystem, runClient = sendMessage(message, counter)

    else:
        run, clientCon = handshake()
        runSystem, runClient = run
        if runClient:
            firstCon = True