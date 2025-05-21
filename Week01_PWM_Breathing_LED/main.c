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

typedef enum
{
    LED_MODE_ON,
    LED_MODE_OFF,
    LED_MODE_BREATHING
} ledmode_typedef_enum;

ledmode_typedef_enum current_led_mode = LED_MODE_OFF;

static void SystemClock_Config(void);

static void MX_GPIO_Init(void);
static void MX_USART1_Init(void);
static void MX_TIM2_PWM_Init(void);

static void LED1_Init(void);
static void LED1_Control(ledmode_typedef_enum mode, uint16_t brightness);

static void Error_Handler(void);

TIM_HandleTypeDef htim2;
UART_HandleTypeDef huart1;

uint8_t uart_rx_idx = 0;
uint8_t uart_rx_data_byte;
uint8_t uart_rx_buffer[32];

void main(void)
{
    HAL_Init();

    SystemClock_Config();

    MX_GPIO_Init();
    MX_USART1_Init();
    MX_TIM2_PWM_Init();

    LED1_Init();

    if (HAL_UART_Receive_IT(&huart1, &uart_rx_data_byte, 1) != HAL_OK)
    {
        Error_Handler();
    }

    printf("Please Enter the Command: \r\n");

    int8_t breath_dir = 1;
    uint16_t breath_duty = 0;

    while (1)
    {
        switch (current_led_mode)
        {
        case LED_MODE_ON:
            break;
        case LED_MODE_OFF:
            break;
        case LED_MODE_BREATHING:
            breath_duty += breath_dir * 10;

            if (breath_duty <= 0)
            {
                breath_duty = 0;
                breath_dir = 1;
            }
            else if (breath_duty >= htim2.Init.Period)
            {
                breath_duty = htim2.Init.Period;
                breath_dir = -1;
            }

            LED1_Control(LED_MODE_BREATHING, breath_duty);

            break;
        default:
            break;
        }

        HAL_Delay(30);
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

    GPIO_InitStruct.Pin = LED1_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(LED_GPIO_PORT, &GPIO_InitStruct);

    GPIO_InitStruct.Pin = USART1_TX_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(USART1_GPIO_PORT, &GPIO_InitStruct);

    GPIO_InitStruct.Pin = USART1_RX_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_INPUT;
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

static void MX_TIM2_PWM_Init(void)
{
    TIM_OC_InitTypeDef sConfigOC = {0};

    __HAL_RCC_TIM2_CLK_ENABLE();

    htim2.Instance = TIM2;
    htim2.Init.Prescaler = 72 - 1;
    htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim2.Init.Period = 1000 - 1;
    htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;

    if (HAL_TIM_PWM_Init(&htim2) != HAL_OK)
    {
        Error_Handler();
    }

    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = 0;
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;

    if (HAL_TIM_PWM_ConfigChannel(&htim2, &sConfigOC, TIM_CHANNEL_2) != HAL_OK)
    {
        Error_Handler();
    }
}

static void LED1_Init(void)
{
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_2);
    LED1_Control(LED_MODE_OFF, 0);
}

static void LED1_Control(ledmode_typedef_enum mode, uint16_t brightness)
{
    uint16_t pulse_value;
    uint16_t period = htim2.Init.Period;

    switch (mode)
    {
    case LED_MODE_ON:
        pulse_value = 0;
        break;
    case LED_MODE_OFF:
        pulse_value = period;
        break;
    case LED_MODE_BREATHING:
        brightness = (brightness > period) ? period : brightness;
        pulse_value = period - brightness;
        break;
    default:
        break;
    }

    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_2, pulse_value);
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

                if (strcmp(command, "LED_ON") == 0)
                {
                    current_led_mode = LED_MODE_ON;
                    LED1_Control(current_led_mode, 0);
                    printf("LED1 ON\r\n");
                }
                else if (strcmp(command, "LED_OFF") == 0)
                {
                    current_led_mode = LED_MODE_OFF;
                    LED1_Control(current_led_mode, 0);
                    printf("LED1 OFF\r\n");
                }
                else if (strcmp(command, "LED_BREATH") == 0)
                {
                    current_led_mode = LED_MODE_BREATHING;
                    printf("LED1 BREATHING\r\n");
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
