from machine import UART, Pin
import time
import ure

uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
uart1 = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9), timeout=100)
end_cmd = b'\xFF\xFF\xFF'

while True:
    if uart1.any():
        ser_bytes = uart1.readline();
        # Debug output
        # print('DEBUG: '+ser_bytes.decode("utf8"))
        # Read UpConverter Values
        if ser_bytes.decode("utf8")[0:3] == 'UPC':
            # Read Temperature (00)
            if ser_bytes.decode("utf8")[7:9] == '00':
                #print('Temp: '+ser_bytes.decode("utf8")[10:12]+'°C')
                txData = b't2.txt="'+ser_bytes.decode("utf8")[10:12]+'°C"'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read Voltage (01)
            elif ser_bytes.decode("utf8")[7:9] == '01':
                #print('Voltage: '+ser_bytes.decode("utf8")[10:11]+'.'+ser_bytes.decode("utf8")[11:14]+'V')
                txData = b't4.txt="'+ser_bytes.decode("utf8")[10:11]+'.'+ser_bytes.decode("utf8")[11:14]+'V"'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read forward power (02)
            elif ser_bytes.decode("utf8")[7:9] == '02':
                print('FWD power: '+ser_bytes.decode("utf8")[10:12]+' / '+ser_bytes.decode("utf8")[13:15]+'dBm')
            # Read PTT state (06)
            elif ser_bytes.decode("utf8")[7:9] == '06':
                if ser_bytes.decode("utf8")[10:11] == '1':
                    #print('PTT state: ON')
                    txData = b'p1.pic=2'
                    uart0.write(txData)
                    uart0.write(end_cmd)
                else:
                    #print('PTT state: OFF')
                    txData = b'p1.pic=1'
                    uart0.write(txData)
                    uart0.write(end_cmd)
            # Print unknown sentences
            else:
                print(ser_bytes.decode("utf8"))
        
        # Read DownConverter Values
        elif ser_bytes.decode("utf8")[0:3] == 'OLD':
            # Read GPS time
            if ser_bytes.decode("utf8")[4:9] == '00 01':
                #print ('GPS Time: '+ser_bytes.decode("utf8")[10:18])
                txData = b't6.txt="'+ser_bytes.decode("utf8")[10:18]+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read GPS SAT count
            elif ser_bytes.decode("utf8")[4:9] == '56 05':
                #print ('SATs: '+ser_bytes.decode("utf8")[10:11])
                txData = b't7.txt="SATs: '+ser_bytes.decode("utf8")[10:11]+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read Maidenhead grid
            elif ser_bytes.decode("utf8")[4:9] == '72 01':
                #print ('Grid: '+ser_bytes.decode("utf8")[10:16])
                txData = b't8.txt="'+ser_bytes.decode("utf8")[10:16]+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read Latitude
            elif ser_bytes.decode("utf8")[4:9] == '48 06':
                #print ('Lat: '+ser_bytes.decode("utf8")[10:20])
                txData = b't9.txt="'+ser_bytes.decode("utf8")[10:12]+'° '+ser_bytes.decode("utf8")[13:18]+' '+ser_bytes.decode("utf8")[18:20]+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read Longitude
            elif ser_bytes.decode("utf8")[4:9] == '40 07':
                #print ('Lon: '+ser_bytes.decode("utf8")[10:20])
                txData = b't10.txt="'+ser_bytes.decode("utf8")[10:13]+'° '+ser_bytes.decode("utf8")[14:19]+' '+ser_bytes.decode("utf8")[19:21]+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Print unknown sentences
            else:
                print(ser_bytes.decode("utf8"))
        else:
            print('Unknown sentence received')
            print(ser_bytes.decode("utf8"))
            
            #txData = b't0.txt="TEST: '+ser_bytes.decode("utf8")+'"'
            #uart0.write(txData)
            #uart0.write(end_cmd)
