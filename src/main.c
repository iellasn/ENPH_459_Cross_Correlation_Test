#include "driver/adc.h"
#include "esp_log.h"

#define NUM_SAMPLES     1024
#define BURST_START     200   // start capturing at sample 200
#define BURST_LENGTH    20    // ~10 cycles at 2.5 samples/cycle
#define ADC_CHANNEL     ADC1_CHANNEL_0   // GPIO36 = VP pin

void app_main(void) {
    adc1_config_width(ADC_WIDTH_BIT_12);
    adc1_config_channel_atten(ADC_CHANNEL, ADC_ATTEN_DB_11);

    int samples[NUM_SAMPLES] = {0};  // initialize all to zero

    // only sample during the burst window
    for (int i = BURST_START; i < BURST_START + BURST_LENGTH; i++) {
        samples[i] = adc1_get_raw(ADC_CHANNEL);
    }

    // print all samples including the zeros
    for (int i = 0; i < NUM_SAMPLES; i++) {
        printf("%d\n", samples[i]);
    }
}