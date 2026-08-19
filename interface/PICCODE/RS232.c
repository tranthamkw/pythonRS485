#include "RS232.h"

 void RS232_Init(void) {
    // Pin Configuration for RD6/TX2 and RD7/RX2
    TRISDbits.TRISD6 = 0;   // TX2 configured as digital output
    TRISDbits.TRISD7 = 1;   // RX2 configured as digital input

    // Ensure pins are digital
    ANSELDbits.ANSD6 = 0;   
    ANSELDbits.ANSD7 = 0;   

    // Baud Rate Control Configuration
    // OLD CODE: BAUDCON2 = 0x08; (BRG16 = 1)
    // NEW CODE: We set CKTXP = 1 and DTRXP = 1 to invert the TX and RX pins natively!
    BAUDCON2 = 0x38;        // BRG16 = 1, CKTXP = 1 (Invert TX), DTRXP = 1 (Invert RX)

    // Receive Status and Control: Enable 9-bit reception
    RCSTA2 = 0xD0;          // SPEN = 1, CREN = 1, RX9 = 1 

    // Transmit Status and Control: Enable 9-bit transmission
    TXSTA2 = 0x64;          // TXEN = 1, BRGH = 1, SYNC = 0, TX9 = 1

    // Baud Rate Reload Value (0x01A0 = 416 decimal for 16MHz)
    SPBRG2 = 0xA0; 
    SPBRGH2 = 0x01; 
    
    // Explicitly seed the line clean before starting
    resetRS232();
}


void RS232_InitOLD(void)
{
    // Pin Configuration for RD6/TX2 and RD7/RX2
    TRISDbits.TRISD6 = 0;   // TX2 configured as digital output
    TRISDbits.TRISD7 = 1;   // RX2 configured as digital input
    
    // ANSELD control (Ensure pins are digital if shared with analog channels)
    ANSELDbits.ANSD6 = 0;   // RD6 digital input buffer enabled
    ANSELDbits.ANSD7 = 0;   // RD7 digital input buffer enabled

    
    BAUDCON2 = 0x38;
    // Baud Rate Control: 16-bit generator, no auto-baud, normal polarity
    //BAUDCON2 = 0x08;        // BRG16 = 1, WUE = 0, ABDEN = 0
    
    
    // Receive Status and Control: Serial port enabled, 8-bit, continuous receive
    RCSTA2 = 0x90;          // SPEN = 1, CREN = 1, RX9 = 0
    // Transmit Status and Control: High-speed asynchronous, transmit enabled
    TXSTA2 = 0x24;          // TXEN = 1, BRGH = 1, SYNC = 0
    
    // Baud Rate Reload Value (0x01A0 = 416 decimal)
    SPBRG2 = 0xA0;
    SPBRGH2 = 0x01;
    resetRS232();
}

void resetRS232(void) {
    volatile unsigned char dummy; 
    
    // 1. Reset the receiver logic and clear OERR errors
    RCSTA2bits.CREN = 0; 
    RCSTA2bits.CREN = 1; 
    
    // 2. Flush any trash data currently stuck in the 2-byte FIFO buffer for EUSART2
    dummy = RCREG2; 
    dummy = RCREG2; 
}



unsigned char RS232_Data_Ready(void) 
{ 
    // Returns 1 if a byte is waiting in the UART2 FIFO receive buffer, 0 if empty
    return PIR3bits.RC2IF;//RC1IF;
}

unsigned char RS232_Read_Data(unsigned char *buffer, unsigned char max) { 
    unsigned char i = 0; 
    unsigned short timeout_counter = 0; 
    volatile unsigned char dummy9th; // Used to safely clear the 9-bit status
    volatile unsigned char dummyReg;

    // Clear Overrun error if it happened historically
    if (RCSTA2bits.OERR) { 
        RCSTA2bits.CREN = 0;
        NOP();
        RCSTA2bits.CREN = 1;
    } 

    // A counter limit of 5000 with a 1us explicit delay roughly equals 
    // a safe ~10-12ms real-world timeout at 16MHz Fosc. 
    while (timeout_counter < 5000) { 
        if (PIR3bits.RC2IF) { 
            timeout_counter = 0; // Reset timeout instantly on byte arrival 
            
            // CRITICAL STEP FOR 9-BIT MODE:
            // You must read the 9th bit status BEFORE reading RCREG2
            dummy9th = RCSTA2bits.RX9D; 

            if (i < max) { 
                buffer[i] = RCREG2; // Reading RCREG2 advances the hardware FIFO
                i++; 
            } else { 
                // Buffer full! Flush hardware FIFO to avoid OERR freezes 
                dummyReg = RCREG2; 
                break; 
            } 
        } else { 
            timeout_counter++; 
            __delay_us(1); 
        } 
    } 
    return i; // Returns total bytes read 
}

unsigned char RS232_Read_DataOLD(unsigned char *buffer, unsigned char max) { 
    unsigned char i = 0; 
    unsigned short timeout_counter = 0; 

    // CRITICAL: Overrun error freezes the RX hardware. You must clear it.
    if (RCSTA2bits.OERR) { 
        resetRS232();
    } 

    // A counter limit of 5000 with a 1us explicit delay roughly equals 
    // a safe ~10-12ms real-world timeout at 16MHz Fosc.
    while (timeout_counter < 5000) { 
        if (PIR3bits.RC2IF) { 
            timeout_counter = 0; // Reset timeout instantly on byte arrival 
            
            if (i < max) { 
                buffer[i] = RCREG2; 
                i++; 
            } else { 
                // Buffer full! Flush hardware FIFO to avoid OERR freezes
                volatile char dummy = RCREG2; 
                break; 
            } 
        } else { 
            timeout_counter++; 
            __delay_us(1); 
        } 
    } 

    return i; // Returns total bytes read
}


void RS232_Write_Data(const unsigned char *text, unsigned char num) { 
    unsigned char i; 
    
    for (i = 0; i < num; i++) { 
        // Wait for the Transmit Buffer (FIFO) to be empty and ready for data 
        while (!PIR3bits.TX2IF); 
        
        // Force the 9th bit high BEFORE writing to TXREG2.
        // This acts as the mandatory 1st stop bit for SRS instruments.
        TXSTA2bits.TX9D = 1; 
        
        // Load the byte into the hardware transmit register 
        TXREG2 = text[i]; 
        
        __delay_us(10); 
    } 
    
    // Wait until the final byte is completely shifted out of the hardware TSR register 
    while (!TXSTA2bits.TRMT); 
    __delay_us(50); 
    
   // resetRS232(); 
}

void RS232_Write_DataOLD(const unsigned char *text, unsigned char num)
{
    unsigned char i;
    for (i = 0; i < num; i++)
    { 
        // Wait for the Transmit Buffer (FIFO) to be empty and ready for data
        while (!PIR3bits.TX2IF);
        // Load the byte into the hardware transmit register
        TXREG2 = text[i];
        __delay_us(10);
       
    }

    // Wait until the final byte is completely shifted out of the hardware TSR register
    while (!TXSTA2bits.TRMT);
    __delay_us(50);
    
    resetRS232();
}
