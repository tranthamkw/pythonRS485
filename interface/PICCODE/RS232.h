/* 
 * File:   RS232.h
 * Author: tranthamkw
 *
 * Created on July 11, 2018, 8:45 PM
 */

#ifndef RS232_H
#define	RS232_H

#ifdef	__cplusplus
extern "C" {
#endif


#include <xc.h> 
#define _XTAL_FREQ 16000000
    
    
void RS232_Init(void);
void resetRS232(void);
unsigned char RS232_Data_Ready(void);
unsigned char RS232_Read_Data(unsigned char *buffer,unsigned char max);
void RS232_Write_Data(const unsigned char *text, unsigned char num);

#ifdef	__cplusplus
}
#endif

#endif	/* RS232_H */

