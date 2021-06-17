#include <stdio.h>
#include <iostream>
#include <unistd.h>
#include <limits>

int main() {

    FILE *serialPort = fopen("/dev/ttyACM0", "w");
    if (serialPort == NULL) {
        std::cout << "Error: Unable to connect to Arduino\n";
        return 1;
    }

    char command;
    bool brakeEngaged = true;

    while (!std::cin.eof()){
        fflush(stdin);
        std::cin.clear();
        // std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        // std::cin.sync();
        
        std::cin >> command;
        if (command == 'g' && brakeEngaged==false) {
            fprintf(serialPort, "%c\n", command);
            std::cin >> command;
            // sleep(4);
            brakeEngaged = true;
        } else if(command == 's' && brakeEngaged==true) {
            fprintf(serialPort, "%c\n", command);
            // sleep(4);
            std::cin >> command;
            brakeEngaged = false;            
        }
        std::cout << command;

    }

    std::cout << "closing port" << std::endl;
    fclose(serialPort);

    

}