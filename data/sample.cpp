#include <iostream>

int main() {
    int counter = 0, limit = 5, test = 0, test1 = 5;
    do {
        counter++;
        do {
            test++;
            do {
                test1--;
            } while (test1 > 0);
        } while (test < 5);
    } while (counter < limit);
}
