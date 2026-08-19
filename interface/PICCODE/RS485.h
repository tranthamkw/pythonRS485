/* 
 * File:   RS485.h
 * Author: tranthamkw
 *
 * Created on July 5, 2018, 5:04 PM
 */

#ifndef RS485_H
#define	RS485_H

#ifdef	__cplusplus
extern "C" {
#endif


#include <xc.h>
#define _XTAL_FREQ 16000000
   
void RS485_Init(void);    
void resetRS485(void);
unsigned short modRTU_CRC(unsigned char* buff, unsigned char len);
unsigned char validateRTU(unsigned char* buff, unsigned char len);
unsigned char RS485_Data_Ready(void);

unsigned char RS485_Read_Data(unsigned char *buffer, unsigned short max);
void RS485_Write_Data(unsigned char *text, char num);

#ifdef	__cplusplus
}
#endif

#endif	/* RS485_H */

