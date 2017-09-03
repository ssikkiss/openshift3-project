#!/usr/bin/env python3

import os,socket, time, bitcoin,struct,binascii,shelve
from contextlib import closing
from messages import *
from bitcoin.net import *
from bitcoin.bloom import *
from io import BytesIO 

PORT = 8333
VERSION=70012

bitcoin.SelectParams('mainnet')

SFILE='servers.db'
HFILE='headers.db'


class node():
    def __init__(self,version=VERSION):
        self.version=version
        self.msgstart=b'\xf9\xbe\xb4\xd9'
        self.servers=[]
        with closing(shelve.open(SFILE)) as serversdb:
            for k in serversdb.keys():
                self.servers.append(serversdb[k])
        if len(self.servers)==0:
            self.servers=[
                ('bitcoin.sipa.be',PORT),
                ('138.201.55.219',PORT),
                ('47.89.38.110',PORT),
                ('114.55.228.40',PORT),
                ('101.201.142.252',PORT),
                ('136.243.139.96',PORT),
                ('120.76.191.81',PORT)
            ]
        self.addrs=[]
        with closing(shelve.open(HFILE)) as hdb:
            if 'topblockhash' in hdb:
                self.tophash=hdb['topblockhash']
                self.height = hdb['blockheight']
            else:
                self.height = 0
                self.tophash = '00'*32
        self.oldhash=self.tophash
        self.recvbuf=b''
        self.server_nStartingHeight=-1

    def connect(self):
        while  len(self.servers)>0:
            server=self.servers[0]
            self.servers=self.servers[1:]
            sock=socket.socket()
            sock.settimeout(5)
            try:
                sock.connect(server)
            except:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                    sock.close()
                except:
                    pass
                return
            else:
                msg=msg_version(self.version)
                rserver=sock.getpeername()
                msg.addrTo.ip = rserver[0]
                msg.addrTo.port = rserver[1]
                client=sock.getsockname()
                msg.addrFrom.ip = client[0]
                msg.addrFrom.port = client[1]
                msg.nServices = 0
                msg.nStartingHeight=self.height
                body=msg.to_bytes()
                try:
                    sock.sendall(body)
                except:
                    print('error')
                    try:
                        sock.shutdown(socket.SHUT_RDWR)
                        sock.close()
                    except:
                        pass
                else:
                    print('connect successful')
                    return sock
        return
    


            

    def recvmsg(self,sock):
        if len(self.recvbuf)<24:
            try:
                r=sock.recv(4096)
                if len(r)<=0:
                    print('err1 in recv msg')
                    return
                else:
                    self.recvbuf+=r
            except:
                print('err in recv msg')
                return
        msgstart=self.recvbuf[:4]
        if msgstart!=self.msgstart:
            print('msg header error')
            return
        command = self.recvbuf[4:16].split(b"\x00", 1)[0]
        msglen = struct.unpack(b"<i", self.recvbuf[16:20])[0]
        checksum = self.recvbuf[20:24]
        while len(self.recvbuf) < 24 + msglen:
            try:
                r=sock.recv(4096)
                if len(r)<=0:
                    print('msg err')
                    return
                else:
                    self.recvbuf+=r
            except:
                print('err2 in recv msg')
                return
        msg=self.recvbuf[24:msglen+24]
        h=bitcoin.core.Hash(msg)
        if checksum!=h[:4]:
            print('msg hash err,in recv msg')
            return
        self.recvbuf=self.recvbuf[msglen+24:]
        if command in messagemap:
            cls = messagemap[command]
            return cls.msg_deser(BytesIO(msg))
        else:
            print("Command '%s' not in messagemap" % repr(command))
            return
    def sendmsg(self,msg,sock):
        if not msg:
            print('msg is none')
            return
        print('send '+str(msg.command))
        body=msg.to_bytes()
        try:
            sock.sendall(body)
        except:
            print('err in send msg')
            return
        return True
    def saveheaders(self,headers):
        with closing(shelve.open(HFILE)) as hdb:
            count=0
            writecount=0
            while count<len(headers):
                bhash=headers[count].GetHash()
                self.tophash=bitcoin.core.b2lx(bhash)
                if self.tophash in hdb:
                    pass
                else:
                    self.height+=1
                    writecount+=1
                    t=headers[count]
                    
                    hdb[self.tophash]={'height':self.height,'nVersion':t.nVersion,'hashPrevBlock':t.hashPrevBlock,'hashMerkleRoot':t.hashMerkleRoot,'nTime':t.nTime,'nBits':t.nBits,'nNonce':t.nNonce}
                    hdb['blockheight']=self.height
                    hdb['topblockhash']=self.tophash
                count+=1
            print('wrote '+str(writecount)+' header into headers.db :')

    def saveservers(self,addrs):
        servers=[]
        for addr in addrs:
            s=(addr.ip,addr.port)
            sock=socket.socket()
            try:
                t=time.time()
                sock.settimeout(0.2)
                sock.connect(s)
                t=time.time()-t
                servers.append((s,t))
            except:
                pass
            sock.close()
        zlist=sorted(servers,key=lambda x:x[1])
        count=0
        self.servers=[]
        with closing(shelve.open(SFILE)) as serversdb:
            for s in zlist:
                print(s)
                self.servers.append(s[0])
                serversdb[str(count)]=s[0]
                count+=1
                if count>30:
                    break

    def work(self,runtime):
        print('-----------  work -----------')
        ret='<ul>-------- work() --------'
        sock=self.connect()
        if not sock:
            print('err in work:no socket')
            print('----------   end  -----------')
            ret+='<li>err: no socket'
            ret+='</li>-------- end ---------</li></ul>'
            try:
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
            except:
                pass
            return ret
        ret+='</li><li>connected server:'+repr(sock.getpeername())
        
        bhash=bitcoin.core.lx(self.tophash)
        shash=None
        addrflag=True
        ackflag=False
        endtime=time.time()+runtime
        while time.time()<endtime:
            msg=self.recvmsg(sock)
            if not msg:
                print('err in work:no msg')
                ret+='</li><li>err:no msg'
                if  ackflag:
                    time.sleep(1)
                    ret+='</li><li>sleep 1 sec'
                    continue
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                    sock.close()
                except:
                    pass
                sock=self.connect()
                if sock:
                    print('change server')
                    ret+='</li><li>connected server:'+repr(sock.getpeername())
                    ackflag=False
                    continue
                else:
                    print('no connect,exit')
                    ret+='</li><li>err:no connect'
                    break
            ret+='</li><li>recv  '+str(msg.command)
            if msg.command==b'version':
                self.server_nStartingHeight=msg.nStartingHeight
                print('recv version')
                retmsg=msg_verack(self.version)
            elif msg.command==b'verack':
                print('recv verack')
                ackflag=True
                retmsg=msg_filterload(self.version)
                bloomfilter=CBloomFilter(2,0.001,0,CBloomFilter.UPDATE_ALL)
                pubkey = bitcoin.core.x('045B81F0017E2091E2EDCD5EECF10D5BDD120A5514CB3EE65B8447EC18BFC4575C6D5BF415E54E03B1067934A0F0BA76B01C6B9AB227142EE1D543764B69D901E0')
                pubkeyhash = bitcoin.core.Hash160(pubkey)
                bloomfilter.insert(pubkey)
                bloomfilter.insert(pubkeyhash)
                retmsg.bloomfilter=bloomfilter

                #retmsg=msg_getheaders(self.version)
                #retmsg.locator.vHave.append(bhash)
                    
            elif msg.command==b'ping':
                print('recv ping')
                retmsg=msg_pong(self.version)
            elif msg.command==b'pong':
                print('recv pong')
            elif msg.command==b'alert':
                print('recv alert')

            elif msg.command==b'sendheaders':
                print('recv sendheaders')
                retmsg=msg_getheaders(self.version)
                retmsg.locator.vHave.append(bhash)
            elif msg.command==b'inv':
                print('recv inv')
                print(msg)
                ret+='</li><li>'+repr(msg)
                if len(self.servers)<10 and addrflag:
                    retmsg=msg_getaddr(self.version)
                    addrflag=False
                else:
                    #retmsg=msg_getdata(self.version)
                    pass
                    
                    
            elif msg.command==b'addr':
                print('recv addr')
                if len(msg.addrs)>1:
                   self.saveservers(msg.addrs)
                   pass
            elif msg.command==b'getaddr':
                print('recv getaddr')
                retmsg=msg_addr(self.version)
                
            elif msg.command==b'headers':
                print('recv headers')
                h=msg.headers
                self.saveheaders(h)
                if self.server_nStartingHeight>self.height:
                    bhash=h[len(h)-1].GetHash()
                    if shash!=bhash:
                        shash=bhash
                        retmsg=msg_getheaders(self.version)
                        retmsg.locator.vHave.append(bhash)


            else:
                print('recv ' +str(msg.command))
                break
            if retmsg:
                ret+='</li><li>send  '+str(retmsg.command)
                self.sendmsg(retmsg,sock)
                retmsg=None
        try:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        except:
            pass
        print('----------   end  -----------')
        ret+='</li>-------- end ---------</li></ul>'
        return ret



