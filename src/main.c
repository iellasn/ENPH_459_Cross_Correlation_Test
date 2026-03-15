#include "driver/adc.h"
#include "esp_log.h"

#define NUM_SAMPLES 1024
#define ADC_CHANNEL ADC1_CHANNEL_0  // GPIO36

void app_main(void) {
    // 1. Configure ADC
    adc1_config_width(ADC_WIDTH_BIT_12);
    adc1_config_channel_atten(ADC_CHANNEL, ADC_ATTEN_DB_11); // 0-3.3V range

    // 2. Sample into buffer
    int samples[NUM_SAMPLES];
    for (int i = 0; i < NUM_SAMPLES; i++) {
        samples[i] = adc1_get_raw(ADC_CHANNEL);
    }

    // 3. Print over serial
    for (int i = 0; i < NUM_SAMPLES; i++) {
        printf("%d\n", samples[i]);
    }
}