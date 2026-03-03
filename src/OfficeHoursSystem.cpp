#include "OfficeHoursSystem.h"
#include <iostream>
#include <iomanip>
#include <algorithm>

// Constructor
OfficeHoursSystem::OfficeHoursSystem() 
    : currentTime(0), totalStudentsProcessed(0), totalStudentsInSystem(0) {}

// Destructor
OfficeHoursSystem::~OfficeHoursSystem() {
    // Clean up arrival queue
    while (!arrivalQueue.empty()) {
        delete arrivalQueue.front();
        arrivalQueue.pop();
    }
    
    // Clean up skill set queues
    for (auto& pair : skillSetQueues) {
        while (!pair.second.empty()) {
            delete pair.second.top();
            pair.second.pop();
        }
    }
    
    // Clean up TAs
    for (TA* ta : taList) {
        delete ta;
    }
}

// Add a new student to the system
void OfficeHoursSystem::addStudent(const std::string& name, const std::string& skillSet, 
                                   const std::string& problemDescription, int severity) {
    Student* newStudent = new Student(name, skillSet, currentTime, problemDescription, severity);
    arrivalQueue.push(newStudent);
    totalStudentsInSystem++;
    
    std::cout << "\n✓ Student added to arrival queue:\n";
    newStudent->display();
}

// Add a new TA to the system
void OfficeHoursSystem::addTA(const std::string& name, const std::vector<std::string>& skillSets) {
    TA* newTA = new TA(name, skillSets);
    taList.push_back(newTA);
    
    std::cout << "\n✓ TA added to system:\n";
    newTA->display();
}

// Process arrival queue - move students to skill set queues
void OfficeHoursSystem::processArrivalQueue() {
    while (!arrivalQueue.empty()) {
        Student* student = arrivalQueue.front();
        arrivalQueue.pop();
        
        std::string skillSet = student->getSkillSet();
        
        // Initialize skill set queue if it doesn't exist
        if (skillSetQueues.find(skillSet) == skillSetQueues.end()) {
            skillSetQueues[skillSet] = std::priority_queue<Student*, 
                                       std::vector<Student*>, StudentPtrComparator>();
        }
        
        skillSetQueues[skillSet].push(student);
        std::cout << "  → " << student->getName() << " moved to " 
                  << skillSet << " queue\n";
    }
}

// Find an available TA with the required skill set
TA* OfficeHoursSystem::findAvailableTA(const std::string& skillSet) {
    for (TA* ta : taList) {
        if (ta->getIsAvailable() && ta->hasSkillSet(skillSet)) {
            return ta;
        }
    }
    return nullptr;
}

// Assign students from skill set queues to available TAs
void OfficeHoursSystem::assignStudentsToTAs() {
    for (auto& pair : skillSetQueues) {
        std::string skillSet = pair.first;
        auto& queue = pair.second;
        
        while (!queue.empty()) {
            TA* availableTA = findAvailableTA(skillSet);
            
            if (availableTA == nullptr) {
                break;  // No available TA for this skill set
            }
            
            Student* student = queue.top();
            queue.pop();
            availableTA->assignStudent(student, currentTime);
        }
    }
}

// Complete current student for a specific TA
void OfficeHoursSystem::completeCurrentStudent(const std::string& taName) {
    for (TA* ta : taList) {
        if (ta->getName() == taName) {
            if (ta->getCurrentStudent() != nullptr) {
                Student* completedStudent = ta->getCurrentStudent();
                delete completedStudent;  // Clean up the student
                ta->finishWithStudent();
                totalStudentsProcessed++;
                totalStudentsInSystem--;
                return;
            } else {
                std::cout << "\n✗ " << taName << " is not currently helping anyone.\n";
                return;
            }
        }
    }
    std::cout << "\n✗ TA '" << taName << "' not found.\n";
}

// Advance system time
void OfficeHoursSystem::advanceTime(int minutes) {
    currentTime += minutes;
    std::cout << "\n⏰ Time advanced to " << currentTime << " minutes\n";
}

// Process the entire system - arrival queue and assignment
void OfficeHoursSystem::processSystem() {
    std::cout << "\n════════════════════════════════════════════════════════\n";
    std::cout << "Processing Office Hours System...\n";
    std::cout << "════════════════════════════════════════════════════════\n";
    
    processArrivalQueue();
    assignStudentsToTAs();
    
    std::cout << "\n✓ System processing complete\n";
}

// Getters
int OfficeHoursSystem::getCurrentTime() const { return currentTime; }

int OfficeHoursSystem::getQueueSize(const std::string& skillSet) const {
    auto it = skillSetQueues.find(skillSet);
    if (it != skillSetQueues.end()) {
        return it->second.size();
    }
    return 0;
}

int OfficeHoursSystem::getTotalQueueSize() const {
    int total = arrivalQueue.size();
    for (const auto& pair : skillSetQueues) {
        total += pair.second.size();
    }
    return total;
}

int OfficeHoursSystem::getArrivalQueueSize() const {
    return arrivalQueue.size();
}

