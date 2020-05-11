// https://codingboost.com/parsing-csv-files-in-c
// V. J. Hansen, 10.05.20

// add to makefile: this has to be compiled/linked with zig_zag_gps.c

#include <stdio.h>
#include <string.h>
//#include "read_csv.h"



void process_field(int field_count, char *value, int row_count) {
    // - Z coordinates
    if (field_count == 1) {
        printf("\nZ:\t");
        for (int i = 0; i < strlen(value); ++i) {
            z[row_count][i] = value[i];
            len_z[row_count] = i;
        }
    }
    // - X start coordinates
    if (field_count == 2) {
        for (int i = 0; i < strlen(value); ++i) {
            xs[row_count][i] = value[i];
            len_xs[row_count] = i;
        }
    }
    // - X end coordinates
    if (field_count == 3) {
        for (int i = 0; i < strlen(value); ++i) {
            xe[row_count][i] = value[i];
            len_xe[row_count] = i;
        }
    }
}


void process_file() {
  char buf[1024];
    char token[1024];
    int row_count = 0, field_count = 0, in_double_quotes = 0;
    int token_pos = 0, i = 0, cell_cnt = 0;
    FILE *fp = fopen("files/waypoints.csv", "r");
    if (!fp) {
        printf("Can't open file\n");
    }
    while (fgets(buf, 1024, fp)) {
        row_count++;
        
        if (row_count == 1) {
            continue;
        }
        cell_cnt++;
        field_count = i = 0;
        do {
            token[token_pos++] = buf[i];
            if (!in_double_quotes && (buf[i] == ',' || buf[i] == '\n' || buf[i] == ']')) {
                token[token_pos - 1] = 0;
                token_pos = 0;          
                process_field(field_count++, token, cell_cnt);
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
    // test
    for (int i = 0; i < len_z[1]; ++i) {
        printf("%c",z[1][i]);  
    }
    printf("\n");  
    fclose(fp);
}


int main(void) {
    process_file();
    return 0;
}