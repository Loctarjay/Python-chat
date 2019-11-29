import socket
import time
import threading
import configparser



conf = configparser.ConfigParser()
conf.read("conf.ini")

startTime = time.time()
runProgram = True
runClient = False

def serverInfo():
    serverName = 'localhost'
    serverPort = 13000
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
    tempCon = serverInfo()
    while test <= 1:
        SYNMessage, tempClient = tempCon.recvfrom(2048)
        print(SYNMessage.decode())
        temp = SYNMessage.decode().split(" ")

        runProgram, runClient = conTest(SYNMessage.decode())
        if runProgram and runClient:
            if test == 0 and temp[0] == "com-0" and temp[1] == "done":
                print("test 1")
                serverAnswer = "com-0 accept"
                tempCon.sendto(serverAnswer.encode(), tempClient)

            elif test == 1 and temp[0] == "com-0" and temp[1] == "accept":
                print("Server Accepted client")
                print(f"Connection to {tempClient} has been made!")
                tempCon.sendto(str(runClient).encode(), tempClient)
                serverConn = tempCon
                client = tempClient
                return (runProgram, runClient), serverConn, client

            else:
                client = tempClient
                runClient = False
                test = 3
                tempCon.sendto(str(runClient).encode(), tempClient)
                return (runProgram, runClient), tempCon.close(), tempClient

        else:
            test = 3
            return (runProgram, runClient), tempCon.close(), tempClient

        test += 1

def Timer():
    return time.time()

package_counter = (time.time(), 0)


while runProgram:
    #Inside Server
    if runClient:
        print("Inside the chat server")
        while runClient:
            if (time.time() - package_counter[0]) >= 4:
                print("you there Client ????")
                serverConn.sendto("con-res 0xFE".encode(), client)
                temp, client = serverConn.recvfrom(2048)
                print(temp)
            else:
                testing, client = serverConn.recvfrom(2048)
                message = testing.decode()
                if "con-h 0x00" in message.lower():
                    print("Client Still Alive")

                elif ": " in message.lower():
                    print(f"msg-{message}")
                    counter = message.split(": ")


                    #Test if closing connection or system
                    runProgram, runClient = conTest(counter[1])
                    if runProgram:
                        if runClient:
                            serverAnswer = ": I am a server."
                            messageCount = int(counter[0]) + 1

                            responseMessage = str(messageCount) + serverAnswer
                            serverConn.sendto(responseMessage.encode(), client)
                        else:
                            serverConn.close()


    #Connection test
    else:
        print("Getting a Client")
        run, serverConn, client = clientTesting()
        runProgram, runClient = run