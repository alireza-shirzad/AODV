import socket, threading , time , random , math
from threading import Timer
start = time.time()
ScenarioFile = 'Scenario.txt'
# Reading Scenario
lines = [line.rstrip('\n').replace(".", "") for line in open(ScenarioFile)]
r = [int(s) for s in lines[1].split() if s.isdigit()][0]
L = [int(s) for s in lines[2].split() if s.isdigit()][0]
W = [int(s) for s in lines[3].split() if s.isdigit()][0]
N = [int(s) for s in lines[4].split() if s.isdigit()][0]
T = [int(s) for s in lines[5].split() if s.isdigit()][0]



global HelloReplyList
HelloReplyList = [False]*N

SERVER = "127.0.0.1"
PORT = 8081
Max_Distance = math.sqrt(sum([L ** 2 , W ** 2]))+1
Max_HOPCount = N

global UIDs
UIDs = []

def code(msg):
    codedmsg = msg + "?}?}"
    return codedmsg
def mdecode(msg):
    s = msg.find("?}?}")
    decodedmsg = msg[0:s]
    return decodedmsg

# Routing tables have 4 coloumns
# Destination Address # Next HOP # HOP Count # Destination Sequence Number # Life Time # Validity
h = 6

class Vehicle:
    def __init__(self,IP,Port,UID,LocationX,LocationY,diameter,Delay):
        self.Messages = []
        self.IP = IP
        self.Port = Port
        self.UID = UID
        UIDs.append(UID)
        self.LocationX = LocationX
        self.LocationY = LocationY
        self.diameter = diameter
        self.Delay = Delay
        self.DistanceTable = [Max_Distance] * N
        self.RoutingTable = [[[] for x in range(h)] for y in range(N)]
        idx = UIDs.index(self.UID)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER, PORT))
        self.csocket = client
        
        
    def Receive(self):
        msg = ''
        while True:
            data = self.csocket.recv(2048)
            msg = data.decode()
            msg = mdecode (msg)
            if (msg[0:4] == 'init'):
                print ("\n Receive " + str(self.UID) + " " + msg)
                self.Messages.append(msg)
                temp = [int(s) for s in msg.split() if s.isdigit()]
                idx = UIDs.index(temp[0])
                x = (temp[1],temp[2])
                y = (self.LocationX,self.LocationY)
                Distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(x, y)]))
                self.DistanceTable[idx] = Distance
                self.Send('InitRep : SourceUID ' + str(self.UID) + ' Destination UID ' + str(temp[0]) )
            elif (msg[0:7] == 'InitRep'):
                print ("\n Receive " + str(self.UID) + " " + msg)
                self.Messages.append(msg)
            elif (msg[0:9] == '-HelloRep'):
                print ("\n Receive " + str(self.UID) + " " + msg)
                self.Messages.append(msg)
            elif (msg[0:8]=='Finished'):
                print ("\n Receive " + str(self.UID) + " " + msg)
                self.Messages.append(msg)
                idx = UIDs.index(self.UID)
                HelloReplyList[idx] = True
            elif (msg[0:4]=='RREQ'):
                print ("\n Receive " + str(self.UID) + " " + msg)
                temp = [int(s) for s in msg.split() if s.isdigit()]
                SrcUID = temp[0]
                DstUID = temp[1]
                Dstidx = UIDs.index(DstUID)
                Srcidx = UIDs.index(SrcUID)
                SrcSeqNum = temp[2]
                HopCount = temp[3]
                fromUID = temp[4]
                self.Messages.append("from "+ str(fromUID)+msg)
                if self.RoutingTable[Srcidx][3]<SrcSeqNum :
                    self.RoutingUpdatefunc(SrcUID,fromUID,HopCount,SrcSeqNum)
                    if HopCount < Max_HOPCount :
                        temp = [int(s) for s in msg.split() if s.isdigit()]
                        if self.RoutingTable[Dstidx][5] == True:
                            self.RREP(SrcUID,DstUID)
                        else:
                            HopCount  = HopCount + 1
                            msg = 'RREQ : SRCUID= ' + str(SrcUID) + ' DSTUID= ' + str(DstUID) + ' SrcSeqNum ' + str(SrcSeqNum) + ' HOPCount ' + str(HopCount) + ' '
                            self.Broadcast(msg,fromUID)
                            
            elif (msg[0:4]=='RREP'):
                print ("\n Receive " + str(self.UID) + " " + msg)
                temp = [int(s) for s in msg.split() if s.isdigit()]
                SrcUID = temp[0]
                DstUID = temp[1]
                Dstidx = UIDs.index(DstUID)
                Srcidx = UIDs.index(SrcUID)
                SrcSeqNum = temp[2]
                HopCount = temp[3]
                fromUID = temp[4]
                self.Messages.append("from "+ str(fromUID)+msg)
                if self.RoutingTable[Srcidx][3]<SrcSeqNum :
                    self.RoutingUpdate(SrcUID,fromUID,HopCount,SrcSeqNum)
                    if HopCount<Max_HOPCount :
                        if self.UID == DstUID:
                            print ("\nRoute has been stablished successfully !!!")
                        else: 
                            HopCount  = HopCount + 1
                            msg = 'RREP : SRCUID= ' + str(SrcUID) + ' DSTUID= ' + str(DstUID) + ' SrcSeqNum ' + str(SrcSeqNum) + ' HOPCount ' + str(HopCount) + ' '
                            self.Send(msg)

            elif (msg[0:7]=='Message'):
                print ("\n Receive " + str(self.UID) + " " + msg)
                temp = [int(s) for s in msg.split() if s.isdigit()]
                DstUID = temp[1]
                if DstUID==self.UID :
                    s = msg.find("::")
                    SrcUID = temp[0]
                    M = msg[s+2:len(msg)-1]
                    s = M.find("::")
                    M = M[0:s]
                    end = time.time()
                    print(end-start)
                    self.Messages.append("from "+ str(SrcUID)+ M)
                else:
                    self.Send(msg)
            elif (msg[0:5]=='Hello'):
                print ("\n Receive " + str(self.UID) + " " + msg)
                self.Messages.append(msg)
                temp = [int(s) for s in msg.split() if s.isdigit()]
                idx = UIDs.index(temp[0])
                x = (temp[1],temp[2])
                y = (self.LocationX,self.LocationY)
                Distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(x, y)]))
                self.DistanceTable[idx] = Distance
                self.Send('-HelloRep : SourceUID ' + str(self.UID) + ' Destination UID ' + str(temp[0]) )
                    
                    
    def RREP(self,SrcUID,DstUID) :
        idx = UIDs.index(self.UID)
        Srcidx = UIDs.index(SrcUID)
        Dstidx = UIDs.index(DstUID)
        self.RoutingTable[Dstidx][3] = self.RoutingTable[Dstidx][3] + 1
        seqNum = self.RoutingTable[Dstidx][3]
        RREPmsg = 'RREP : SRCUID= ' + str(DstUID) + ' DSTUID= ' + str(SrcUID) + ' SrcSeqNum ' + str(seqNum) + ' HOPCount 0 '
        self.Send(RREPmsg)
                    
                    
    def RoutingUpdate(self,SrcUID,fromUID,HopCount,SrcSeqNum):
        RUthread = threading.Thread(target=self.RoutingUpdatefunc , args = (SrcUID,fromUID,HopCount,SrcSeqNum,))
        RUthread.setDaemon(True)
        RUthread.start()
        RUthread.join()

        
        
    def RoutingUpdatefunc(self,SrcUID,fromUID,HopCount,SrcSeqNum):
        print ("\n Update " + str(self.UID))
        idx = UIDs.index(SrcUID)
        if self.RoutingTable[idx][3] < SrcSeqNum :
            self.RoutingTable[idx][0] = SrcUID
            self.RoutingTable[idx][1] = fromUID
            self.RoutingTable[idx][2] = HopCount
            self.RoutingTable[idx][3] = SrcSeqNum
            #self.RoutingTable[idx][4] = LifeTime
            self.RoutingTable[idx][5] = True

            
    
              

    def Send(self,msg):
        Sthread = threading.Thread(target=self.Sendfunc , args = (msg,))
        Sthread.setDaemon(True)
        Sthread.start()

        
        
    def Broadcast(self,msg,fromUID):
        Bthread = threading.Thread(target=self.Broadcastfunc , args = (msg,fromUID))
        Bthread.setDaemon(True)
        Bthread.start()


        
        
    def Broadcastfunc(self,msg,fromUID):
        
        ind = [i for i in range(len(self.DistanceTable)) if (self.DistanceTable[i]<self.diameter)and(self.DistanceTable[i]>0)and(fromUID!=V[i].UID)]        
        for i in ind :
            msg2send = []
            msg2send = msg + " nextHOP = " + str(UIDs[i]) 
            time.sleep(self.Delay)
            self.csocket.send(bytes(code(msg2send),'UTF-8'))
    
    
    
    def findNextHOP(self,SrcUID) :
        idx = UIDs.index(SrcUID)
        if self.RoutingTable[idx][5]:
            return self.RoutingTable[idx][1]
        else :
            self.RREQ(SrcUID)
            while self.RoutingTable[idx][5] == False :
                pass
            return self.RoutingTable[idx][1]
        

        
        
    def Sendfunc(self,msg):
        if msg[0:7] == 'Message':
            temp = [int(s) for s in msg.split() if s.isdigit()]
            DstUID = temp[1]
            msg = msg + " nextHOP = " + str(self.findNextHOP(DstUID))
            time.sleep(self.Delay)
            print ("\n Send " + str(self.UID) + " " + msg)
            self.csocket.sendall(bytes(code(msg),'UTF-8'))
        elif msg[0:4] == 'RREP' :
            temp = [int(s) for s in msg.split() if s.isdigit()]
            UID = temp[1]
            msg = msg + " nextHOP = " + str(self.findNextHOP(UID))
            time.sleep(self.Delay)
            print ("\n Send " + str(self.UID) + " " + msg)
            self.csocket.sendall(bytes(code(msg),'UTF-8'))
        else :
            time.sleep(self.Delay)
            print ("\n Send " + str(self.UID) + " " + msg)
            self.csocket.sendall(bytes(code(msg),'UTF-8'))
            
            
            
            
    def Listen(self):
        Rthread = threading.Thread(target=self.Receive)
        Rthread.setDaemon(True)
        Rthread.start()
        
    def init(self):
        initthread = threading.Thread(target=self.initialize)
        initthread.setDaemon(True)
        initthread.start()
        
    def initialize(self) :
        msg = "init " + str(self.UID) + " XLocation " + str(self.LocationX) + " YLocation " + str(self.LocationY)
        print ("\n Send " + str(self.UID) + " " + msg)
        self.csocket.sendall(bytes(code(msg) , 'UTF-8'))
    
    def RREQ(self,DstUID) :
        idx = UIDs.index(self.UID)
        self.RoutingTable[idx][3] += 1
        msg = 'RREQ : SRCUID= ' + str(self.UID) + ' DSTUID= ' + str(DstUID) + ' SrcSeqNum ' + str(self.RoutingTable[idx][3]) + ' HOPCount 0 '
        self.Broadcast(msg,0)
        
    def Hello(self):
        Hellothread = threading.Thread(target=self.SendHello)
        Hellothread.setDaemon(True)
        Hellothread.start()
        
    def SendHello(self) :
        msg = "Hello " + "SrcUID : "+ str(self.UID) + " XLoc " + str(self.LocationX) + " YLoc " + str(self.LocationY) 
        print ("\n Send " + str(self.UID) + " " + msg)
        self.csocket.sendall(bytes(code(msg), 'UTF-8'))
    

        
