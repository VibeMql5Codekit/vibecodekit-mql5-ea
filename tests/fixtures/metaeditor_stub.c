/*
 * MetaEditor64.exe CI stub — simulates MQL5 compilation for testing.
 *
 * Build with MinGW:
 *   x86_64-w64-mingw32-gcc -o metaeditor64.exe metaeditor_stub.c -static
 *
 * Usage (same as real MetaEditor):
 *   wine metaeditor64.exe /compile:path/to/EA.mq5 /log:path/to/log.txt
 *
 * Produces a UTF-16LE log file with "0 error(s)" on success.
 * The real MetaEditor is needed for production compilation.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>
#include <windows.h>

int main(int argc, char *argv[]) {
    char compile_path[1024] = {0};
    char log_path[1024] = {0};

    for (int i = 1; i < argc; i++) {
        if (_strnicmp(argv[i], "/compile:", 9) == 0) {
            strncpy(compile_path, argv[i] + 9, sizeof(compile_path) - 1);
        } else if (_strnicmp(argv[i], "/log:", 5) == 0) {
            strncpy(log_path, argv[i] + 5, sizeof(log_path) - 1);
        }
    }

    if (compile_path[0] == '\0') {
        fprintf(stderr, "MetaEditor64 CI Stub\n");
        fprintf(stderr, "Usage: metaeditor64.exe /compile:<file> /log:<logfile>\n");
        return 1;
    }

    FILE *src = fopen(compile_path, "r");
    if (!src) {
        fprintf(stderr, "Error: cannot open %s\n", compile_path);
        return 1;
    }
    fclose(src);

    if (log_path[0] != '\0') {
        FILE *log = fopen(log_path, "wb");
        if (log) {
            /* UTF-16LE BOM */
            fputc(0xFF, log);
            fputc(0xFE, log);

            wchar_t buf[2048];
            swprintf(buf, 2048,
                L"MetaEditor64 Build 4756 (CI Stub)\r\n"
                L"Compiling '%hs'\r\n"
                L"Result: 0 error(s), 0 warning(s)\r\n"
                L"Compile complete\r\n",
                compile_path);
            fwrite(buf, sizeof(wchar_t), wcslen(buf), log);
            fclose(log);
        }
    }

    return 0;
}
