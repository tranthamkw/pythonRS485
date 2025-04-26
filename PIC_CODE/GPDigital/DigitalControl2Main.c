#include <pic.h>
#include <string.h>
#include "ModBusRTU.h"
#include "SSD1306.h"


/*
 * General purpose Digital I/O
 * 
 * 
 * Microcontroller listens to RS485 commands:
 * 
 * available ports: RA5, RA4, RC3, RB4
 * Configurable individually as input or output
 *  
 * Structure of MODBUS commands:
 * RECEIVE DATA
 * data[0] = RS485 address
 * data[1] = 0x06 or 0x03; read or write respectively to a register
 * data[2] = which register LSB
 * data[3] = which register MSB
 * data[4] = data MSB
 * data[5] = data LSB [MSB:  RA5 RA4 RC3 RB4: LSB]
 * data[6] = CRC
 * data[7] = CRC
 * 
 * BASEREG +16 = read/write to RA5 RA4 RC3 RB4
 * BASEREG + 8 = read/write to TRISA5  TRISA4   TRISC3  TRISB4  : 1 = input,0=output
 * 
 * RETURN DATA
 * data[0] = RS485 address
 * data[1] = 0x06 or 0x03 (echo back) and (OR) 0x80 if there is an error
 *              if an error, data[2] and [3] contain error codes
 * data[2] = Number of bytes to follow
 *      if request function string
 * data[3.. n] = information
 *      if getting digital status 
 * data[3]=0
 * data[4] = MSB->  RA5 RA4 RC3 RB4 <- MSB
 * 
 *

*/

// PIC16F690 Configuration Bit Settings

// 'C' source line config statements

// CONFIG
#pragma config FOSC = INTRCIO   // Oscillator Selection bits (INTOSCIO oscillator: I/O function on RA4/OSC2/CLKOUT pin, I/O function on RA5/OSC1/CLKIN)
#pragma config WDTE = OFF       // Watchdog Timer Enable bit (WDT disabled and can be enabled by SWDTEN bit of the WDTCON register)
#pragma config PWRTE = OFF      // Power-up Timer Enable bit (PWRT disabled)
#pragma config MCLRE = OFF      // MCLR Pin Function Select bit (MCLR pin function is digital input, MCLR internally tied to VDD)
#pragma config CP = OFF         // Code Protection bit (Program memory code protection is disabled)
#pragma config CPD = OFF        // Data Code Protection bit (Data memory code protection is disabled)
#pragma config BOREN = OFF      // Brown-out Reset Selection bits (BOR disabled)
#pragma config IESO = OFF       // Internal External Switchover bit (Internal External Switchover mode is disabled)
#pragma config FCMEN = OFF      // Fail-Safe Clock Monitor Enabled bit (Fail-Safe Clock Monitor is disabled)


#define BASEREG 0x0A0A
#define FNREG 0x00F0
#define ADDRESSREG 0x00FF

#define MYFUNCTION "GPDIGITALIO"//16 char limit
unsigned char address=0xA6;

void updateDisplayStatus(void){
	char temp[16],outText[24];
	unsigned int k;
	clearDisplaySSD1306();
	strcpy(outText,"FUNCTION: ");
	strcat(outText,MYFUNCTION);
	k=strlen(outText);
	writeCharSSD1306(0,0,outText,k,0);

	strcpy(outText,"RS485Address: 0x");
	itoa(address,temp,16,2);
	strcat(outText,temp);
	k=strlen(outText);
	writeCharSSD1306(1,0,outText,k,0);
/*
	strcpy(outText,"RA4 ");
	itoa(RA4,temp,2,1);
	strcat(outText,temp);
	k=strlen(outText);
	writeCharSSD1306(3,0,outText,k,0);

	strcpy(outText,"RA5 ");
	itoa(RA5,temp,2,1);
	strcat(outText,temp);
	k=strlen(outText);
	writeCharSSD1306(3,10,outText,k,0);
*/
    
}


