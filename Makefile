# Makefile for Office Hours Triage System
# Compiler and flags
CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra -pedantic -g -Isrc

# Source directory
SRC_DIR = src

# Target executable
TARGET = officehours

# Source files
SOURCES = $(SRC_DIR)/officehours.cpp $(SRC_DIR)/Student.cpp $(SRC_DIR)/TA.cpp $(SRC_DIR)/OfficeHoursSystem.cpp

# Object files
OBJECTS = $(SOURCES:$(SRC_DIR)/%.cpp=%.o)

# Header files
HEADERS = $(SRC_DIR)/Student.h $(SRC_DIR)/TA.h $(SRC_DIR)/OfficeHoursSystem.h

# Default target
all: $(TARGET)

# Link object files to create executable
$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJECTS)
	@echo "Build complete! Run with: ./$(TARGET)"

# Compile source files to object files
%.o: $(SRC_DIR)/%.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean build artifacts
clean:
	rm -f $(OBJECTS) $(TARGET)
	@echo "Clean complete!"

# Clean and rebuild
rebuild: clean all

# Run the program
run: $(TARGET)
	./$(TARGET)

# Help target
help:
	@echo "Office Hours Triage System - Makefile"
	@echo "Usage:"
	@echo "  make          - Build the project"
	@echo "  make clean    - Remove build artifacts"
	@echo "  make rebuild  - Clean and rebuild"
	@echo "  make run      - Build and run the program"
	@echo "  make help     - Display this help message"

# Phony targets
.PHONY: all clean rebuild run help
