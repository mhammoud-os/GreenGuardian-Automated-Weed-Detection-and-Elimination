#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "hardware/clocks.h"

float clockDiv = 64;
float wrap = 39062;
int TurningPin= 0;


void setMillis(int servoPin, float millis)
{
    pwm_set_gpio_level(servoPin, (millis/20000.f)*wrap);
}

void setServo(int servoPin, float startMillis)
{
    gpio_set_function(TurningPin, GPIO_FUNC_PWM);
    uint slice_num = pwm_gpio_to_slice_num(servoPin);

    pwm_config config = pwm_get_default_config();
    
    uint64_t clockspeed = clock_get_hz(5);
    clockDiv = 64;
    wrap = 39062;

    while (clockspeed/clockDiv/50 > 65535 && clockDiv < 256) clockDiv += 64; 
    wrap = clockspeed/clockDiv/50;

    pwm_config_set_clkdiv(&config, clockDiv);
    pwm_config_set_wrap(&config, wrap);

    pwm_init(slice_num, &config, true);

    setMillis(servoPin, startMillis);
}

int main() {
    setServo(TurningPin, 1400);

    //Initialise I/O
    stdio_init_all();

    char userInput;
    const uint en1 = 6;
    const uint en2 = 7;
    const uint in1= 2;
    const uint in2= 3;
    const uint in3= 4;
    const uint in4= 5;
    gpio_init(en1);
    gpio_init(en2);
    gpio_init(in1);
    gpio_init(in2);
    gpio_init(in3);
    gpio_init(in4);
    
    gpio_set_dir(en1, GPIO_OUT);
    gpio_set_dir(en2, GPIO_OUT);
    gpio_set_dir(in1, GPIO_OUT);
    gpio_set_dir(in2, GPIO_OUT);
    gpio_set_dir(in3, GPIO_OUT);
    gpio_set_dir(in4, GPIO_OUT);
    gpio_put(en1, 1);
    gpio_put(en2, 1);
    gpio_put(in1, 1);
    gpio_put(in2, 0);
    gpio_put(in3, 1);
    gpio_put(in4, 0);
    printf("Command (0 = left, 1 = up, 2 = right, 3 = down, 4 = stop turning, 5 = stop moving):\n");
    while (true) {
        //Get User Input
        userInput = getchar();

        if(userInput == '0'){
	    setMillis(TurningPin, 400);
            printf("Turning Left\n");
        }
        else if(userInput == '1'){
	    gpio_put(en1, 1);
	    gpio_put(in1, 1);
	    gpio_put(in2, 0);
            printf("Moving Forward\n");
        }
        else if(userInput == '2'){
	    setMillis(TurningPin, 2400);
            printf("Turning Right\n");
        }
        else if(userInput == '3'){
	    gpio_put(en1, 1);
	    gpio_put(in1, 0);
	    gpio_put(in2, 1);
            printf("Moving Backward\n");
        }
        else if(userInput == '4'){
	    setMillis(TurningPin, 1400);
            printf("Stoping Turn\n");
	}
        else if(userInput == '5'){
	    gpio_put(en1, 0);
	    gpio_put(in1, 0);
	    gpio_put(in2, 0);
            printf("Stoping \n");
        }
        else if(userInput == '6'){
	    gpio_put(en2, 1);
	    gpio_put(in3, 1);
	    gpio_put(in4, 0);
            printf("Starting Spray \n");
        }
        else if(userInput == '5'){
	    gpio_put(en2, 0);
	    gpio_put(in3, 0);
	    gpio_put(in4, 0);
            printf("Stoping spray \n");
        }
        else{
            printf("Invalid Input!\n");
        }

    }
}




