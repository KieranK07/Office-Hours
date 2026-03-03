#include "Student.h"
#include <iomanip>

// Initialize static member
int Student::nextTicketNumber = 1000;

// Default constructor
Student::Student() 
    : name(""), skillSet(""), arrivalTime(0), problemDescription(""), 
      severity(1), ticketNumber(nextTicketNumber++) {}

// Parameterized constructor
Student::Student(const std::string& name, const std::string& skillSet, 
                 int arrivalTime, const std::string& problemDescription, int severity)
    : name(name), skillSet(skillSet), arrivalTime(arrivalTime), 
      problemDescription(problemDescription), severity(severity), 
      ticketNumber(nextTicketNumber++) {
    
    // Validate severity range
    if (this->severity < 1) this->severity = 1;
    if (this->severity > 5) this->severity = 5;
}

// Getters
std::string Student::getName() const { return name; }
std::string Student::getSkillSet() const { return skillSet; }
int Student::getArrivalTime() const { return arrivalTime; }
std::string Student::getProblemDescription() const { return problemDescription; }
int Student::getSeverity() const { return severity; }
int Student::getTicketNumber() const { return ticketNumber; }

// Setters
void Student::setName(const std::string& name) { this->name = name; }
void Student::setSkillSet(const std::string& skillSet) { this->skillSet = skillSet; }
void Student::setArrivalTime(int time) { this->arrivalTime = time; }
void Student::setProblemDescription(const std::string& description) { 
    this->problemDescription = description; 
}
void Student::setSeverity(int severity) { 
    this->severity = severity;
    if (this->severity < 1) this->severity = 1;
    if (this->severity > 5) this->severity = 5;
}

// Display student information
void Student::display() const {
    std::cout << "┌─────────────────────────────────────────────────────────┐\n";
    std::cout << "│ Ticket #" << std::setw(6) << ticketNumber << std::setw(41) << "│\n";
    std::cout << "├─────────────────────────────────────────────────────────┤\n";
    std::cout << "│ Name: " << std::setw(49) << std::left << name << "│\n";
    std::cout << "│ Skill Set: " << std::setw(44) << std::left << skillSet << "│\n";
    std::cout << "│ Severity: " << std::setw(45) << std::left 
              << (std::string(severity, '*') + " (" + std::to_string(severity) + "/5)") << "│\n";
    std::cout << "│ Arrival Time: " << std::setw(42) << std::left << arrivalTime << "│\n";
    std::cout << "│ Problem: " << std::setw(46) << std::left 
              << (problemDescription.length() > 46 ? 
                  problemDescription.substr(0, 43) + "..." : problemDescription) << "│\n";
    std::cout << "└─────────────────────────────────────────────────────────┘\n";
}

// Comparison operators for priority queue
// Higher severity comes first; if equal severity, earlier arrival time comes first
bool Student::operator<(const Student& other) const {
    if (severity != other.severity) {
        return severity < other.severity;  // Lower severity = lower priority
    }
    return arrivalTime > other.arrivalTime;  // Later arrival = lower priority
}

bool Student::operator>(const Student& other) const {
    if (severity != other.severity) {
        return severity > other.severity;  // Higher severity = higher priority
    }
    return arrivalTime < other.arrivalTime;  // Earlier arrival = higher priority
}
