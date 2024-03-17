#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "hardware/clocks.h"
#include "math.h"


const int TRIG_PIN = 17;
const int ECHO_PIN = 16;


float clockDiv = 64;
float wrap = 39062;
int TurningPin= 14;

int sprayingPin= 15;

const uint encoder = 13;

const uint LED_PIN = PICO_DEFAULT_LED_PIN;
char userInput;
const uint en2 = 7;
const uint in1= 2;
const uint in2= 3;

void setMillis(int servoPin, float millis)
{
    pwm_set_gpio_level(servoPin, (millis/20000.f)*wrap);
}

void setServo(int servoPin, float startMillis)
{
    gpio_set_function(servoPin, GPIO_FUNC_PWM);
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

int pulseIn(int pin, int level, int timeout)
{
   int tn;
   int t0;
   int t1;
   long micros;
   t0 = time_us_64();
   micros = 0;
   while (gpio_get(pin) != level)
   {
      tn = time_us_64();
      if (tn/1000000 > t0/1000000) micros = 1000000L; else micros = 0;
      micros += (tn - t0);
      if (micros > timeout) return 0;
   }
   t1 = time_us_64();
   while (gpio_get(pin) == level)
   {
   tn = time_us_64();
      if (tn/1000000 > t0/1000000) micros = 1000000L; else micros = 0;
      micros = micros + (tn - t0);
      if (micros > timeout) return 0;
   }
   if (tn/1000000 > t1/1000000) micros = 1000000L; else micros = 0;
   micros = micros + (tn - t1);
   return micros;
}

void setup() {
	//Initialise I/O
	stdio_init_all();

	gpio_init(TRIG_PIN);
	gpio_init(ECHO_PIN);
	gpio_set_dir(TRIG_PIN,GPIO_OUT);
	gpio_set_dir(ECHO_PIN,GPIO_IN);

	setServo(TurningPin, 1400);
	setServo(sprayingPin, 1400);


	gpio_init(encoder);
	gpio_set_dir(encoder,GPIO_IN);

	gpio_init(LED_PIN);
	gpio_set_dir(LED_PIN, GPIO_OUT);

	gpio_init(en2);
	gpio_init(in1);
	gpio_init(in2);

	gpio_set_dir(en2, GPIO_OUT);
	gpio_set_dir(in1, GPIO_OUT);
	gpio_set_dir(in2, GPIO_OUT);
	gpio_put(en2, 1);
	gpio_put(in1, 0);
	gpio_put(in2, 0);
	printf("Command (0 = left, 1 = up, 2 = right, 3 = down, 4 = stop turning, 5 = stop moving):\n");
}
int main() {
    setup();
    while (1) {
        //Get User Input
        userInput = getchar();

        if(userInput == '0'){
	    setMillis(TurningPin, 1000);
            printf("Turning Left\n");
        }
        else if(userInput == '1'){
	    gpio_put(in1, 1);
	    gpio_put(in2, 0);
            printf("Moving Forward\n");
        }
        else if(userInput == '2'){
	    setMillis(TurningPin, 1800);
            printf("Turning Right\n");
        }
        else if(userInput == '3'){
	    gpio_put(in1, 0);
	    gpio_put(in2, 1);
            printf("Moving Backward\n");
        }
        else if(userInput == '4'){
	    setMillis(TurningPin, 1403);
	   
            printf("Stoping Turn\n");
	}
        else if(userInput == '5'){
	    gpio_put(in1, 0);
	    gpio_put(in2, 0);
            printf("Stoping \n");
        }
        else if(userInput == '6'){
	    gpio_put(en2, 0);
	    gpio_put(LED_PIN, 1);
            printf("Starting Spray \n");
        }
        else if(userInput == '7'){
	    gpio_put(en2, 1);
	    gpio_put(LED_PIN, 0);
            printf("Stoping spray \n");
        }
	else if(userInput == '8'){
		printf("StartPrinting out the number, press q to stop\n");
		userInput = getchar();
		char numberChar[50] = ""; 
		while(userInput != 'q'){
			char str[2] = {userInput, '\0'};
			printf(str);
			strcat(numberChar, str);
			userInput = getchar();
		}
		char *output;
		int number = strtol(numberChar, &output, 10);
		setMillis(sprayingPin, number);
		printf("Moving Sprayer\n");
		printf(numberChar);
	}
	else if (userInput =='m'){
		printf("Moving Forward Amount, press q to stop\n");
		userInput = getchar();
		char numberChar[50] = ""; 
		while(userInput != 'q'){
			char str[2] = {userInput, '\0'};
			printf(str);
			strcat(numberChar, str);
			userInput = getchar();
		}
		char *output;
		int number = strtol(numberChar, &output, 10);
		printf("Moving forward\n");
		printf(numberChar);

		int stateCurrent = 0;
		int stateLast = 1;
		int stateCount = 0;
		//int statesPerRotation = 40;
		//int distancePerRotation = 22;


		gpio_put(in1, 1);
		gpio_put(in2, 0);
		printf("Moving Forward\n");
		//number = round((number/distancePerRotation)*statesPerRotation);
		while(stateCount < number){
		    stateCurrent =gpio_get(encoder);
		    if (stateCurrent != stateLast){
			    stateLast = stateCurrent;
			    stateCount += 1;
		    }
		    sleep_ms(10);
		}
		gpio_put(in1, 0);
		gpio_put(in2, 0);
		printf("Stoping \n");
	
	}
	else if (userInput =='f'){
		long duration, distanceCm;
		gpio_put(TRIG_PIN, 0);
		sleep_ms(2);
		gpio_put(TRIG_PIN, 1);
		sleep_ms(10);
		gpio_put(TRIG_PIN, 0);
		duration = pulseIn(ECHO_PIN, 1, 60*220);

		// convert the time into a distance
		distanceCm = duration / 29.1 / 2 ;

		if (distanceCm <= 0){
			printf("0\n");
		}
		else {
			printf("%d\n", distanceCm);
		}
	}
        else{
            printf("Invalid Input!\n");
        }

    }
}
