# ConverterDisplay v0.2
# Florian Wolters, DF2ET

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
string = ''
config_written=0

while True:
    if uart1.any():
        act_led.value(1)
        ser_bytes = uart1.readline();
        string = ser_bytes.decode("utf8").strip()
        x = string.split(" ")
        # Debug output
        if debug==1:
            txData = b't01.txt+="\r'+string+'"'
            uart0.write(txData)
            uart0.write(end_cmd)
            print(string)
            print('       012345678901234567890')
            print('                 1         2')
        # Read UpConverter Values (first column is always 00 here so ignore x[1])
        if x[0] == 'UPC':
            # Read Temperature (00)
            if x[2] == '00':
                #print('Temp: '+x[3]+' \u00b0C')
                txData = b't3.txt="'+x[3]+'\u00b0C "'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read Voltage (01)
            elif x[2] == '01':
                voltage = int(x[3]) / 1000
                #print('Voltage: %3.2f V' % voltage)
                txData = b't4.txt="%3.2f V "' % voltage
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read forward power (02)
            elif x[2] == '02':
                dbm = int(x[4])
                watts = pow(10,(dbm/10))/1000
                #print('FWD power: %d dBm / %3.2f W' % (dbm, watts))
                txData = b't20.txt="%d dBm "' % dbm
                uart0.write(txData)
                uart0.write(end_cmd)
                txData = b't21.txt="%3.2f W "' % watts
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read LO frequency (05)
            elif x[2] == '05':
                if tx_lo == '':
                    print('LO: '+x[3]+' kHz')
                    tx_lo = int(x[3])/1000
            # Read PTT state (06)
            elif x[2] == '06':
                if x[3] == '1':
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
            elif x[2] == '07':
                print('Ver: '+x[3])
            # Read IF frequency (10)
            elif x[2] == '10':
                if tx_if == '':
                    print('IF: '+x[3]+' kHz')
                    tx_if = int(x[3])/1000
            # Read UpConverter ADF4351 state
            elif x[2] == '09':
                #print ('UpConv ADF4351 state: '+x[3])
                up4351 = x[3];
            # Print unknown sentences
            else:
                if debug==1:
                    print(ser_bytes.decode("utf8"))
        
        # Read DownConverter Values
        elif x[0] == 'OLD':
            # Read GPS time
            if x[1] == '00' and x[2] =='01':
                #print ('GPS Time: '+x[3])
                txData = b't1.txt="'+x[3]+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read GPS SAT count
            elif x[1] == '56' and x[2] == '05':
                #print ('SATs: '+x[3])
                txData = b't2.txt="'+x[3]+' "'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read Maidenhead grid
            elif x[1] == '72' and x[2] == '01':
                #print ('Grid: '+x[3])
                txData = b't0.txt="'+x[3][0:4]+x[3][4:].lower()+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read Latitude
            elif x[1] == '48' and x[2] == '06':
                #print ('Lat: '+x[3])
                txData = b't10.txt="'+x[3][0:2]+'\u00b0 '+x[3][3:5]+'.'+x[3][6:8]+' '+x[3][8:9]+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read Longitude
            elif x[1] == '40' and x[2] == '07':
                #print ('Lon: '+x[3])
                txData = b't11.txt="'+x[3][0:3]+'\u00b0 '+x[3][4:6]+'.'+x[3][7:9]+' '+x[3][9:10]+'"'
                uart0.write(txData)
                uart0.write(end_cmd)
            # Read Downlink IF (40 03 + 64 03)
            elif x[1] == '40' and x[2] == '03':
                rx_if_1 = x[3]
            elif x[1] == '64' and x[2] == '03':
                rx_if_2 = x[3][1:]
                print ('RX IF: '+rx_if_1+'.'+rx_if_2+' MHz')
            # Read LNB Reference IF (48 04 + 64 04)
            elif x[1] == '48' and x[2] == '04':
                lnb_ref_1 = x[3]
            elif x[1] == '64' and x[2] == '04':
                lnb_ref_2 = x[3][1:]
                print ('LNB Ref: '+lnb_ref_1+'.'+lnb_ref_2+' MHz')
            # Read source for reference frequency (80 00)
            elif x[1] == '80' and x[2] == '00':
                #print ('Ref source: '+x[3])
                ref_source = x[3];
            # Read DownConverter ADF4351 state
            elif x[1] == '88' and x[2] == '06':
                #print ('DownConv ADF4351 state: '+x[3])
                down4351 = x[3];
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