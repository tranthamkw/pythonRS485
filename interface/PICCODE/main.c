/**
  Generated Main Source File

  Company:
    Microchip Technology Inc.

  File Name:
    main.c

  Summary:
    This is the main file generated using PIC10 / PIC12 / PIC16 / PIC18 MCUs

  Description:
    This header file provides implementations for driver APIs for all modules selected in the GUI.
    Generation Information :
        Product Revision  :  PIC10 / PIC12 / PIC16 / PIC18 MCUs - 1.81.8
        Device            :  PIC18F46K22
        Driver Version    :  2.00
*/

/*
    (c) 2018 Microchip Technology Inc. and its subsidiaries. 
    
    Subject to your compliance with these terms, you may use Microchip software and any 
    derivatives exclusively with Microchip products. It is your responsibility to comply with third party 
    license terms applicable to your use of third party software (including open source software) that 
    may accompany Microchip software.
    
    THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER 
    EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY 
    IMPLIED WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS 
    FOR A PARTICULAR PURPOSE.
    
    IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE, 
    INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND 
    WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP 
    HAS BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO 
    THE FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL 
    CLAIMS IN ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT 
    OF FEES, IF ANY, THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS 
    SOFTWARE.
*/

#include "mcc_generated_files/mcc.h"
#include "RS485.h"
#include "RS232.h"
#include <string.h>
#include "memoryFunctions.h"
#include "simpleGFX.h"


#define BASEREG 0x0C0CU
#define FNREG 0x00F0U
#define MYFUNCTION "485-232Bridge"
#define SETTING_ADDR 0x00
#define MAXCHARS 128

unsigned char address;
char outText[MAXCHARS];


/*
 * BASEREG:
 * +1 : numreads (not used any more)
 * +2 : timeout in milliseconds default 1000
 * +4 : debug print (1 or 0) default 0
 * +32: write a string to the RS232 and wait for a response
 * 
 * FNREG: same for all device. register for function string
 * 
                         Main application
 */

void drawStartupScreen(void){
   
    strcpy(outText,"RS485Address:");
    advanceConsole(outText,CYAN,BLACK);
    charToHex(address,outText,2);
    advanceConsole(outText,CYAN,BLACK);
    strcpy(outText,"RS485 to RS232");
    advanceConsole(outText,YELLOW,BLACK); 
    strcpy(outText,"BRIDGE");
    advanceConsole(outText,YELLOW,BLACK);   
}




