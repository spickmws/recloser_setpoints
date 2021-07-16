from telnetlib import Telnet
from time import sleep
import socket
from csv import reader, writer
from datetime import datetime


class Recloser:
    """Contains protective device information for a recloser"""
    def __init__(self, fid, ip, group=9, phPU=1, phFC=1, phFTD=1, phSC=1, phSTD=1, gPU=1, gFC=1, gFTD=1, gSC=1, gSTD=1, model=1, ctr=1000):
        self.fid = fid
        self.ip = ip
        self.group = group
        self.phPU = phPU
        self.phFC = phFC
        self.phFTD = phFTD
        self.phSC = phSC
        self.phSTD = phSTD
        self.gPU = gPU
        self.gFC = gFC
        self.gFTD = gFTD
        self.gSC = gSC
        self.gSTD = gSTD
        self.model = model
        self.TIMEOUT = 5
        self.WAIT = 1
        self.setpoints = ""
        with open("PASSWORD", "r") as file:
            self.password = file.read()
        
    def connect_recloser(self):
        """Connects to a recloser"""
        try:
            self.tn = Telnet(host=self.ip, port=1700, timeout=self.TIMEOUT)
        except socket.timeout:
            print(self.ip + " Timed Out\n")
            with open("logs\\connection_errors.txt", "a") as file:
                file.write(self.fid + "," + self.ip + ", Timed out\r")
                return 1
        except socket.gaierror:
            print(self.ip + " Socket Error\n")
            with open("logs\\connection_errors.txt", "a") as file:
                file.write(self.fid + "," + self.ip + ", Socket Error\r")
                return 1
        except ConnectionRefusedError:
            print(self.ip + " Refused connection\n")
            with open("logs\\connection_errors.txt", "a") as file:
                file.write(self.fid + "," + self.ip + ", Refused connection\r")
                return 1
            
        print("Connected to " + self.fid + " " + self.ip)
        return 0
        
    
    def close_connection(self):
        """Closes TELNET connection to recloser"""
        try:
            self.tn.close()

        except:
            print("Problem closing connection to " + self.fid + " " + self.ip)
            
            
    def retrieve_model(self):
        """Retrieves model number of the recloser"""
        self.tn.write(b"ID" + b"\r\n")
        sleep(self.WAIT)
        try:
            output = self.tn.read_very_eager().decode('ascii')
        except ConnectionResetError:
            print("Recloser refused connection. Logged in to many times in a row")
            self.tn.close()
        try:
            self.model = output.split("SEL-")[1].split("-")[0]
        except:
            print("Connection unavailable, likely a Form 6\n")
            self.tn.close()
        if self.model == "651R":
            print("Model: " + self.model, end=" ")
            return 0
        elif self.model == "351R":
            print("Model: " + self.model, end=" ")
            return 0
        elif self.model == "351RS":
            print("Model: " + self.model, end=" ")
            return 0
        else:
            return 1
            
            
    def login(self):
        """Logs into a recloser using the password contained in PASSWORD"""
        try:
            self.tn.write(b"ACC" + b"\r\n")
            sleep(self.WAIT)
            self.tn.write(self.password.encode('ascii') + b"\r\n")
            sleep(self.WAIT)
            return 0
        except AttributeError:
            with open("logs\\connection_errors.txt", "a") as file:
                file.write(self.fid + "," + self.ip + ", NoneType\r")
                return 1
            
    
    def retrieve_group(self):
        """Retrieves the group number of the recloser"""
        try:
            self.tn.write(b"GRO" + b"\r\n")
            sleep(self.WAIT)
            output = self.tn.read_very_eager().decode('ascii')
            self.group = int((output.split("Active Group = ")[1].split("=>")[0])[0])
            if self.group > 0 and self.group < 9:
                print("Group: " + str(self.group))
                return 0
            else:
                print("Group number is nonsensicle")
                return 1
        except:
            print("Unable to obtain group number\n")
            self.group = 99
            return 1
    
    
    def retrieve_setpoints(self):
        """Retrieves the setpoints for the recloser"""
        
        if self.model == "651R":
            self.tn.write(b"SHO " + str(self.group).encode('ascii') + b"\r\n")
            sleep(self.WAIT * 2)
            self.setpoints = self.tn.read_very_eager().decode('ascii')
            file_name = "setpoints\\RECL " + self.fid + ".txt"
            with open(file_name, "w") as file:
                file.write(self.setpoints)
                
        if self.model == "351R":
            self.tn.write(b"SHO " + str(self.group).encode('ascii') + b"\r\n")
            sleep(self.WAIT * 4)
            self.tn.write(b"\r\n")
            sleep(self.WAIT * 4)
            self.tn.write(b"\r\n")
            sleep(self.WAIT * 4)
            self.setpoints = self.tn.read_very_eager().decode('ascii')
            file_name = "setpoints\\RECL " + self.fid + ".txt"
            with open(file_name, "w") as file:
                file.write(self.setpoints)
                
        if self.model == "351RS":
            self.tn.write(b"SHO " + str(self.group).encode('ascii') + b"\r\n")
            sleep(self.WAIT * 4)
            self.tn.write(b"\r\n")
            sleep(self.WAIT * 4)
            self.tn.write(b"\r\n")
            sleep(self.WAIT * 4)
            self.setpoints = self.tn.read_very_eager().decode('ascii')
            file_name = "setpoints\\RECL " + self.fid + ".txt"
            with open(file_name, "w") as file:
                file.write(self.setpoints)
            
            
    def parse_ctr(self):
        """Parses the CTR for the recloser"""
        
        if self.model == "651R":
            try:
                self.ctr = int(float(self.setpoints.split("CTR")[1].split(":=")[1].strip()))
                return 0
            except:
                print("CTR Parsing Error")
                self.ctr = 999999
                with open("logs\\connection_errors.txt", "a") as file:
                    file.write(self.fid + "," + self.ip + ", No CTR\r")
                return 1
            
        if self.model == "351R":
            try:
                self.ctr = int(float(self.setpoints.split("CTR")[1].split("=")[1].strip()))
                return 0
            except:
                print("CTR Parsing Error")
                self.ctr = 999999
                with open("logs\\connection_errors.txt", "a") as file:
                    file.write(self.fid + "," + self.ip + ", No CTR\r")
                return 1
            
        if self.model == "351RS":
            try:
                self.ctr = int(float(self.setpoints.split("CTR")[1].split("=")[1].split("PTR")[0].strip()))
                return 0
            except:
                print("CTR Parsing Error")
                self.ctr = 999999
                with open("logs\\connection_errors.txt", "a") as file:
                    file.write(self.fid + "," + self.ip + ", No CTR\r")
                return 1
            
            
