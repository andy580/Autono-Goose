#include <stdio.h>
#include <iostream>

int main() {

    FILE *serialPort = fopen("/dev/ttyACM0", "w");
    if (serialPort == NULL) {
        std::cout << "Error: Unable to connect to Arduino\n";
        return 1;
    }

    char command;
    while (!std::cin.eof()){
        std::cin >> command;
        fprintf(serialPort, "%c\n", command);
    }
    std::cout << "closing port" << std::endl;
    fclose(serialPort);

    

}