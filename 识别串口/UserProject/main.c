#include "stm32f10x.h"
#include "usart.h"
#include "usart2.h"
#include "delay.h"
#include "sys.h"
#include "lcd.h"
#include "gui.h"
extern int m;
int m_last = 0,i;

int main()
{
	
	uart_init(9600);
	USART2_Init(115200);
	SystemInit();//��ʼ��RCC ����ϵͳ��ƵΪ72MHZ
	delay_init();
	LCD_Init();	   //Һ������ʼ��
	LCD_Clear(BLACK); //����

	POINT_COLOR=WHITE; 
	
	LCD_DrawRectangle(0,0,128-1,128-1);	//������ 

	Show_Str(32,5,BLACK,WHITE,"ϵͳ���",16,0);
	
	Show_Str(5,25,WHITE,WHITE,"�¶�:     ��",24,1);
	
	LCD_ShowNum2412(15+48,25,WHITE,WHITE,"3.2",24,1);

	Show_Str(5,50,WHITE,WHITE,"ʪ��:     ��",24,1);
	LCD_ShowNum2412(15+48,50,WHITE,WHITE,"2.0",24,1);

Show_Str(5,75,WHITE,WHITE,"��ѹ:     ��",24,1);
	LCD_ShowNum2412(15+48,75,WHITE,WHITE,"3.2",24,1);

  Show_Str(5,100,WHITE,WHITE,"����:     ��",24,1);
//	LCD_ShowNum2412(5+48,100,GREEN,YELLOW,":0.2",24,1);	  
	while(1)
	{
		i = 20;
    LCD_ShowNum(18,105,i,8,16);
	}
	
	
}