# PHASE PHASE PHASE PHASE PHASE PHASE PHASE PHASE PHASE PHASE PHASE PHASE PHASE PHASE PHASE PHASE PHASE PHASE PHASE PHASE


    def parse_phPU(self) -> int:
        """Parses the setpoints to find phase PU"""
        
        if self.model == "651R":
            try:
                self.phPU = self.setpoints.split("51PJP")[1].split(":=")[1].split("51PJC")[0].strip()
                print("Phase: " + str(float(self.phPU) * self.ctr), end=' ')
                return 0
            except:
                print("Could not obtain phase pickup")
                return 1
            
        elif self.model == "351R":
            try:
                self.phPU = self.setpoints.split("51P1P =")[1].split("51P1C")[0].strip()
                print("Phase: " + str(float(self.phPU) * self.ctr), end=' ')
                return 0
            except:
                print("Could not obtain phase pickup")
                return 1
            
        elif self.model == "351RS":
            try:
                self.phPU = self.setpoints.split("51P1P")[1].split("=")[1].split("51P1C")[0].strip()
                print("Phase: " + str(float(self.phPU) * self.ctr), end=' ')
                return 0
            except:
                print("Could not obtain phase pickup")
                return 1
            
            
    def parse_phFC(self) -> int:
        """Parses the setpoints to find phase fast curve"""
        
        if self.model == "651R":
            try:
                self.phFC = self.setpoints.split("51PJC")[1].split(":=")[1].split("51PJTD")[0].strip()
                print(self.phFC, end=' ')
                return 0
            except:
                print("Could not obtain phase fast curve")
                return 1
        elif self.model == "351R":
            try:
                self.phFC = self.setpoints.split("51P1C =")[1].split("51P1TD=")[0].strip()
                print(self.phFC, end=' ')
                return 0
            except:
                print("Could not obtain phase fast curve")
                return 1
            
        elif self.model == "351RS":
            try:
                self.phFC = self.setpoints.split("51P1C")[1].split("=")[1].split("51P1TD")[0].strip()
                print(self.phFC, end=' ')
                return 0
            except:
                print("Could not obtain phase fast curve")
                return 1
    
    
    def parse_phFTD(self) -> int:
        """Parses the setpoints to find phase fast curve time dial"""
        
        if self.model == "651R":
            try:
                self.phFTD = self.setpoints.split("51PJTD")[1].split(":=")[1].split("51PJCT")[0].strip()
                try: 
                    self.phFTD = self.phFTD.split("51PJRS")[0].strip()
                    print(self.phFTD, end=' ')
                    return 0
                except:
                    print(self.phFTD, end=' ')
                    return 0
            except:
                print("Could not obtain phase fast time dial")
                return 1
            
        elif self.model == "351R":
            try:
                self.phFTD = self.setpoints.split("51P1TD=")[1].split("51P1CT")[0].strip()
                print(self.phFTD, end=' ')
                return 0
            except:
                print("Could not obtain phase fast time dial")
                return 1
            
        elif self.model == "351RS":
            try:
                self.phFTD = self.setpoints.split("51P1TD")[1].split("=")[1].split("51P1CT")[0].strip()
                print(self.phFTD, end=' ')
                return 0
            except:
                print("Could not obtain phase fast time dial")
                return 1
            
            
    def parse_phSC(self) -> int:
        """Parses the setpoints to find phase slow curve"""
        
        if self.model == "651R":
            try:
                self.phSC = self.setpoints.split("51PKC")[1].split(":=")[1].split("51PKTD")[0].strip()
                print(self.phSC, end=' ')
                return 0
            except:
                print("Could not obtain phase slow curve")
                return 1
            
        elif self.model == "351R":
            try:
                self.phSC = self.setpoints.split("51P2C =")[1].split("51P2TD")[0].strip()
                print(self.phSC, end=' ')
                return 0
            except:
                print("Could not obtain phase slow curve")
                return 1
            
        elif self.model == "351RS":
            try:
                self.phSC = self.setpoints.split("51P2C")[1].split("=")[1].split("51P2TD")[0].strip()
                print(self.phSC, end=' ')
                return 0
            except:
                print("Could not obtain phase slow curve")
                return 1
            
            
    def parse_phSTD(self) -> int:
        """Parses the setpoints to find phase slow curve time dial"""
        
        if self.model == "651R":
            try:
                self.phSTD = self.setpoints.split("51PKTD")[1].split(":=")[1].split("51PKRS")[0].strip()
                try:
                    self.phSTD = self.phSTD.split("51PKCT")[0].strip()
                    print(self.phSTD)
                    return 0
                except:
                    print(self.phSTD)
                    return 0
            except:
                print("Could not obtain slow curve time dial")
                return 1
            
        elif self.model == "351R":
            try:
                self.phSTD = self.setpoints.split("51P2TD=")[1].split("51P2CT=")[0].strip()
                try:
                    self.phSTD = self.phSTD.split("51P2RS")[0].strip()
                    print(self.phSTD)
                    return 0
                except:
                    print(self.phSTD)
                    return 0
            except:
                print("Could not obtain slow curve time dial")
                return 1
            
        elif self.model == "351RS":
            try:
                self.phSTD = self.setpoints.split("51P2TD")[1].split("=")[1].split("51P2RS")[0].strip()
                try:
                    self.phSTD = self.phSTD.split("51P2RS")[0].strip()
                    print(self.phSTD + "\n")
                    return 0
                except:
                    print(self.phSTD)
                    return 0
            except:
                print("Could not obtain slow curve time dial")
                return 1
        

