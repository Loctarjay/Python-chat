import socket
import time
import threading
import configparser
from datetime import datetime

conf = configparser.ConfigParser()
conf.read("conf.ini")

startTime = time.time()
runProgram = True
runClient = False
package_counter = (time.time(), 0)
timer = None

def logTrack(client):
    log = 'Successful Three-way handshake with user: '
    log2 = ', was established: '
    logFile = open('successLogin.txt', 'a')
    clientIP, clientPORT = client
    logTime = str(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

    logMessage = log + clientIP + ", " + str(clientPORT) + log2 + logTime

    logFile.write(logMessage)
    logFile.write('\n')
    logFile.close()

def serverInfo():
    serverName = 'localhost'
    serverPort = 11000
    serverS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverS.bind((serverName, serverPort))
    return serverS



def conTest(message):
    if message.lower() == "exit client" or message.lower() == "client exit":
        print("Client disconnected")
        return True, False
    elif message.lower() == "exit system" or message.lower() == "system exit":
        print("SYSTEM EXIT !!!!!!!!!")
        return False, False
    else:
        return True, True


def clientTesting():
    test = 0
    tempConn = serverInfo()
    while test <= 1:
        SYNMessage, tempClient = tempConn.recvfrom(2048)
        connTry = SYNMessage.decode()


        runProgram, runClient = conTest(connTry)
        if runProgram and runClient:
            if connTry == "com-0":
                serverAnswer = "com-0 accept"
                tempConn.sendto(serverAnswer.encode(), tempClient)

            elif connTry == "com-0 accept":
                print("Server Accepted client")
                print(f"Connection to {tempClient} has been made!")
                tempConn.sendto(str(runClient).encode(), tempClient)
                serverConn = tempConn
                client = tempClient
                logTrack(client)
                return (runProgram, runClient), serverConn, client

            else:
                client = tempClient
                runClient = False
                test = 3
                tempConn.sendto(str(runClient).encode(), tempClient)
                return (runProgram, runClient), tempConn.close(), tempClient

        else:
            test = 3
            return (runProgram, runClient), tempConn.close(), tempClient

        test += 1


def resetConn(serverConn):
    print('Resetting connection')
    print(address)
    resetting = "con-res 0xFE"
    serverConn.send(resetting)

def timerResetter(resetConn):
    if timer is not None:
        timer.cancel()
    timer = threading.Timer(4, resetConn, serverConn)
    timer.start()



message_Number_Reminder = -1

while runProgram:
    #Inside Server
    if runClient:
        print("Inside the chat server")
        while runClient:

            testing, client = serverConn.recvfrom(2048)

            if testing.startswith(b'con-'):
                if testing.decode() == "con-h 0x00":
                    print("Client is still alive.")
                    continue
                elif testing.decode() == "con-res 0xFF":
                    print("Client wants a reset.")

                    continue
            elif testing.startswith(b'msg-'):
                tempNumber = testing[4:].decode().split(": ")
                if int(tempNumber[0]) > message_Number_Reminder:

                    if (time.time() - package_counter[0]) <= 10:

                        if package_counter[1] < int(conf['Server']['MP']):
                            package_counter = (package_counter[0], package_counter[1] + 1)
                        else:
                            print('Received too many messages, skipping')
                            serverConn.sendto("skip".encode(), client)
                            time.sleep(3)
                            print("skipping is over")
                            serverConn.sendto("ready".encode(), client)
                            serverConn.sendto("res-1: Ready, but reset.".encode(), client)
                            package_counter = (time.time(), 0)
                            continue
                    else:
                        print("package counter reset")
                        package_counter = (time.time(), 0)


                    temp = testing.decode()
                    print(temp)
                    findInt = int(tempNumber[0])


                    #Test if closing connection or system
                    runProgram, runClient = conTest(tempNumber[1])
                    if runProgram:
                        if runClient:
                            serverAnswer = ": I am a server."
                            counter = findInt + 1

                            responseMessage = "res-" + str(counter) + serverAnswer
                            serverConn.sendto(responseMessage.encode(), client)
                            continue
                        else:
                            serverConn.close()



    #Connection test
    else:
        print("Getting a Client")
        run, serverConn, client = clientTesting()
        runProgram, runClient = run