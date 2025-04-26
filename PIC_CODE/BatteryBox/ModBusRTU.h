#include <pic.h>

#define _XTAL_FREQ 8000000


unsigned short modRTU_CRC(unsigned char* buff, unsigned int len);
int validateRTU(unsigned char* buff, unsigned int len);
char RS485_Init(void);
char RS485_Data_Ready(void);
unsigned int RS485_Read_Data(unsigned char *buffer,unsigned char max);
void RS485_Write_Data(unsigned char *text, unsigned int num);
void RS232_Write_Data(char *text, int num);