// Display all queues
void OfficeHoursSystem::displayAllQueues() const {
    std::cout << "\n╔═════════════════════════════════════════════════════════╗\n";
    std::cout << "║              OFFICE HOURS QUEUE STATUS                 ║\n";
    std::cout << "╠═════════════════════════════════════════════════════════╣\n";
    std::cout << "║ Current Time: " << std::setw(41) << std::left 
              << (std::to_string(currentTime) + " minutes") << "║\n";
    std::cout << "╠═════════════════════════════════════════════════════════╣\n";
    
    // Arrival Queue
    std::cout << "║ ARRIVAL QUEUE: " << std::setw(40) << std::left 
              << (std::to_string(arrivalQueue.size()) + " students") << "║\n";
    
    // Skill Set Queues
    std::cout << "╠═════════════════════════════════════════════════════════╣\n";
    std::cout << "║ SKILL SET QUEUES:                                      ║\n";
    
    if (skillSetQueues.empty()) {
        std::cout << "║   (No queues yet)                                      ║\n";
    } else {
        for (const auto& pair : skillSetQueues) {
            std::string line = "  • " + pair.first + ": " + 
                             std::to_string(pair.second.size()) + " students";
            std::cout << "║ " << std::setw(54) << std::left << line << "║\n";
        }
    }
    
    std::cout << "╚═════════════════════════════════════════════════════════╝\n";
}

// Display TA status
void OfficeHoursSystem::displayTAStatus() const {
    std::cout << "\n╔═════════════════════════════════════════════════════════╗\n";
    std::cout << "║                   TA STATUS BOARD                      ║\n";
    std::cout << "╚═════════════════════════════════════════════════════════╝\n\n";
    
    if (taList.empty()) {
        std::cout << "No TAs in the system.\n";
        return;
    }
    
    for (const TA* ta : taList) {
        ta->display();
        std::cout << "\n";
    }
}

// Display system statistics
void OfficeHoursSystem::displaySystemStats() const {
    std::cout << "\n╔═════════════════════════════════════════════════════════╗\n";
    std::cout << "║              SYSTEM STATISTICS                         ║\n";
    std::cout << "╠═════════════════════════════════════════════════════════╣\n";
    std::cout << "║ Total Students Processed: " << std::setw(30) << std::left 
              << totalStudentsProcessed << "║\n";
    std::cout << "║ Students Currently in System: " << std::setw(26) << std::left 
              << totalStudentsInSystem << "║\n";
    std::cout << "║ Total TAs: " << std::setw(45) << std::left 
              << taList.size() << "║\n";
    std::cout << "║ Current Time: " << std::setw(42) << std::left 
              << (std::to_string(currentTime) + " minutes") << "║\n";
    std::cout << "╚═════════════════════════════════════════════════════════╝\n";
    
    // Display individual TA statistics
    if (!taList.empty()) {
        std::cout << "\n╔═════════════════════════════════════════════════════════╗\n";
        std::cout << "║                 TA PERFORMANCE                         ║\n";
        std::cout << "╚═════════════════════════════════════════════════════════╝\n\n";
        
        for (const TA* ta : taList) {
            ta->displayStats();
            std::cout << "\n";
        }
    }
}

// Display menu
void OfficeHoursSystem::displayMenu() const {
    std::cout << "\n╔═════════════════════════════════════════════════════════╗\n";
    std::cout << "║         OFFICE HOURS TRIAGE SYSTEM - MENU              ║\n";
    std::cout << "╠═════════════════════════════════════════════════════════╣\n";
    std::cout << "║ 1. Add Student                                         ║\n";
    std::cout << "║ 2. Add TA                                              ║\n";
    std::cout << "║ 3. Process System (Move students through queues)       ║\n";
    std::cout << "║ 4. Complete Student (TA finishes helping)              ║\n";
    std::cout << "║ 5. Display All Queues                                  ║\n";
    std::cout << "║ 6. Display TA Status                                   ║\n";
    std::cout << "║ 7. Display System Statistics                           ║\n";
    std::cout << "║ 8. Advance Time                                        ║\n";
    std::cout << "║ 9. Exit                                                ║\n";
    std::cout << "╚═════════════════════════════════════════════════════════╝\n";
    std::cout << "Enter choice: ";
}

// Clear the entire system
void OfficeHoursSystem::clearSystem() {
    // Clean up arrival queue
    while (!arrivalQueue.empty()) {
        delete arrivalQueue.front();
        arrivalQueue.pop();
    }
    
    // Clean up skill set queues
    for (auto& pair : skillSetQueues) {
        while (!pair.second.empty()) {
            delete pair.second.top();
            pair.second.pop();
        }
    }
    skillSetQueues.clear();
    
    currentTime = 0;
    totalStudentsInSystem = 0;
    std::cout << "\n✓ System cleared (TAs retained)\n";
}

// Get available skill sets from TAs
std::vector<std::string> OfficeHoursSystem::getAvailableSkillSets() const {
    std::vector<std::string> skillSets;
    for (const TA* ta : taList) {
        for (const std::string& skill : ta->getSkillSets()) {
            if (std::find(skillSets.begin(), skillSets.end(), skill) == skillSets.end()) {
                skillSets.push_back(skill);
            }
        }
    }
    return skillSets;
}