# GROUND GROUND GROUND GROUND GROUND GROUND GROUND GROUND GROUND GROUND GROUND GROUND GROUND GROUND GROUND GROUND

    def parse_gPU(self) -> int:
        """Parses the setpoints to find ground pickup"""
        
        if self.model == "651R":
            try:
                self.gPU = self.setpoints.split("51G1JP")[1].split(":=")[1].split("51G1JC")[0].strip()
                print("Ground: " + str(float(self.gPU) * self.ctr), end=' ')
                return 0
            except:
                print("Could not obtain ground pickup")
                return 1
            
        elif self.model == "351R":
            try:
                self.gPU = self.setpoints.split("51G1P =")[1].split("51G1C")[0].strip()
                print("Ground: " + str(float(self.gPU) * self.ctr), end=' ')
                return 0
            except:
                print("Could not obtain ground pickup")
                return 1
            
        elif self.model == "351RS":
            try:
                self.gPU = self.phPU
                return 0
            except:
                print("Could not obtain ground pickup")
                return 1
            
            
    def parse_gFC(self) -> int:
        """Parses the setpoints to find ground fast curve"""
        
        if self.model == "651R":
            try:
                self.gFC = self.setpoints.split("51G1JC")[1].split(":=")[1].split("51G1JTD")[0].strip()
                print(self.gFC, end=' ')
                return 0
            except:
                print("Could not obtain ground fast curve")
                return 1
            
        elif self.model == "351R":
            try:
                self.gFC = self.setpoints.split("51G1C =")[1].split("51G1TD=")[0].strip()
                print(self.gFC, end=' ')
                return 0
            except:
                print("Could not obtain ground fast curve")
                return 1
            
        elif self.model == "351RS":
            try:
                self.gFC = self.phFC
                return 0
            except:
                print("Could not obtain ground fast curve")
                return 1
    
    
    def parse_gFTD(self) -> int:
        """Parses the setpoints to find ground fast curve time dial"""
        
        if self.model == "651R":
            try:
                self.gFTD = self.setpoints.split("51G1JTD")[1].split(":=")[1].split("51G1JCT")[0].strip()
                try:
                    self.gFTD = self.gFTD.split("51G1JRS")[0].strip()
                    print(self.gFTD, end=' ')
                    return 0
                except:
                    print(self.gFTD, end=' ')
                    return 0
            except:
                print("Could not obtain ground fast time dial")
                return 1
            
        elif self.model == "351R":
            try:
                self.gFTD = self.setpoints.split("51G1TD=")[1].split("51G1CT=")[0].strip()
                print(self.gFTD, end=' ')
                return 0
            except:
                print("Could not obtain ground fast time dial")
                return 1
            
        elif self.model == "351RS":
            try:
                self.gFTD = self.phFTD
                return 0
            except:
                print("Could not obtain ground fast time dial")
                return 1            
            
            
    def parse_gSC(self) -> int:
        """Parses the setpoints to find ground slow curve"""
        
        if self.model == "651R":
            try:
                self.gSC = self.setpoints.split("51G1KC")[1].split(":=")[1].split("51G1KTD")[0].strip()
                print(self.gSC, end=' ')
                return 0
            except:
                print("Could not obtain ground slow curve")
                return 1
            
        elif self.model == "351R":
            try:
                self.gSC = self.setpoints.split("51G2C =")[1].split("51G2TD=")[0].strip()
                print(self.gSC, end=' ')
                return 0
            except:
                print("Could not obtain ground slow curve")
                return 1
            
        elif self.model == "351RS":
            try:
                self.gSC = self.phSC
                return 0
            except:
                print("Could not obtain ground slow curve")
                return 1
            
    def parse_gSTD(self) -> int:
        """Parses the setpoints to find ground slow curve time dial"""
        
        if self.model == "651R":
            try:
                self.gSTD = self.setpoints.split("51G1KTD")[1].split(":=")[1].split("51G1KRS")[0].strip()
                try:
                    self.gSTD = self.gSTD.split("51G1KCT")[0].strip()
                    print(self.gSTD + "\n")
                    return 0
                except:
                    print(self.gSTD + "\n")
                    return 0
            except:
                print("Could not obtain ground slow time dial\n")
                return 1
            
        elif self.model == "351R":
            try:
                self.gSTD = self.setpoints.split("51G2TD=")[1].split("51G2CT=")[0].strip()
                try:
                    self.gSTD = self.gSTD.split("51G2RS")[0]
                    print(self.gSTD + "\n")
                    return 0
                except:
                    print(self.gSTD + "\n")
                    return 0
            except:
                print("Could not obtain ground slow time dial\n")
                return 1

        elif self.model == "351RS":
            try:
                self.gSTD = self.phSTD
                return 0
            except:
                print("Could not obtain ground slow time dial\n")
                return 1            
            
    def parse_all_settings(self) -> int:
        """ This function calls the individual parsers"""
        self.parse_ctr()
        self.parse_phPU()
        self.parse_phFC()
        self.parse_phFTD()
        self.parse_phSC()
        self.parse_phSTD()
        self.parse_gPU()
        self.parse_gFC()
        self.parse_gFTD()
        self.parse_gSC()
        self.parse_gSTD()


