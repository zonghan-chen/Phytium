#include "stdio.h"

#include "stm32f1xx_hal.h"

#define LED_BUZZER_GPIO_PORT GPIOA

#define LED1_PIN GPIO_PIN_1
#define LED2_PIN GPIO_PIN_2
#define LED3_PIN GPIO_PIN_3

#define BUZZER_PIN GPIO_PIN_6

// 初始化GPIO
static void GPIO_Init(void);

static void Turn_On_LED_Buzzer(void);  // 点亮LED并开启蜂鸣器
static void Turn_Off_LED_Buzzer(void); // 熄灭LED并关闭蜂鸣器

int main(void)
{
    HAL_Init();

    GPIO_Init();

    while (1)
    {
        Turn_On_LED_Buzzer();
        HAL_Delay(5000);

        Turn_Off_LED_Buzzer();
        HAL_Delay(5000);
    }

    return 0;
}

static void GPIO_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    // 使能GPIOA时钟
    __HAL_RCC_GPIOA_CLK_ENABLE();

    // 配置LED & 蜂鸣器GPIO引脚
    GPIO_InitStruct.Pin = LED1_PIN | LED2_PIN | LED3_PIN | BUZZER_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;

    HAL_GPIO_Init(LED_BUZZER_GPIO_PORT, &GPIO_InitStruct);
}

static void Turn_On_LED_Buzzer(void)
{
    // 点亮LED
    HAL_GPIO_WritePin(LED_BUZZER_GPIO_PORT, LED1_PIN | LED2_PIN | LED3_PIN, GPIO_PIN_RESET);

    // 开启蜂鸣器
    HAL_GPIO_WritePin(LED_BUZZER_GPIO_PORT, BUZZER_PIN, GPIO_PIN_SET);
}

static void Turn_Off_LED_Buzzer(void)
{
    // 熄灭LED
    HAL_GPIO_WritePin(LED_BUZZER_GPIO_PORT, LED1_PIN | LED2_PIN | LED3_PIN, GPIO_PIN_SET);

    // 关闭蜂鸣器
    HAL_GPIO_WritePin(LED_BUZZER_GPIO_PORT, BUZZER_PIN, GPIO_PIN_RESET);
}

void SysTick_Handler(void)
{
    HAL_IncTick();
}
