#include "stm32f10x.h"

int main(void)
{
    RCC_APB2ENR |= 0x4;

    GPIOA_CRL |= (1 << 4 * 1);
    GPIOA_CRL |= (1 << 4 * 2);
    GPIOA_CRL |= (1 << 4 * 3);

    while (1)
    {
    }

    return 0;
}
