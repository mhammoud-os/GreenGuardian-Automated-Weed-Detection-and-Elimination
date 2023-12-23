#include <stdio.h>
#include "pico/stdlib.h"

int main() {
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
    gpio_set_dir(in1, GPIO_OUT);
    gpio_set_dir(in2, GPIO_OUT);
    gpio_set_dir(in3, GPIO_OUT);
    gpio_set_dir(in4, GPIO_OUT);
    gpio_put(en1, 1);
    gpio_put(en2, 1);
    gpio_put(in1, 1);
    gpio_put(in2, 0);
    gpio_put(in1, 1);
    gpio_put(in2, 0);
    printf("Command (0 = left, 1 = up, 2 = right, 3 = down, 4 = stop turning, 5 = stop moving):\n");
    while (true) {
        //Get User Input
        userInput = getchar();

        if(userInput == '0'){
	    gpio_put(en2, 1);
	    gpio_put(in3, 1);
	    gpio_put(in4, 0);
            printf("Turning Left\n");
        }
        else if(userInput == '1'){
	    gpio_put(en1, 1);
	    gpio_put(in1, 1);
	    gpio_put(in2, 0);
            printf("Moving Forward\n");
        }
        else if(userInput == '2'){
	    gpio_put(en2, 1);
	    gpio_put(in3, 0);
	    gpio_put(in4, 1);
            printf("Turning Right\n");
        }
        else if(userInput == '3'){
	    gpio_put(en1, 1);
	    gpio_put(in1, 0);
	    gpio_put(in2, 1);
            printf("Moving Backward\n");
        }
        else if(userInput == '4'){
	    gpio_put(en2, 0);
	    gpio_put(in3, 0);
	    gpio_put(in4, 0);
            printf("Stoping Turn\n");
	}
        else if(userInput == '5'){
	    gpio_put(en1, 0);
	    gpio_put(in1, 0);
	    gpio_put(in2, 0);
            printf("Stoping \n");
        }
        else{
            printf("Invalid Input!\n");
        }

    }
}
