import socket, threading , time , math , random
p = 0.1
ScenarioFile = 'Scenario.txt'
# Reading Scenario

lines = [line.rstrip('\n').replace(".", "") for line in open(ScenarioFile)]
r = [int(s) for s in lines[1].split() if s.isdigit()][0]
L = [int(s) for s in lines[2].split() if s.isdigit()][0]
W = [int(s) for s in lines[3].split() if s.isdigit()][0]
N = [int(s) for s in lines[4].split() if s.isdigit()][0]
T = [int(s) for s in lines[5].split() if s.isdigit()][0]
Delays =[]
def code(msg):
    codedmsg = msg + "?}?}"
    return codedmsg
def mdecode(msg):
    s = msg.find("?}?}")
    decodedmsg = msg[0:s]
    return decodedmsg
for i in range(N):
    temp = [int(s) for s in lines[i+7].split() if s.isdigit()]
    Delays.append(temp[5])
Maximum_Delay = max(Delays)
UIDs = []
for i in range(N):
    temp = [int(s) for s in lines[i+7].split() if s.isdigit()]
    UIDs.append(temp[0])

HelloList = [False]*N
def HelloListTrue(idx):
    HelloList[idx]=True
def HelloListFalse(idx):
    HelloList[idx]=False
def HelloListaccess():
    return HelloList
# Defining Clientthread Class
class ClientThread:
    def __init__(self,clientAddress,clientsocket,r,totallNum,dropNum):
        self.csocket = clientsocket
        self.r = r
        self.totallNum = 0
        self.dropNum = 0
        
    def Receive(self):
        msg = ''
        while True:
            data = self.csocket.recv(2048)
            self.totallNum = self.totallNum + 1
            msg = data.decode()
            msg = mdecode(msg)
            # initial Format: UID X Y
            if msg[0:5] == 'Hello':
                self.dropmodel(p)
                idx = UIDs.index(self.UID)
                HelloListTrue(idx)
                temp = [int(s) for s in msg.split() if s.isdigit()]
                self.LocationX = temp[1]
                self.LocationY = temp[2]
            elif msg[0:4] == 'init':
                temp = [int(s) for s in msg.split() if s.isdigit()]
                self.UID = temp[0] 
                self.LocationX = temp[1]
                self.LocationY = temp[2]
                self.dropmodel(p)
            elif msg[0:7] == 'InitRep':
                self.dropmodel(p)
                temp = [int(s) for s in msg.split() if s.isdigit()]
                idx = UIDs.index(temp[1])
                Clients[idx].Send(msg)
            elif msg[0:9] == '-HelloRep':
                self.dropmodel(p)
                temp = [int(s) for s in msg.split() if s.isdigit()]
                idx = UIDs.index(temp[1])
                Clients[idx].Send(msg)
            elif msg[0:4] == 'RREQ':
                self.dropmodel(p)
                temp = [int(s) for s in msg.split() if s.isdigit()]
                idx = UIDs.index(temp[4])
                s = msg.find(" nextHOP = ")
                msg = msg[0:s] + ' from UID ' + str(self.UID)
                Clients[idx].Send(msg)
            elif msg[0:4] == 'RREP':
                self.dropmodel(p)
                temp = [int(s) for s in msg.split() if s.isdigit()]
                idx = UIDs.index(temp[4])
                s = msg.find(" nextHOP = ")
                msg = msg[0:s] + ' from UID ' + str(self.UID)
                Clients[idx].Send(msg)
            elif msg[0:7] == 'Message':
                self.dropmodel(p)
                msgNH = msg[msg.find(" nextHOP = ") : len(msg)]
                temp = [int(s) for s in msgNH.split() if s.isdigit()]
                idx = UIDs.index(temp[0])
                s = msg.find(" nextHOP = ")
                msg = msg[0:s]
                Clients[idx].Send(msg)
    def flipcoin(self):
        x = random.uniform(0, 1)
        if x>p :
            Y = False
        else :
            Y = True
        return Y
    
    def dropmodel(self,p):
        idx = UIDs.index(self.UID)
        cond = False
        while not(cond):
            self.dropNum = self.dropNum + 1
            q = self.flipcoin()
            if q==True:
                cond = False
                time.sleep(Delays[idx])
            else :
                cond = True
            
            
        
        
            
    def Send(self,msg):
        print(msg)
        Sthread = threading.Thread(target=self.Sendfunc , args = (msg,))
        Sthread.setDaemon(True)
        Sthread.start()
        
    def Sendfunc(self,msg):
        self.csocket.sendall(bytes(code(msg),'UTF-8'))  

    def run(self):
        Rthread = threading.Thread(target=self.Receive)
        Rthread.setDaemon(True)
        Rthread.start()


#Creating the server socket
LOCALHOST = "127.0.0.1"
PORT = 8081
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))
Clients = []

# Connecting the servers to vehicles
totallNum = 0
dropNum = 0
for i in range(N):
    server.listen()
    clientsock, clientAddress = server.accept()
    newClienthread = ClientThread(clientAddress, clientsock,r,totallNum,dropNum)
    newClienthread.run()
    Clients.append(newClienthread)


time.sleep(Maximum_Delay + 1)



# Broadcasting initialization Information
for i in range(N):
    SendIndice = list(range(N))
    SendIndice.remove(i)
    vs = Clients[i]
    y = (vs.LocationX,vs.LocationY)
    r = vs.r
    for j in SendIndice:
        vr = Clients[j]
        x = (vr.LocationX,vr.LocationY)
        Distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(x, y)]))
        if (Distance < r) and (Distance>0) :
            RoutingUpdate = "init : SourceUID " + str(vs.UID) + " XLocation " + str(vs.LocationX) + " YLocation " + str(vs.LocationY)
            vr.Send(RoutingUpdate)
time.sleep(Maximum_Delay + 1)

# Now the Initialization phase is finished 


def HelloReply():
    q = [True]*N
    while True :
        L=HelloListaccess()
        while L!=q:
            pass
        for i in range(N):
            SendIndice = list(range(N))
            SendIndice.remove(i)
            vs = Clients[i]
            y = (vs.LocationX,vs.LocationY)
            r = vs.r
            for j in SendIndice:
                vr = Clients[j]
                x = (vr.LocationX,vr.LocationY)
                Distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(x, y)]))
                if (Distance < r) and (Distance>0) :
                    RoutingUpdate = "Hello : SrcUID " + str(vs.UID) + " XLoc " + str(vs.LocationX) + " YLoc " + str(vs.LocationY)
                    vr.Send(RoutingUpdate)
            vs.Send("Finished Hello")
        for i in range(N):
            HelloListFalse(i)

HelloReplythread = threading.Thread(target= HelloReply)
HelloReplythread.setDaemon(True)
HelloReplythread.start()