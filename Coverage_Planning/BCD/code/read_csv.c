// V. J. Hansen
// 06.05.2020
// https://codingboost.com/parsing-csv-files-in-c

#include <stdio.h>
#include <string.h>

int main(void) {
    FILE *fp = fopen("coordinates.csv", "r");
    if (!fp) {
        printf("Can't open file\n");
        return 0;
    }
    char buf[1024];
    int row_count, field_count = 0;
    while (fgets(buf, 1024, fp)) {
        field_count = 0;
        row_count++;
        if (row_count == 1) {
            continue;
        }
        char *field = strtok(buf, ",");
        while (field) {
            if (field_count == 0) {
                printf("Cell:\t");
            }
            if (field_count == 5) {
                printf("Z_s:\t");
            }
            if (field_count == 6) {
                    printf("Z_e:\t");
            }
            if (field_count == 7) {
                printf("X_s:\t");
            }
            if (field_count == 8) {
                printf("X_e:\t");
            }
            if (field_count >= 5 || field_count < 1 ) {
                printf("%s\n", field);
            }
            field = strtok(NULL, ",");
            field_count++;
        }
        printf("\n");
    }
    fclose(fp);
    return 0;
}