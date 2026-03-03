@echo off
REM Build script for Windows (Office Hours Triage System)

echo Building Office Hours Triage System...
echo.

REM Compile all source files from src/ directory
g++ -std=c++11 -Wall -Wextra -pedantic -g -c src/Student.cpp -o Student.o
g++ -std=c++11 -Wall -Wextra -pedantic -g -c src/TA.cpp -o TA.o
g++ -std=c++11 -Wall -Wextra -pedantic -g -c src/OfficeHoursSystem.cpp -o OfficeHoursSystem.o
g++ -std=c++11 -Wall -Wextra -pedantic -g -c src/officehours.cpp -o officehours.o

REM Link all object files
g++ -std=c++11 -Wall -Wextra -pedantic -g -o officehours.exe Student.o TA.o OfficeHoursSystem.o officehours.o

echo.
echo Build complete! Run with: officehours.exe
echo.
pause
