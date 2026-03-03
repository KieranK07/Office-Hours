/**
 * Office Hours Triage System
 * 
 * A three-layer queue system for managing student help requests:
 * 1. Arrival Queue - All students enter here first
 * 2. Skill Set Queues - Students sorted by problem type and priority
 * 3. TA Assignment - Students matched with available TAs
 * 
 * Features:
 * - Priority-based queuing (severity + arrival time)
 * - Multiple skill set support
 * - Real-time statistics tracking
 * - Interactive menu system
 */

#include <iostream>
#include <string>
#include <vector>
#include <limits>
#include "OfficeHoursSystem.h"

using namespace std;

// Function prototypes
void displayWelcome();
void addStudentMenu(OfficeHoursSystem& system);
void addTAMenu(OfficeHoursSystem& system);
void completeStudentMenu(OfficeHoursSystem& system);
void advanceTimeMenu(OfficeHoursSystem& system);
void initializeDemo(OfficeHoursSystem& system);
void clearInputBuffer();

int main() {
    OfficeHoursSystem system;
    int choice;
    
    displayWelcome();
    
    // Ask if user wants demo data
    cout << "\nWould you like to load demo data? (1=Yes, 0=No): ";
    int loadDemo;
    cin >> loadDemo;
    clearInputBuffer();
    
    if (loadDemo == 1) {
        initializeDemo(system);
    }
    
    // Main program loop
    while (true) {
        system.displayMenu();
        cin >> choice;
        clearInputBuffer();
        
        switch (choice) {
            case 1:
                addStudentMenu(system);
                break;
                
            case 2:
                addTAMenu(system);
                break;
                
            case 3:
                system.processSystem();
                break;
                
            case 4:
                completeStudentMenu(system);
                break;
                
            case 5:
                system.displayAllQueues();
                break;
                
            case 6:
                system.displayTAStatus();
                break;
                
            case 7:
                system.displaySystemStats();
                break;
                
            case 8:
                advanceTimeMenu(system);
                break;
                
            case 9:
                cout << "\n╔═════════════════════════════════════════════════════════╗\n";
                cout << "║  Thank you for using Office Hours Triage System!       ║\n";
                cout << "╚═════════════════════════════════════════════════════════╝\n\n";
                return 0;
                
            default:
                cout << "\n✗ Invalid choice. Please try again.\n";
        }
        
        cout << "\nPress Enter to continue...";
        cin.get();
    }
    
    return 0;
}

// Display welcome message
void displayWelcome() {
    cout << "\n╔═════════════════════════════════════════════════════════╗\n";
    cout << "║                                                        ║\n";
    cout << "║         OFFICE HOURS TRIAGE SYSTEM v2.0                ║\n";
    cout << "║                                                        ║\n";
    cout << "║     Efficiently managing student help requests         ║\n";
    cout << "║                                                        ║\n";
    cout << "╚═════════════════════════════════════════════════════════╝\n";
}

// Menu for adding a student
void addStudentMenu(OfficeHoursSystem& system) {
    string name, skillSet, problemDescription;
    int severity;
    
    cout << "\n─── ADD NEW STUDENT ───\n";
    
    cout << "Student name: ";
    getline(cin, name);
    
    cout << "Skill set (e.g., C++, Python, Java, Data Structures): ";
    getline(cin, skillSet);
    
    cout << "Problem description: ";
    getline(cin, problemDescription);
    
    cout << "Severity (1-5, where 5 is most urgent): ";
    cin >> severity;
    clearInputBuffer();
    
    // Validate severity
    if (severity < 1 || severity > 5) {
        cout << "✗ Invalid severity. Using default value of 3.\n";
        severity = 3;
    }
    
    system.addStudent(name, skillSet, problemDescription, severity);
}

// Menu for adding a TA
void addTAMenu(OfficeHoursSystem& system) {
    string name, skillSet;
    vector<string> skillSets;
    int numSkills;
    
    cout << "\n─── ADD NEW TA ───\n";
    
    cout << "TA name: ";
    getline(cin, name);
    
    cout << "Number of skill sets: ";
    cin >> numSkills;
    clearInputBuffer();
    
    for (int i = 0; i < numSkills; i++) {
        cout << "Skill set " << (i + 1) << ": ";
        getline(cin, skillSet);
        skillSets.push_back(skillSet);
    }
    
    system.addTA(name, skillSets);
}

// Menu for completing a student's session
void completeStudentMenu(OfficeHoursSystem& system) {
    string taName;
    
    cout << "\n─── COMPLETE STUDENT SESSION ───\n";
    
    // First show current TA status
    system.displayTAStatus();
    
    cout << "\nEnter TA name: ";
    getline(cin, taName);
    
    system.completeCurrentStudent(taName);
}

// Menu for advancing time
void advanceTimeMenu(OfficeHoursSystem& system) {
    int minutes;
    
    cout << "\n─── ADVANCE TIME ───\n";
    cout << "Current time: " << system.getCurrentTime() << " minutes\n";
    cout << "Minutes to advance: ";
    cin >> minutes;
    clearInputBuffer();
    
    if (minutes > 0) {
        system.advanceTime(minutes);
    } else {
        cout << "✗ Invalid time value.\n";
    }
}

// Initialize system with demo data
void initializeDemo(OfficeHoursSystem& system) {
    cout << "\n═══════════════════════════════════════════════════════\n";
    cout << "Loading demo data...\n";
    cout << "═══════════════════════════════════════════════════════\n";
    
    // Add TAs
    system.addTA("Dr. Smith", {"C++", "Data Structures"});
    system.addTA("Alice Johnson", {"Python", "Machine Learning"});
    system.addTA("Bob Chen", {"Java", "C++"});
    system.addTA("Carol Martinez", {"Python", "Data Structures"});
    
    // Add students
    system.addStudent("Emma Wilson", "C++", "Segmentation fault in linked list", 4);
    system.addStudent("Liam Brown", "Python", "Help with numpy arrays", 2);
    system.addStudent("Olivia Davis", "Java", "Cannot compile my project", 5);
    system.addStudent("Noah Miller", "C++", "Memory leak issue", 3);
    system.addStudent("Ava Garcia", "Data Structures", "Binary tree traversal confusion", 3);
    system.addStudent("Ethan Rodriguez", "Python", "Need help with file I/O", 1);
    system.addStudent("Sophia Martinez", "C++", "Template syntax error", 2);
    
    cout << "\n✓ Demo data loaded successfully!\n";
    cout << "✓ 4 TAs added\n";
    cout << "✓ 7 students added\n";
}

// Clear input buffer
void clearInputBuffer() {
    cin.clear();
    cin.ignore(numeric_limits<streamsize>::max(), '\n');
}
