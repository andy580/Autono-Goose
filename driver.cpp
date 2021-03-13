#include <iostream>
#include <unistd.h>
#include <wait.h>
#include <vector>
#include <stdio.h>
// #include <fcntl.h>


int main(int argc, char **argv) {

    std::cout << "Driver Start\n";
    int py2cpp[2];
    pipe(py2cpp);

    pid_t python, cpp;

    // SO for starting 2 child processes of same parent
    // https://stackoverflow.com/questions/6542491/how-to-create-two-processes-from-a-single-parent
    (python = fork()) && (cpp = fork());

    if (cpp == 0) {
        // Child 1
        close(py2cpp[1]);
        dup2(py2cpp[0], STDIN_FILENO);
        close(py2cpp[0]);

        execvp("./steering", NULL);
        

    } else if (python == 0) {
        // Child 2
        close(py2cpp[0]);
        dup2(py2cpp[1], STDOUT_FILENO);
        close(py2cpp[1]);

        char* args[] = {"python3", "../pythonSim.py", NULL};
        execvp("python3", args);
    } 
    else {
        // Parent
        waitpid(python, 0, 0);
        waitpid(cpp, 0, 0);
    }

    std::cout << "Driver End" << "\n";

}