#ifndef TA_H
#define TA_H

#include <string>
#include <vector>
#include <iostream>
#include "Student.h"

/**
 * @brief Represents a Teaching Assistant available during office hours
 */
class TA {
private:
    std::string name;
    std::vector<std::string> skillSets;  // Can have multiple skill sets
    bool isAvailable;
    Student* currentStudent;  // Pointer to student currently being helped
    int studentsHelped;
    int totalWaitTime;  // Total wait time of all students helped

public:
    // Constructors
    TA();
    TA(const std::string& name, const std::vector<std::string>& skillSets);
    
    // Destructor
    ~TA();
    
    // Getters
    std::string getName() const;
    std::vector<std::string> getSkillSets() const;
    bool getIsAvailable() const;
    Student* getCurrentStudent() const;
    int getStudentsHelped() const;
    double getAverageWaitTime() const;
    
    // Setters
    void setName(const std::string& name);
    void addSkillSet(const std::string& skillSet);
    void setAvailable(bool available);
    
    // TA operations
    bool hasSkillSet(const std::string& skillSet) const;
    bool canHelp(const Student& student) const;
    void assignStudent(Student* student, int currentTime);
    void finishWithStudent();
    
    // Utility methods
    void display() const;
    void displayStats() const;
};

#endif // TA_H