# Vehicle Creation
V = []
Delays = []
for i in range(N):
    temp = [int(s) for s in lines[i+7].split() if s.isdigit()]
    v = Vehicle(temp[1],temp[2],temp[0],temp[3],temp[4],r,temp[5])
    V.append(v)
    V[i].Listen()
    V[i].init()
    Delays.append(temp[5])


#Initialization time
Max_Delay = max(Delays)
time.sleep(2*Max_Delay)

#Completing Routing Tables
for i in range(N):
    print ("\n Update " + str(V[i].UID))
    V[i].DistanceTable[i] = 0
    for j in range(N):
        V[i].RoutingTable[j][3] = 0
        V[i].RoutingTable[j][0] = V[j].UID
        if V[i].DistanceTable[j] < V[i].diameter :
            V[i].RoutingTable[j][5] = True
            V[i].RoutingTable[j][1] = V[j].UID
        else:
            V[i].RoutingTable[j][5] = False


    
# Now the initialization phase in finished
# It's time for the scenario to begin

def ChangeLoc(uids,xs,ys):
    for i in range(N) :
        HelloReplyList[i] = False
    CNums = len(uids)
    for p in range(CNums):
        idx = UIDs.index(uids[p])
        V[idx].LocationX = xs[p]
        V[idx].LocationY = ys[p]
    for i in range(N):
        V[i].DistanceTable = [Max_Distance] * N
        V[i].RoutingTable[:][1:5] = [[] for x in range(5) for y in range(1)]
        for j in range(N):
            V[i].RoutingTable[j][5] = False
        V[i].Hello()
    q = [True]*N

    
    while HelloReplyList != q:
        pass
    
    for i in range(N):
        V[i].DistanceTable[i] = 0
        for j in range(N):
            V[i].RoutingTable[j][3] = 0
            V[i].RoutingTable[j][0] = V[j].UID
            if V[i].DistanceTable[j] < V[i].diameter :
                V[i].RoutingTable[j][5] = True
                V[i].RoutingTable[j][1] = V[j].UID
            else:
                V[i].RoutingTable[j][5] = False
    time.sleep(2*Max_Delay)
        
    
