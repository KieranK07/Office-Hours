#ifndef STUDENT_H
#define STUDENT_H

#include <string>
#include <iostream>

/**
 * @brief Represents a student seeking help during office hours
 */
class Student {
private:
    std::string name;
    std::string skillSet;
    int arrivalTime;
    std::string problemDescription;
    int severity;  // 1 (low) to 5 (high)
    int ticketNumber;
    static int nextTicketNumber;

public:
    // Constructors
    Student();
    Student(const std::string& name, const std::string& skillSet, 
            int arrivalTime, const std::string& problemDescription, int severity);
    
    // Getters
    std::string getName() const;
    std::string getSkillSet() const;
    int getArrivalTime() const;
    std::string getProblemDescription() const;
    int getSeverity() const;
    int getTicketNumber() const;
    
    // Setters
    void setName(const std::string& name);
    void setSkillSet(const std::string& skillSet);
    void setArrivalTime(int time);
    void setProblemDescription(const std::string& description);
    void setSeverity(int severity);
    
    // Utility methods
    void display() const;
    
    // Comparison operator for priority queue (higher severity = higher priority)
    // If severity is equal, earlier arrival time has priority
    bool operator<(const Student& other) const;
    bool operator>(const Student& other) const;
};

#endif // STUDENT_H