void main(void){
    unsigned short reg;
    unsigned char i,k,strlength;
	unsigned short error;
	unsigned char RS485data[MAXCHARS];
	unsigned char RS232data[MAXCHARS-4];
	char fnString[16];
    unsigned short timeOut = 1000; //time out in ms
    
    unsigned char debugPrint=0;
	unsigned short timeOutCounter;
	unsigned char temp;

    // Initialize the device
    SYSTEM_Initialize();
    
    __delay_ms(10);
    
    address=EEPROM_Read(SETTING_ADDR);
    __delay_ms(10);
    
    RS485_Init();
    RS232_Init();
    initDisplay();
    drawStartupScreen();
    // If using interrupts in PIC18 High/Low Priority Mode you need to enable the Global High and Low Interrupts
    // If using interrupts in PIC Mid-Range Compatibility Mode you need to enable the Global and Peripheral Interrupts
    // Use the following macros to:

    // Enable the Global Interrupts
    //INTERRUPT_GlobalInterruptEnable();

    // Disable the Global Interrupts
    //INTERRUPT_GlobalInterruptDisable();

    // Enable the Peripheral Interrupts
    //INTERRUPT_PeripheralInterruptEnable();

    // Disable the Peripheral Interrupts
    //INTERRUPT_PeripheralInterruptDisable();
   
    
    while (1){
       
        if (RS485_Data_Ready()){
            strlength = RS485_Read_Data(RS485data,MAXCHARS);
            
            if (validateRTU(RS485data,strlength)==0){
                if (PORTBbits.RB1==0){
                    // change the address
                    address=RS485data[0];
                    EEPROM_Write(SETTING_ADDR, address);
                    drawStartupScreen();
                    __delay_us(100);
                }
                error=0;
                if (RS485data[0]==address){
                    if (debugPrint){
                        //strcpy(outText, "RS485 Rx");
                        //printData(RS485data, strlength, BLACK,CYAN); 
                    }
                switch (RS485data[1]){  // command code byte
					case 0x06: // write a register  - USED TO "RECONFIGURE" THE DEVICE.
					reg = (unsigned short)((RS485data[2]<<8) | (RS485data[3]));
						switch (reg){
							
                            case (BASEREG+4):
                                temp = RS485data[5];  // assign new data to variable ("register")
								if (temp<2){
									debugPrint=temp;
										// formulate a response echo back command
									strlength=6;
                                    RS485_Write_Data(RS485data,strlength);
									error = 0;
									} else {
									error = 0x06; // out of range
									}
							break;
							case (BASEREG+2):
								 
                                timeOutCounter = ((unsigned short)RS485data[4]<<8)|(unsigned short)RS485data[5];  
								if (timeOutCounter>0){
									timeOut=timeOutCounter;
									strlength=6;
                                    RS485_Write_Data(RS485data,strlength); 
                                    error = 0;
									} else {
									error = 0x06; // out of range
									}
                                
							break;
							case (BASEREG+32):   
                                
                                strlength = strlength-2; // ignore last two elements as they are CRC's
                                for (i=4; i<strlength; i++){ //ignore first four bytes: ADDRESS 0x06 REGh REGl
										RS232data[i-4]=RS485data[i];//copy to RS232 buffer
								}
								strlength=strlength-4;  
								//rs232data is 4 bytes shorter since ignore channel and command bytes
                                if (debugPrint) {
                                   
                                    strcpy(outText,"RS232 Tx ==>");
                                    advanceConsole(outText,YELLOW,BLACK);
                                   RS232data[strlength]=0;
                                    strcpy(outText,(char *)RS232data);
                                    advanceConsole(outText,WHITE,BLACK);
                                    
                                }
                                    
                                RS232_Write_Data(RS232data,strlength); 
                                    
                                timeOutCounter=0;
                                strlength=0;
                                do{
								        __delay_ms(1);
                                        if (RS232_Data_Ready()==1){
                                        strlength = RS232_Read_Data(RS232data,MAXCHARS-4);
                                        timeOutCounter=timeOut; // message received so quit
                                        }
                                    timeOutCounter++;
                                } while (timeOutCounter<timeOut);
                                
								
								if (strlength==0){
											// no response from 232 device
									strcpy((char *)RS232data,"NO RESPONSE FROM RS232 DEVICE");
									strlength=(unsigned char)strlen((char *)RS232data);
								}		
                                if (debugPrint) {
                                    strcpy(outText,"==> RS232 Rx");
                                    advanceConsole(outText,YELLOW,BLACK);
                                    RS232data[strlength]=0;
                                    strcpy(outText,(char *)RS232data);
                                    advanceConsole(outText,WHITE,BLACK);
                                 }
							//copy to rs485 buffer. Address,command code is still saved data[0],data[1]
								RS485data[2] = strlength;
								for (i=3; i<(strlength+3); i++){
										RS485data[i]=RS232data[i-3];
								}
								strlength +=3;
								RS485_Write_Data(RS485data,strlength);
								error = 0;
                                      
                                
							break;// END WRITE TO write to RS232
							
                            default:
									// invalid register
                                error = 0x02;
							}
						break; // end write to a register
					case 0x03: // read from a register
					reg = (unsigned short)((RS485data[2]<<8) | (RS485data[3]));
						switch (reg){
							case (BASEREG + 2) :
									RS485data[2] = 2;
                                    //TODO change timeout
									RS485data[3] = ((timeOut&0xFF00)>>8);
									RS485data[4] = (timeOut&0x00FF);
									strlength=5;
									RS485_Write_Data(RS485data,strlength);
									error = 0;
							break;
                            case (BASEREG + 4):
								RS485data[2] = 2;
								RS485data[3] = 0;
								RS485data[4] = ((debugPrint&0x00FF));
								strlength=5;
                                RS485_Write_Data(RS485data,strlength);
								error = 0;
							break;
							case FNREG:
                                strcpy(fnString,MYFUNCTION);
                                strlength = (unsigned char) strlen(fnString);
                                    //data[0]=<RS485Address>; //data[1]=03;
                                RS485data[2] = (unsigned char)strlength;// number of bytes to follow
                                for (i=0;i<strlength;i++){
										RS485data[3+i]=fnString[i];
								}
                                strlength+=3;
                                RS485_Write_Data(RS485data,strlength);
                                error =0;
							break;
							default:
									// invalid register
								error = 0x02;
                            }// switch reg
                        break;//read a register
						default:
								// unknown command
								error = 0x08;
						break;
						}//end switch
                if ((debugPrint)&!(error)){
                    strcpy(outText, "RS485 Tx");
                    //printData(RS485data, strlength, CYAN, BLACK); 
                }
				if (error) {
					RS485data[1]=RS485data[1] | 0x80;
					RS485data[2]= (unsigned char)((error & 0xFF00) >> 8);
					RS485data[3]=(error & 0x00FF);
					strlength=4;
					RS485_Write_Data(RS485data,strlength);
                    if (debugPrint) {
                        strcpy(outText,"RS485 ERROR");
                        advanceConsole(outText,RED,BLACK);
                        switch (error){
                            case 0x02: strcpy(outText,"INVALID REGISTER");
                            break;
                            case 0x06: strcpy(outText, "VALUE OUT OF RANGE");
                            break;
                        default: strcpy(outText,"UNKNOWN COMMAND");
                        }
                    advanceConsole(outText,RED,BLACK);
                    }
                }

            } // if our address.
            //invalid RTU  just ignore the message
			}
       }//end RS485 data ready
    }
}
     
/*
 End of File
*/