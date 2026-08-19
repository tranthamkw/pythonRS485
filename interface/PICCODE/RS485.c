#include "RS485.h"

#define RS485CONTROL LATAbits.LATA7

#define LISTEN 0
#define WRITE 1

void RS485_Init(void){
   /* ANSELCbits.ANSC7 = 0;  // Disable analog on RX1
    TRISCbits.TRISC7 = 1;  // Set RX1 as input
    TRISAbits.TRISA7 = 0;  // Set RS485 DE/RE control pin as outpu
   */ 
   // EUSART1_Initialize();
        // ABDOVF no_overflow; CKTXP async_noninverted_sync_fallingedge; BRG16 16bit_generator; WUE disabled; ABDEN disabled; DTRXP not_inverted; 
    BAUDCON1 = 0x08;
    // SPEN enabled; RX9 8-bit; CREN enabled; ADDEN disabled; SREN disabled; 
    RCSTA1 = 0x90;
    // TX9 8-bit; TX9D 0; SENDB sync_break_complete; TXEN enabled; SYNC asynchronous; BRGH hi_speed; CSRC slave_mode; 
    TXSTA1 = 0x24;
    // Baud Rate = 9600; 
    SPBRG1 = 0xA0;
    // Baud Rate = 9600; 
    SPBRGH1 = 0x01;
    
    RS485CONTROL=LISTEN;
    resetRS485();
 
}

void resetRS485(void){
    volatile unsigned char dummy;
    
    // 1. Reset the receiver logic and clear OERR errors
    RCSTA1bits.CREN = 0; 
    RCSTA1bits.CREN = 1;
    
    // 2. Flush any trash data currently stuck in the 2-byte FIFO buffer
    dummy = RCREG1; 
    dummy = RCREG1;
}

unsigned short modRTU_CRC(unsigned char* buff, unsigned char len){
//calculates CRC for Modbus specs
	unsigned short crc=0xFFFF;
	unsigned char pos;
	unsigned char bits;
    for(pos=0;pos<len;pos++){
		crc^=(unsigned short) buff[pos];
		for(bits=8;bits!=0;bits--){
			if((crc&0x0001)!=0){
				crc>>=1;
				crc^=0xA001;
			}else{
				crc>>=1;
			}
		}
	}
return crc;
}

unsigned char validateRTU(unsigned char* buff, unsigned char len){
	/* len is the full length of the buffer.  The last two elements in the array
	are assumed to be  CRC bytes.
		*/
	unsigned char j;
	unsigned short temp;
	j=1;
	if(len>3){
        temp = (((unsigned short)buff[len-1] << 8) | (unsigned short)buff[len-2]);

//		temp=((buff[len-1]<<8)|(buff[len-2]));
		if(temp==modRTU_CRC(buff,(unsigned char) len-2)) j=0; // valid.yes.
	}
return j;
}

unsigned char RS485_Data_Ready(void)
{
    return PIR1bits.RC1IF;//RC1IF;
}



unsigned char RS485_Read_Data(unsigned char *buffer, unsigned short max) {
    unsigned char i = 0;
    unsigned int timeout_counter = 0;
    
    // Safety check: If a hardware overrun happened before starting, clear it
    if (RCSTA1bits.OERR) {
        resetRS485();
    }

    // Loop until we hit a character timeout (inter-byte gap)
    while (timeout_counter < 8000) { // Adjust this number based on your clock
        if (PIR1bits.RC1IF) {
            // A byte arrived! Reset the timeout counter instantly
            timeout_counter = 0; 
            
            if (i < max) { // Utilize the full array size up to 'max'
                buffer[i] = RCREG1;
                i++;
            } else {
                volatile char dummy = RCREG1; // Flush buffer safely if full
            }
        } else {
            // No byte ready, increment the timeout tracker
            timeout_counter++;
            __delay_us(1); 
        }
    }

    return i; // Return the exact number of raw binary bytes read
}


void RS485_Write_Data(unsigned char *text, char num){
  	char i;
	unsigned short temp;
	char crc[2];
	temp=modRTU_CRC(text,num);
	crc[1]=(temp&0xFF00)>>8;
	crc[0]=(temp&0x00FF);
 
    RS485CONTROL=WRITE;
	
    for(i=0;i<num;i++){
			while (!TXSTA1bits.TRMT); // wait until empty
			if (TXSTA1bits.TRMT){  // transmit register empty
			TXREG1 = text[i];
			}
	}
	for(i=0;i<2;i++){
			while (!TXSTA1bits.TRMT); // wait until empty
			if (TXSTA1bits.TRMT){  // transmit register empty
			TXREG1 = crc[i];
			}
	}

	while (!TXSTA1bits.TRMT); //wait until data is completely shifted out.
	__delay_us(20);
    
	 RS485CONTROL=LISTEN;
		// set RS485 to listen
     resetRS485();
}