def showheader(hdb,strhash):
    ret='----------'
    if strhash in hdb:
        ret+='<li>found '+strhash
        t=hdb[strhash]
        s=t['height']
        ret+='</li><li>height: '+str(s)
        s=t['nVersion']
        ret+='</li><li>nVersion: '+str(s)
        s=t['hashPrevBlock']
        ret+='</li><li>hashPrevBlock:<br>'+bitcoin.core.b2lx(s)
        s=t['hashMerkleRoot']
        ret+='</li><li>hashMerkleRoot:<br>'+bitcoin.core.b2lx(s)
        s=t['nTime']
        ret+='</li><li>nTime: '+str(s)
        s=t['nBits']
        ret+='</li><li>nBits: '+str(s)
        s=t['nNonce']
        ret+='</li><li>nNonce: '+str(s)
    else:
        ret='</li><li>not found:'+strhash+'</li>'
    return ret

def search():
    ret='<ul>-------search-------'
    with closing(shelve.open(HFILE)) as hdb:
        if 'blockheight'  not in hdb:
            ret+='<li>headers.db file is empty</li>'
            return ret
        if hdb['blockheight']==0:
            ret+='<li>headers.db file is empty</li>'
            return ret
        ret+='<li>height:'+str(hdb['blockheight'])
        ret+='</li><li>tophash:'
        ret+=hdb['topblockhash']

        h478711 ='0000000000000000003702a4567b1329ffbcc1f89dcc9d620b8fb0da4b4f5228'
        h478717='000000000000000000e7e30d8455dffab92aaa9dddbc27426409258e9cc94581'
        h303552='000000000000000011ee234c0f25b64c07a9a74ec33000f67530bdae5ded953a'
        ret+=showheader(hdb,h303552)
        ret+=showheader(hdb,hdb['topblockhash'])
        ret+='</ul>'

        return ret





if __name__=='__main__':

    n=node()
    n.work()
    print(search())

