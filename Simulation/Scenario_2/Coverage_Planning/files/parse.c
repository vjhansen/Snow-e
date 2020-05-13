
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CELLS 5
static double Z_BCD[CELLS][200];
static double X_BCD[CELLS][200];
static int len_Z[CELLS];
static int len_X[CELLS];

void process_field(int field_count, char *value, int row_count) {
    // - Z coordinates
    if (field_count == 1) {
        for (int i = 0; i < strlen(value); ++i) {
          if (value[i] != ',') {
            Z_BCD[row_count][i] = atof(&value[i]);
            len_Z[row_count] = i;
          }
        }
    }
    // - X coordinates
    if (field_count == 2) {
        for (int i = 0; i < strlen(value); ++i) {
            X_BCD[row_count][i] = atof(&value[i]);
            len_X[row_count] = i;
        }
    }
}

// based on: https://codingboost.com/parsing-csv-files-in-c
// https://stackoverflow.com/questions/2620146/how-do-i-return-multiple-values-from-a-function-in-c
void process_file() {
    char buf[1024];
    char token[1024];
    int row_count = 0, field_count = 0, in_double_quotes = 0;
    int token_pos = 0, i = 0, cell_cnt = 0;
    FILE *fp = fopen("/x_waypoints.txt", "r");
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
            if (!in_double_quotes && (buf[i] == '\n' || buf[i] == ',' || buf[i] == ' ')) {
                token[token_pos - 1] = 0;
                token_pos = 0;
                process_field(field_count++, token, cell_cnt);
            }
            else if (buf[i] == '"' && buf[i + 1] != '"') {
                token_pos--;
                in_double_quotes = !in_double_quotes;
            }
            else if ((buf[i] == '[' && buf[i + 1] != '[') || (buf[i] == ']' && buf[i + 1] != ']')) {
                token_pos--;
            }
            else if (buf[i] == '"' && buf[i + 1] == '"') {
              i++;
            }

        } while (buf[++i]);
    }
    for (int i = 0; i < len_Z[4]; ++i) {
      printf("%.2f ", Z_BCD[4][i]);
    }
    fclose(fp);
}


int main () {
  process_file();
  return 0;
}
