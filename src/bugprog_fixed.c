#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("Usage: %s <number>\n", argv[0]);
        return 0;
    }

    int x = atoi(argv[1]);
    
/* AUTO-PATCH (template): add guard for division-by-zero */
if (x == 0) {
    printf("Input was 0, auto-patched to avoid division.\n");
    return 1;
}


    // BUG: if x == 0 we print "CRASH" and abort (simulates a failure)
    if (x == 0) {
        puts("CRASH");
        abort();
    }

    int y = 10 / x; // safe when x != 0
    printf("Result: %d\n", y);
    return 0;
}
