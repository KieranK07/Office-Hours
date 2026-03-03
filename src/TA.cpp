#include "TA.h"
#include <algorithm>
#include <iomanip>

// Default constructor
TA::TA() 
    : name(""), isAvailable(true), currentStudent(nullptr), 
      studentsHelped(0), totalWaitTime(0) {}

// Parameterized constructor
TA::TA(const std::string& name, const std::vector<std::string>& skillSets)
    : name(name), skillSets(skillSets), isAvailable(true), 
      currentStudent(nullptr), studentsHelped(0), totalWaitTime(0) {}

// Destructor
TA::~TA() {
    // Note: We don't delete currentStudent as it's managed elsewhere
    currentStudent = nullptr;
}

// Getters
std::string TA::getName() const { return name; }
std::vector<std::string> TA::getSkillSets() const { return skillSets; }
bool TA::getIsAvailable() const { return isAvailable; }
Student* TA::getCurrentStudent() const { return currentStudent; }
int TA::getStudentsHelped() const { return studentsHelped; }

double TA::getAverageWaitTime() const {
    if (studentsHelped == 0) return 0.0;
    return static_cast<double>(totalWaitTime) / studentsHelped;
}

// Setters
void TA::setName(const std::string& name) { this->name = name; }

void TA::addSkillSet(const std::string& skillSet) {
    if (std::find(skillSets.begin(), skillSets.end(), skillSet) == skillSets.end()) {
        skillSets.push_back(skillSet);
    }
}

void TA::setAvailable(bool available) { this->isAvailable = available; }

// Check if TA has a specific skill set
bool TA::hasSkillSet(const std::string& skillSet) const {
    return std::find(skillSets.begin(), skillSets.end(), skillSet) != skillSets.end();
}

// Check if TA can help a specific student
bool TA::canHelp(const Student& student) const {
    if (!isAvailable) return false;
    return hasSkillSet(student.getSkillSet());
}

// Assign a student to this TA
void TA::assignStudent(Student* student, int currentTime) {
    if (student == nullptr) return;
    
    currentStudent = student;
    isAvailable = false;
    studentsHelped++;
    
    // Calculate wait time
    int waitTime = currentTime - student->getArrivalTime();
    totalWaitTime += waitTime;
    
    std::cout << "\n✓ " << name << " is now helping " << student->getName() 
              << " (Ticket #" << student->getTicketNumber() << ")\n";
    std::cout << "  Wait time: " << waitTime << " minutes\n";
}

// Mark that TA has finished with current student
void TA::finishWithStudent() {
    if (currentStudent != nullptr) {
        std::cout << "\n✓ " << name << " finished helping " 
                  << currentStudent->getName() << "\n";
        currentStudent = nullptr;
    }
    isAvailable = true;
}

// Display TA information
void TA::display() const {
    std::cout << "┌─────────────────────────────────────────────────────────┐\n";
    std::cout << "│ TA: " << std::setw(51) << std::left << name << "│\n";
    std::cout << "├─────────────────────────────────────────────────────────┤\n";
    std::cout << "│ Status: " << std::setw(47) << std::left 
              << (isAvailable ? "Available" : "Busy") << "│\n";
    std::cout << "│ Skill Sets: " << std::setw(43) << std::left;
    
    if (skillSets.empty()) {
        std::cout << "None" << std::setw(39) << " " << "│\n";
    } else {
        std::string skillsStr;
        for (size_t i = 0; i < skillSets.size(); ++i) {
            skillsStr += skillSets[i];
            if (i < skillSets.size() - 1) skillsStr += ", ";
        }
        if (skillsStr.length() > 43) {
            skillsStr = skillsStr.substr(0, 40) + "...";
        }
        std::cout << skillsStr << std::setw(43 - skillsStr.length()) << " " << "│\n";
    }
    
    if (!isAvailable && currentStudent != nullptr) {
        std::cout << "│ Currently helping: " << std::setw(36) << std::left 
                  << currentStudent->getName() << "│\n";
    }
    std::cout << "└─────────────────────────────────────────────────────────┘\n";
}

// Display TA statistics
void TA::displayStats() const {
    std::cout << "┌─────────────────────────────────────────────────────────┐\n";
    std::cout << "│ TA Statistics - " << std::setw(39) << std::left << name << "│\n";
    std::cout << "├─────────────────────────────────────────────────────────┤\n";
    std::cout << "│ Students Helped: " << std::setw(39) << std::left 
              << studentsHelped << "│\n";
    std::cout << "│ Average Wait Time: " << std::setw(37) << std::left 
              << (std::to_string(static_cast<int>(getAverageWaitTime())) + " minutes") << "│\n";
    std::cout << "└─────────────────────────────────────────────────────────┘\n";
}
