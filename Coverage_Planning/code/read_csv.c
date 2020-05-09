// https://codingboost.com/parsing-csv-files-in-c
// V. J. Hansen, 09.05.20


#include <stdio.h>
#include <string.h>

void process_field(int field_count, char *value) {
    if (field_count == 0) {
        printf("Cell:\t");
        //printf("%s\n", value);
    }
    if (field_count == 1) {
        printf("Z:\t");
        // z[]=value
        //printf("%s\n", value);
    }
    if (field_count == 2) {
        // xs[]=value
        printf("Xs:\t");
        printf("%s\n", value);
    }
    if (field_count == 3) {
        // xe[] = value
        printf("Xe:\t");
    }
}

int main(void) {
    char buf[1024];
    char token[1024];
    int row_count = 0, field_count = 0, in_double_quotes = 0;
    int token_pos = 0, i = 0;
    FILE *fp = fopen("waypoints.csv", "r");
    if (!fp) {
        printf("Can't open file\n");
        return 0;
    }
    while (fgets(buf, 1024, fp)) {
        row_count++;
        if (row_count == 1) {
            continue;
        }
        field_count = i = 0;
        do {
            token[token_pos++] = buf[i];
            if (!in_double_quotes && (buf[i] == ',' || buf[i] == '\n')) {
                token[token_pos - 1] = 0;
                token_pos = 0;
                process_field(field_count++, token);
            }
            if (buf[i] == '"' && buf[i + 1] != '"') {
                token_pos--;
                in_double_quotes = !in_double_quotes;
            }
            if (buf[i] == '"' && buf[i + 1] == '"')
                i++;
        } while (buf[++i]);
        printf("\n");
    }
    fclose(fp);
    return 0;
}