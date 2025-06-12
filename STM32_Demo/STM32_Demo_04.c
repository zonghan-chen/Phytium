#include "stdio.h"

#include "stm32f1xx_hal.h"

#define LED_GPIO_PORT GPIOA

#define LED1_PIN GPIO_PIN_1
#define LED2_PIN GPIO_PIN_2
#define LED3_PIN GPIO_PIN_3

// 初始化GPIO
static void MX_GPIO_Init(void);

int main(void)
{
    HAL_Init();

    MX_GPIO_Init();

    while (1)
    {
        HAL_GPIO_WritePin(LED_GPIO_PORT, LED1_PIN, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(LED_GPIO_PORT, LED3_PIN, GPIO_PIN_SET);
        HAL_Delay(2000);

        HAL_GPIO_WritePin(LED_GPIO_PORT, LED2_PIN, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(LED_GPIO_PORT, LED1_PIN, GPIO_PIN_SET);
        HAL_Delay(2000);

        HAL_GPIO_WritePin(LED_GPIO_PORT, LED3_PIN, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(LED_GPIO_PORT, LED2_PIN, GPIO_PIN_SET);
        HAL_Delay(2000);
    }

    return 0;
}

static void MX_GPIO_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    // 使能GPIOA时钟
    __HAL_RCC_GPIOA_CLK_ENABLE();

    // 配置LED GPIO引脚
    GPIO_InitStruct.Pin = LED1_PIN | LED2_PIN | LED3_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_MEDIUM;

    HAL_GPIO_Init(LED_GPIO_PORT, &GPIO_InitStruct);

    // 初始化LED为关闭状态（低电平有效）
    HAL_GPIO_WritePin(LED_GPIO_PORT, LED1_PIN | LED2_PIN | LED3_PIN, GPIO_PIN_SET);
}