def SendMessage(SrcUID,DstUID,msg):
    msg = 'Message from ' + str(SrcUID) + ' to ' + str(DstUID) + ' ::' + msg + ':: '
    idx = UIDs.index(SrcUID)
    V[idx].Send(msg)

def Scenario(file):
    lines = [line.rstrip('\n').replace(".", "") for line in open(file)]
    lineNum = len(lines) - N -8
    for i in range(lineNum):
        m = lines[i+N + 8].replace('-', ' ')
        temp = [int(s) for s in m.split() if s.isdigit()]
        if lines[i+N+8][0] == 'C':
            CNum = int(len(temp)/3)
            uids = []
            xs = []
            ys = []
            for p in range(CNum):
                uids.append(temp[0+p*3])
                xs.append(temp[1+p*3])
                ys.append(temp[2+p*3])
            ChangeLoc(uids,xs,ys)
        elif lines[i+N+8][0] == 'S':
            s = [k for k in range(len(lines[i+N+8])) if lines[i+N+8][k] in "-"]
            msg = lines[i+N+8][s[0]+1:s[1]]
            SendMessage(temp[0],temp[1],msg)
        elif lines[i+N+8][0] == 'W':
            time.sleep(temp[0])
        else:
            pass
Scenariothread = threading.Thread(target= Scenario , args = (ScenarioFile,))
Scenariothread.setDaemon(True)
Scenariothread.start()
            

