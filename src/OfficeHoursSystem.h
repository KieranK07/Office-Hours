#ifndef OFFICEHOURSSYSTEM_H
#define OFFICEHOURSSYSTEM_H

#include <queue>
#include <vector>
#include <map>
#include <string>
#include "Student.h"
#include "TA.h"

/**
 * @brief Comparator for Student pointers in priority queue
 * Higher priority students should come first (greater severity, earlier arrival)
 */
struct StudentPtrComparator {
    bool operator()(const Student* a, const Student* b) const {
        // Use the Student's > operator: returns true if a has higher priority than b
        // priority_queue is a max heap, so we want higher priority students at top
        // We need to return true if a has LOWER priority than b (for min-heap behavior of high priority)
        return *a < *b;
    }
};

/**
 * @brief Manages the entire office hours triage system
 * 
 * Three-layer system:
 * 1. Arrival Queue - All students arrive here first
 * 2. Skill Set Queues - Students sorted by their question type
 * 3. TA Assignment - Students matched with available TAs
 */
class OfficeHoursSystem {
private:
    // Arrival queue - all students enter here first
    std::queue<Student*> arrivalQueue;
    
    // Skill set priority queues - students sorted by severity and arrival time
    std::map<std::string, std::priority_queue<Student*, 
             std::vector<Student*>, StudentPtrComparator>> skillSetQueues;
    
    // List of available TAs
    std::vector<TA*> taList;
    
    // Current system time (in minutes)
    int currentTime;
    
    // System statistics
    int totalStudentsProcessed;
    int totalStudentsInSystem;
    
    // Helper methods
    void processArrivalQueue();
    void assignStudentsToTAs();
    TA* findAvailableTA(const std::string& skillSet);

public:
    // Constructor and Destructor
    OfficeHoursSystem();
    ~OfficeHoursSystem();
    
    // System operations
    void addStudent(const std::string& name, const std::string& skillSet, 
                   const std::string& problemDescription, int severity);
    void addTA(const std::string& name, const std::vector<std::string>& skillSets);
    void completeCurrentStudent(const std::string& taName);
    void advanceTime(int minutes = 1);
    void processSystem();
    
    // Query methods
    int getCurrentTime() const;
    int getQueueSize(const std::string& skillSet) const;
    int getTotalQueueSize() const;
    int getArrivalQueueSize() const;
    
    // Display methods
    void displayAllQueues() const;
    void displayTAStatus() const;
    void displaySystemStats() const;
    void displayMenu() const;
    
    // Utility methods
    void clearSystem();
    std::vector<std::string> getAvailableSkillSets() const;
};

#endif // OFFICEHOURSSYSTEM_H
