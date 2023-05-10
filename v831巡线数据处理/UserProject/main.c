#include "stm32f10x.h"
#include "usart.h"
#include "usart2.h"
#include "delay.h"
#include "sys.h"
#include "lcd.h"
#include "gui.h"
extern int X,Y;
extern __IO uint8_t rxBuffer[20];
int main()
{

	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);//w4级抢占,4级响应。
	uart_init(115200);
	USART2_Init(115200);
	delay_init(); 
	while(1)
	{

		  
	}
	
	
}