with open("ip_list.csv", "r") as file:
    
    # Creating a current time stamp
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d") + " " + now.strftime("%H") + ":" + now.strftime("%M")
    
    # Clears connection report
    with open("logs\\connection_errors.txt", "w") as file:
        file.write("")
    
    # Determines the lenght of the IP list
    ip_list_length = 0
    with open("ip_list.csv", "r") as file:
        csv_reader = reader(file)
        for row in csv_reader:
            ip_list_length += 1
    
    # Iterates through the reclosers on the list
    current_recloser_number = 0
    with open("ip_list.csv", "r") as file:
        
        csv_reader = reader(file)
        
        # Iterates through reclosers
        for row in csv_reader:
            
            # Prints recloser X of Y
            current_recloser_number += 1
            print("Recloser " + str(current_recloser_number) + " of " + str(ip_list_length))
            
            recloser = Recloser(ip=row[1], fid=row[0])
            if recloser.connect_recloser() == 0:
                
                # Connecting and retrieving required information
                recloser.retrieve_model()
                if recloser.login() == 0:
                    if recloser.retrieve_group() == 0:
                        recloser.retrieve_setpoints()
                        recloser.close_connection()
                        
                        # Parsing the information that was gathered
                        recloser.parse_all_settings()
                        
                        # Incrementally updates the output file
                        recloser_output = [recloser.fid, recloser.model, recloser.ip, recloser.group, recloser.ctr, recloser.phPU, recloser.phFC, recloser.phFTD, recloser.phSC, recloser.phSTD, recloser.gPU, recloser.gFC, recloser.gFTD, recloser.gSC, recloser.gSTD, timestamp]
                        output_file_name = "output_" + timestamp.replace(" ","-").replace(":","") + ".csv"
                        with open(output_file_name, "a", newline='') as file:
                            write = writer(file)
                            write.writerow(recloser_output)