void main (void) {	
 	unsigned int i,k;
	unsigned int reg;
	unsigned int strlength;
	char error;
	unsigned char data[24];
	char fnString[16];
	unsigned short outdata;
	
	PORTA =0;    //clears port A
	TRISA=0;
	TRISC = 0;    
	PORTC = 0;    //clears port C
	CM1CON0 = 7;    //turn off comparators
	CM2CON0 = 7;
	CM2CON1 = 7;
	ANSEL = 0;    //turns off ADC
	OSCCON=0x70;         // Select 8 MHz internal clock
	address=EEPROM_READ(0x00);
	RS485_Init();

    //Power on DEFAULT: set to inputs. IF any need to be set to outputs
    //then the init code from the controlling computer needs to set this.
    //so we dont accidentally have to outputs connected to another 'output' device.
	TRISC3=1; //1: input.  0: Output
	TRISB4=1;
	TRISA5=1;
	TRISA4=1;

 	initSSD1306();
	//updateDisplayStatus();
	
	strlength=0;
	error=0;
   /* MSB         LSB
  * RA5 RA4 RC3 RB4*/
    
    
  do  {

	if (RS485_Data_Ready()==1){		
        strlength = RS485_Read_Data(data,24);
		CREN=0;	
		if (validateRTU(data,strlength) ==0){
				// RTU CRC valid
			if (!RA3) {	// if button pressed, remember this address as our own.
				address = data[0];
				EEPROM_WRITE(0x00,address);
			}
			delay(100);
            if (data[0]==address){ //address byte
			// message intended for us
				switch (data[1]){  // command code byte
					case 0x06: // write a register
						reg = (unsigned int)(data[2]<<8) | (data[3]);
							switch (reg){
								case BASEREG +16:
 /* MSB         LSB
  * RA5 RA4 RC3 RB4*/
									RB4=(data[5] & 0x01);
                                    RC3=((data[5] & 0x02) >>1);
                                    RA4=((data[5] & 0x04)>>2);
									RA5=((data[5] & 0x08)>>3);
									strlength=6;
									RS485_Write_Data(data,strlength);
									error = 0;
									break;
                                case BASEREG+8:
 /* MSB         LSB
  * RA5 RA4 RC3 RB4*/
									TRISB4=(data[5] & 0x01);
                                    TRISC3=((data[5] & 0x02) >>1);
                                    TRISA4=((data[5] & 0x04)>>2);
									TRISA5=((data[5] & 0x08)>>3);
									strlength=6;
									RS485_Write_Data(data,strlength);
									error = 0;
									break;    
                                case ADDRESSREG:
                                    address=(unsigned char)(data[4]<<4|data[5]);
                                    strlength=6;
									RS485_Write_Data(data,strlength);
									error = 0;
									break;        
                                default:
								// invalid register
									error = 0x02;
									break;
								}
								break; // write to a register
					case 0x03:  // read a register
						reg = (unsigned int)(data[2]<<8) | (data[3]);
							switch (reg) {
								case BASEREG+16:
										// formulate a response. 
									data[2]=2;  //number of bytes to follow of data
									data[3]=0;
 /* MSB         LSB
  * RA5 RA4 RC3 RB4*/
									data[4]=(unsigned char)((RA5*8)+(RA4*4)+(RC3*2)+RB4);
									strlength=5;
									RS485_Write_Data(data,strlength);
									error =0;
									break;
                                    case BASEREG+8:
										// formulate a response. 
									data[2]=2;  //number of bytes to follow of data
									data[3]=0;
 /* MSB         LSB
  * RA5 RA4 RC3 RB4*/
									data[4]=(unsigned char)((TRISA5*8)+(TRISA4*4)+(TRISC3*2)+TRISB4);
									strlength=5;
									RS485_Write_Data(data,strlength);
									error =0;
									break;
								case FNREG:
									strcpy(fnString,MYFUNCTION);
									strlength = strlen(fnString);
										//data[0]=<RS485Address>; //data[1]=03;
									data[2] = (unsigned char)strlength;// number of bytes to follow
									for (i=0;i<strlength;i++){
										data[3+i]=fnString[i];
									}
									strlength+=3;
            						RS485_Write_Data(data,strlength);
									error =0;
								break;
								default:
									error = 0x02; // invalid register+
									break;
								}		
							break;// read a register
						
					default:
					// unknown command byte
					error = 0x08;
					break;
				}//end switch data[1]
				if (error) {
					data[1]=data[1] | 0x80;
					data[2]= (error & 0xFF00)>>8;
					data[3]=(error & 0x00FF);
					strlength=4;
					RS485_Write_Data(data,strlength);
					}
						//updateDisplayStatus();
			}/// message intended for another address. ignore message.
			} else {
					//invalid RTU  just ignore the message
			}	
			CREN=1; // this sequence resets the receive register. The act of writing tends to load a single bit 
			CREN=0;
			CREN=1;
		}// end data ready
}while(1);
}