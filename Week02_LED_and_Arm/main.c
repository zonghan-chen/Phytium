#include <stdio.h>
#include <string.h>

#include "stm32f1xx_hal.h"

#ifdef __GNUC__
#define PUTCHAR_PROTOTYPE int __io_putchar(int ch)
#else
#define PUTCHAR_PROTOTYPE int fputc(int ch, FILE *f)
#endif

#define LED1_PIN GPIO_PIN_1
#define LED2_PIN GPIO_PIN_2
#define LED3_PIN GPIO_PIN_3

#define LED_GPIO_PORT GPIOA

#define USART1_TX_PIN GPIO_PIN_9
#define USART1_RX_PIN GPIO_PIN_10

#define USART1_GPIO_PORT GPIOA

static void SystemClock_Config(void);

static void MX_GPIO_Init(void);
static void MX_USART1_Init(void);

static void Error_Handler(void);

UART_HandleTypeDef huart1;

uint8_t uart_rx_idx = 0;
uint8_t uart_rx_data_byte;
uint8_t uart_rx_buffer[32];

int main(void)
{
    HAL_Init();

    SystemClock_Config();

    MX_GPIO_Init();
    MX_USART1_Init();

    if (HAL_UART_Receive_IT(&huart1, &uart_rx_data_byte, 1) != HAL_OK)
    {
        Error_Handler();
    }

    printf("Please Enter the Command: \r\n");

    while (1)
    {
    }
}

static void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    RCC_OscInitStruct.HSEState = RCC_HSE_ON;
    RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;

    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
    {
        Error_Handler();
    }

    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
    {
        Error_Handler();
    }
}

static void MX_GPIO_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    __HAL_RCC_GPIOA_CLK_ENABLE();

    GPIO_InitStruct.Pin = LED1_PIN | LED2_PIN | LED3_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(LED_GPIO_PORT, &GPIO_InitStruct);

    HAL_GPIO_WritePin(LED_GPIO_PORT, LED1_PIN | LED2_PIN | LED3_PIN, GPIO_PIN_SET);

    GPIO_InitStruct.Pin = USART1_TX_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(USART1_GPIO_PORT, &GPIO_InitStruct);

    GPIO_InitStruct.Pin = USART1_RX_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(USART1_GPIO_PORT, &GPIO_InitStruct);
}

static void MX_USART1_Init(void)
{
    __HAL_RCC_USART1_CLK_ENABLE();

    huart1.Instance = USART1;
    huart1.Init.BaudRate = 115200;
    huart1.Init.WordLength = UART_WORDLENGTH_8B;
    huart1.Init.StopBits = UART_STOPBITS_1;
    huart1.Init.Parity = UART_PARITY_NONE;
    huart1.Init.Mode = UART_MODE_TX_RX;
    huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart1.Init.OverSampling = UART_OVERSAMPLING_16;

    if (HAL_UART_Init(&huart1) != HAL_OK)
    {
        Error_Handler();
    }

    HAL_NVIC_SetPriority(USART1_IRQn, 0, 1);
    HAL_NVIC_EnableIRQ(USART1_IRQn);
}

static void Error_Handler(void)
{
    printf("ERROR: Error_Handler Called!\r\n");
    while (1)
    {
    }
}

void SysTick_Handler(void)
{
    HAL_IncTick();
}

void USART1_IRQHandler(void)
{
    HAL_UART_IRQHandler(&huart1);
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART1)
    {
        if (uart_rx_idx < sizeof(uart_rx_buffer) - 1)
        {
            if (uart_rx_data_byte == '\n')
            {
                uart_rx_buffer[uart_rx_idx] = '\0';

                char *command = (char *)uart_rx_buffer;
                printf("COMMAND: %s\r\n", command);

                if (strcmp(command, "RED_ON") == 0)
                {
                    HAL_GPIO_WritePin(LED_GPIO_PORT, LED1_PIN, GPIO_PIN_RESET);
                    HAL_GPIO_WritePin(LED_GPIO_PORT, LED2_PIN, GPIO_PIN_SET);
                    HAL_GPIO_WritePin(LED_GPIO_PORT, LED3_PIN, GPIO_PIN_SET);

                    printf("RED_ON\r\n");
                }
                else if (strcmp(command, "RED_OFF") == 0)
                {
                    HAL_GPIO_WritePin(LED_GPIO_PORT, LED1_PIN, GPIO_PIN_SET);
                    printf("RED_OFF\r\n");
                }
                else if (strcmp(command, "GREEN_ON") == 0)
                {
                    HAL_GPIO_WritePin(LED_GPIO_PORT, LED1_PIN, GPIO_PIN_SET);
                    HAL_GPIO_WritePin(LED_GPIO_PORT, LED2_PIN, GPIO_PIN_RESET);
                    HAL_GPIO_WritePin(LED_GPIO_PORT, LED3_PIN, GPIO_PIN_SET);

                    printf("GREEN_ON\r\n");
                }
                else if (strcmp(command, "GREEN_OFF") == 0)
                {
                    HAL_GPIO_WritePin(LED_GPIO_PORT, LED2_PIN, GPIO_PIN_SET);
                    printf("GREEN_OFF\r\n");
                }
                else if (strcmp(command, "BLUE_ON") == 0)
                {
                    HAL_GPIO_WritePin(LED_GPIO_PORT, LED1_PIN, GPIO_PIN_SET);
                    HAL_GPIO_WritePin(LED_GPIO_PORT, LED2_PIN, GPIO_PIN_SET);
                    HAL_GPIO_WritePin(LED_GPIO_PORT, LED3_PIN, GPIO_PIN_RESET);

                    printf("BLUE_ON\r\n");
                }
                else if (strcmp(command, "BLUE_OFF") == 0)
                {
                    HAL_GPIO_WritePin(LED_GPIO_PORT, LED3_PIN, GPIO_PIN_SET);
                    printf("BLUE_OFF\r\n");
                }
                else
                {
                    printf("Unknown Command!\r\n");
                }

                uart_rx_idx = 0;
                memset(uart_rx_buffer, 0, sizeof(uart_rx_buffer));
            }
            else if (uart_rx_data_byte == '\r')
            {
            }
            else
            {
                uart_rx_buffer[uart_rx_idx++] = uart_rx_data_byte;
            }
        }
        else
        {
            uart_rx_idx = 0;
            memset(uart_rx_buffer, 0, sizeof(uart_rx_buffer));

            printf("WARN: USART1 RX Buffer Overflow!\r\n");
        }

        HAL_UART_Receive_IT(&huart1, &uart_rx_data_byte, 1);
    }
}

// printf重定向
PUTCHAR_PROTOTYPE
{
    if (huart1.Instance != NULL)
    {
        HAL_UART_Transmit(&huart1, (uint8_t *)&ch, 1, HAL_MAX_DELAY);
    }
}
