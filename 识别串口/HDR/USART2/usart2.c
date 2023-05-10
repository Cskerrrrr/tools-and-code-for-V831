#include "usart2.h"
#include "usart.h"
#include "stm32f10x_usart.h"

u8     USART2SendBuff[USART2BuffSize];        
u8     USART2ReceBuff[USART2BuffSize];        
u16    USART2ReceIn = 0;
u8     USART2ReceFullFlag = 0;



void USART2_Init(u32 bound)
{
    GPIO_InitTypeDef GPIO_InitStructure;
    NVIC_InitTypeDef NVIC_InitStructure;
    USART_InitTypeDef USART_InitStructure;;
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_USART2,ENABLE);
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA,ENABLE);
    
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_2;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    

    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_3;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
    GPIO_Init(GPIOA, &GPIO_InitStructure); 
    

    NVIC_InitStructure.NVIC_IRQChannel = USART2_IRQn;
    NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority=4;
    NVIC_InitStructure.NVIC_IRQChannelSubPriority = 0;
    NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
    NVIC_Init(&NVIC_InitStructure);
    
    USART_InitStructure.USART_BaudRate = bound;
    USART_InitStructure.USART_WordLength = USART_WordLength_8b;
    USART_InitStructure.USART_StopBits = USART_StopBits_1;
    USART_InitStructure.USART_Parity = USART_Parity_No;
    USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
    USART_InitStructure.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;
    USART_Init(USART2, &USART_InitStructure);
    
    USART_ITConfig(USART2,USART_IT_RXNE,ENABLE);
    USART_Cmd(USART2, ENABLE);
}


void USART2_SendData(u8 data)
{
	while((USART2->SR&0X40)==0); 
	USART2->DR = data;
}

void USART2_SendString(u8 *DAT,u8 len)
{
	u8 i;
	for(i=0;i<len;i++)
	{
	 	USART2_SendData(*DAT++);
	}	
}





void USART2_IRQHandler(void)
{
	  
    if(USART_GetITStatus(USART2, USART_IT_RXNE) != RESET)
    {
			  static char Res,Res_last;
			  static int i,flag;
				Res = USART_ReceiveData(USART2);
        if(Res == '1')
				{			
						Res_last = USART_ReceiveData(USART2);					
						if(Res_last == '1')
						{
							i = 1;
						}
					
				}
        if(Res == '2')
				{	
						Res_last = USART_ReceiveData(USART2);					
						if(Res_last == '2')
						{
							i = 2;
						}
					
        }
        if(Res == '3')
				{	
						Res_last = USART_ReceiveData(USART2);					
						if(Res_last == '3')
						{
							i = 3;
						}
        }
        if(Res == '4')
				{		
						Res_last = USART_ReceiveData(USART2);					
						if(Res_last == '4')
						{
							i = 4;
						}							
				}
				
				if(flag != i)
				{
					
						 switch(i)
						 {
							 case 1: 
								 flag = 1;
								 printf("棉签");
							 break;
							 case 2:
								 flag = 2;
								 printf("酒精");
							 break;
							 case 3: 
								 flag = 3;
								 printf("口罩");
							 break;
							 case 4:
								 flag = 4;
								 printf("防护服");
							 break;
							 default:
								 break;
						 }
						 
				}
						
				
    }

		   
}
