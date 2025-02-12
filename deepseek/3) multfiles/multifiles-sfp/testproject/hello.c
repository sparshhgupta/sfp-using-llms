#include <stdio.h>

int main() {
    int x = 10  // Missing semicolon (Syntax Error)
    int y;  
    
    printf("Value of y: %d\n", y);  // Might print garbage value

    return 0;
}
