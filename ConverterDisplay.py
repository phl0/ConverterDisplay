from machine import UART, Pin
import time
import ure

uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
uart1 = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9), timeout=100)
end_cmd = b'\xFF\xFF\xFF'
act_led = Pin(3, Pin.OUT)
ptt_led = Pin(2, Pin.OUT)
debug=0

#txData = b'page 1'
#uart0.write(txData)
#uart0.write(end_cmd)
tx_lo=''
tx_if=''
rx_if_1=''
rx_if_2=''
lnb_ref_1=''
lnb_ref_2=''
config_written=0

while True:
    if uart1.any():
        act_led.value(1)
        ser_bytes = uart1.readline();
        # Debug output
        if debug==1:
            txData = b't01.txt+="\r'+ser_bytes.decode("utf8")+'"'
            uart0.write(txData)
            uart0.write(end_cmd)
            print('DEBUG: '+ser_bytes.decode("utf8"))
        # Read UpConverter Values
        if ser_bytes.decode("utf8")[0:3] == 'UPC':
            # Read Temperature (00)
            if ser_bytes.decode("utf8")[7:9] == '00':
                #print('Temp: '+ser_bytes.decode("utf8")[10:12]+'°C')
                txData = b't3.txt="'+ser_bytes.decode("utf8")[10:12]+'°C "'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read Voltage (01)
            #elif ser_bytes.decode("utf8")[7:9] == '01':
                #print('Voltage: '+ser_bytes.decode("utf8")[10:11]+'.'+ser_bytes.decode("utf8")[11:14]+'V')
                #txData = b't4.txt="'+ser_bytes.decode("utf8")[10:11]+'.'+ser_bytes.decode("utf8")[11:14]+'V"'
                #uart0.write(txData)
                #uart0.write(end_cmd)
            # Read forward power (02)
            elif ser_bytes.decode("utf8")[7:9] == '02':
                #print('FWD power: '+ser_bytes.decode("utf8")[10:12]+' / '+ser_bytes.decode("utf8")[13:15]+'dBm')
                txData = b't20.txt="'+ser_bytes.decode("utf8")[13:15]+'dBm "'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read reflected power (03)
            elif ser_bytes.decode("utf8")[7:9] == '03':
                #print('REF power: '+ser_bytes.decode("utf8")[10:12]+' / '+ser_bytes.decode("utf8")[13:15]+'dBm')
                txData = b't21.txt="'+ser_bytes.decode("utf8")[13:15]+'dBm "'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read LO frequency (05)
            elif ser_bytes.decode("utf8")[7:9] == '05':
                if tx_lo == '':
                    print('LO: '+ser_bytes.decode("utf8")[10:14]+' MHz')
                    tx_lo = ser_bytes.decode("utf8")[10:14]
            # Read PTT state (06)
            elif ser_bytes.decode("utf8")[7:9] == '06':
                if ser_bytes.decode("utf8")[10:11] == '1':
                    #print('PTT state: ON')
                    ptt_led.value(1)
                    txData = b'page 2'
                    #txData = b'p1.pic=2'
                    uart0.write(txData)
                    uart0.write(end_cmd)
                else:
                    #print('PTT state: OFF')
                    ptt_led.value(0)
                    txData = b'page 1'
                    #txData = b'p1.pic=1'
                    uart0.write(txData)
                    uart0.write(end_cmd)
            # Read version string (07)
            elif ser_bytes.decode("utf8")[7:9] == '07':
                print('Ver: '+ser_bytes.decode("utf8")[10:-5])
            # Read IF frequency (10)
            elif ser_bytes.decode("utf8")[7:9] == '10':
                if tx_if == '':
                    print('IF: '+ser_bytes.decode("utf8")[10:-5]+' MHz')
                    tx_if = ser_bytes.decode("utf8")[10:-5]
            # Print unknown sentences
            else:
                if debug==1:
                    print(ser_bytes.decode("utf8"))
        
        # Read DownConverter Values
        elif ser_bytes.decode("utf8")[0:3] == 'OLD':
            # Read GPS time
            if ser_bytes.decode("utf8")[4:9] == '00 01':
                #print ('GPS Time: '+ser_bytes.decode("utf8")[10:18])
                txData = b't1.txt="'+ser_bytes.decode("utf8")[10:18]+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read GPS SAT count
            elif ser_bytes.decode("utf8")[4:9] == '56 05':
                #print ('SATs: '+ser_bytes.decode("utf8")[10:11])
                txData = b't2.txt="'+ser_bytes.decode("utf8")[10:11]+' "'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read Maidenhead grid
            elif ser_bytes.decode("utf8")[4:9] == '72 01':
                #print ('Grid: '+ser_bytes.decode("utf8")[10:16])
                txData = b't0.txt="'+ser_bytes.decode("utf8")[10:14]+ser_bytes.decode("utf8")[14:16].lower()+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read Latitude
            elif ser_bytes.decode("utf8")[4:9] == '48 06':
                #print ('Lat: '+ser_bytes.decode("utf8")[10:20])
                txData = b't10.txt="'+ser_bytes.decode("utf8")[10:12]+'° '+ser_bytes.decode("utf8")[13:18]+' '+ser_bytes.decode("utf8")[18:20]+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read Longitude
            elif ser_bytes.decode("utf8")[4:9] == '40 07':
                #print ('Lon: '+ser_bytes.decode("utf8")[10:20])
                txData = b't11.txt="'+ser_bytes.decode("utf8")[10:13]+'° '+ser_bytes.decode("utf8")[14:19]+' '+ser_bytes.decode("utf8")[19:21]+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read Downlink IF (40 03 + 64 03)
            elif ser_bytes.decode("utf8")[4:9] == '40 03':
                rx_if_1 = ser_bytes.decode("utf8")[10:13]
            elif ser_bytes.decode("utf8")[4:9] == '64 03':
                rx_if_2 = ser_bytes.decode("utf8")[11:13]
                print ('RX IF: '+rx_if_1+'.'+rx_if_2+' MHz')
            # Read LNB Reference IF (48 04 + 64 04)
            elif ser_bytes.decode("utf8")[4:9] == '48 04':
                lnb_ref_1 = ser_bytes.decode("utf8")[10:12]
            elif ser_bytes.decode("utf8")[4:9] == '64 04':
                lnb_ref_2 = ser_bytes.decode("utf8")[11:13]
                print ('LNB Ref: '+lnb_ref_1+'.'+lnb_ref_2+' MHz')
            # Print unknown sentences
            else:
                if debug==1:
                    print(ser_bytes.decode("utf8"))
        else:
            print('Unknown sentence received')
            print(ser_bytes.decode("utf8"))
        act_led.value(0)
        if config_written == 0:
            #print("config not yet written")
            if tx_lo != '' and tx_if != '' and rx_if_1 != '' and rx_if_2 != '' and lnb_ref_1 != '' and lnb_ref_2 != '':
            #if rx_if_1 != '' and rx_if_2 !I= '' and lnb_ref_1 != '' and lnb_ref_2 != '':
                txData = b'config.va0.txt="'+tx_lo+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
                txData = b'config.va1.txt="'+tx_if+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
                txData = b'config.va2.txt="'+rx_if_1+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
                txData = b'config.va3.txt="'+rx_if_2+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
                txData = b'config.va4.txt="'+lnb_ref_1+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
                txData = b'config.va5.txt="'+lnb_ref_2+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
                txData = b'page 1'
                uart0.write(txData)
                uart0.write(end_cmd)
                config_written=1
                    
            
            
            #txData = b't0.txt="TEST: '+ser_bytes.decode("utf8")+'"'
            #uart0.write(txData)
            #uart0.write(end_cmd)

txData = b'page 0'
uart0.write(txData)
uart0.write(end_cmd)