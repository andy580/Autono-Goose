#include <iostream>
#include <sstream>
#include <unistd.h>
#include <string>

int main(){

    std::string command;
    
    while(!std::cin.eof()) {
        std::getline(std::cin, command); 
        std::cout << "Steering Command: \n";                                        
        std::cout << command <<std::endl;
    }

  return 0;
}