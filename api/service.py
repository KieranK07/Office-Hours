"""
Triage Service Layer - Business Logic for Office Hours Queue Management
Implements priority-based queuing with separation of concerns
"""
from datetime import datetime
from typing import Optional
from collections import defaultdict
import heapq
from models import Student, TA, QueueType
from schemas import StudentResponse, TAResponse, SystemStatsResponse, QueueStatsResponse


class PriorityStudent:
    """Wrapper for Student to enable priority queue ordering"""
    
    def __init__(self, student: Student):
        self.student = student
    
    def __lt__(self, other: 'PriorityStudent') -> bool:
        """
        Priority comparison: Higher severity wins, earlier arrival time breaks ties
        priority_queue uses min-heap, so we invert for max priority behavior
        """
        # Higher severity = higher priority (invert)
        if self.student.severity != other.student.severity:
            return self.student.severity > other.student.severity
        
        # Earlier arrival time = higher priority (invert)
        return self.student.arrival_time < other.student.arrival_time
    
    def __eq__(self, other: 'PriorityStudent') -> bool:
        return self.student.id == other.student.id


class OfficeHoursService:
    """
    Core service layer for managing office hours triage system
    Implements three-layer queue architecture with priority-based logic
    """
    
    def __init__(self):
        # Layer 1: Arrival Queue (FIFO)
        self.arrival_queue: list[Student] = []
        
        # Layer 2: Skill Set Priority Queues (Priority by severity & arrival time)
        # Using heapq for priority queue implementation
        self.skill_queues: dict[str, list[PriorityStudent]] = defaultdict(list)
        
        # Layer 3: TA Management
        self.tas: dict[str, TA] = {}
        
        # Student tracking
        self.students: dict[str, Student] = {}
        
        # Statistics
        self.total_students_processed: int = 0
        self.next_ticket_number: int = 1
    
    # ========================================================================
    # Student Management
    # ========================================================================
    
    def add_student(self, name: str, severity: int, skill_set: str, 
                   problem_description: str) -> Student:
        """
        Add a student to the arrival queue
        
        Args:
            name: Student name
            severity: Problem severity (1-5)
            skill_set: Required skill set
            problem_description: Description of the problem
            
        Returns:
            Created Student object
        """
        student_id = f"student_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        student = Student(
            id=student_id,
            name=name,
            severity=severity,
            skill_set=skill_set.strip(),
            problem_description=problem_description,
            arrival_time=datetime.now(),
            ticket_number=self.next_ticket_number,
            queue_type=QueueType.ARRIVAL
        )
        
        self.next_ticket_number += 1
        self.students[student_id] = student
        self.arrival_queue.append(student)
        
        return student
    
    def get_student(self, student_id: str) -> Optional[Student]:
        """Retrieve a student by ID"""
        return self.students.get(student_id)
    
    def remove_student(self, student_id: str) -> bool:
        """Remove a student from the system"""
        if student_id in self.students:
            del self.students[student_id]
            return True
        return False
    
    def get_all_students_in_system(self) -> list[Student]:
        """Get all students currently in the system"""
        return list(self.students.values())
    
    # ========================================================================
    # TA Management
    # ========================================================================
    
    def add_ta(self, ta_id: str, name: str, skills: list[str]) -> TA:
        """
        Add a TA to the system
        
        Args:
            ta_id: Unique TA identifier
            name: TA name
            skills: List of skill sets the TA can help with
            
        Returns:
            Created TA object
        """
        ta = TA(
            id=ta_id,
            name=name,
            skills=skills,
            is_available=True,
            students_helped=0,
            total_wait_time_minutes=0
        )
        
        self.tas[ta_id] = ta
        return ta
    
    def get_ta(self, ta_id: str) -> Optional[TA]:
        """Retrieve a TA by ID"""
        return self.tas.get(ta_id)
    
    def get_all_tas(self) -> list[TA]:
        """Get all TAs in the system"""
        return list(self.tas.values())
    
    def get_available_tas(self) -> list[TA]:
        """Get all available TAs"""
        return [ta for ta in self.tas.values() if ta.is_available]
    
    # ========================================================================
    # Queue Operations (Three-Layer System)
    # ========================================================================
    
    def triage_arrival_queue(self) -> int:
        """
        Layer 1 → Layer 2: Move students from arrival queue to skill-set queues
        
        Returns:
            Number of students moved to skill-set queues
        """
        students_moved = 0
        
        while self.arrival_queue:
            student = self.arrival_queue.pop(0)
            student.queue_type = QueueType.SKILL_SET
            
            # Add to appropriate skill set priority queue
            priority_student = PriorityStudent(student)
            heapq.heappush(self.skill_queues[student.skill_set], priority_student)
            
            students_moved += 1
        
        return students_moved
    
    def assign_students_to_tas(self) -> int:
        """
        Layer 2 → Layer 3: Assign students from skill queues to available TAs
        
        Returns:
            Number of students assigned to TAs
        """
        students_assigned = 0
        
        # Iterate through all skill queues
        for skill_set, priority_queue in list(self.skill_queues.items()):
            if not priority_queue:
                continue
            
            # Find available TAs with this skill set
            available_tas = [
                ta for ta in self.tas.values() 
                if ta.is_available and ta.has_skill(skill_set)
            ]
            
            # Assign students to available TAs
            while priority_queue and available_tas:
                # Get highest priority student
                priority_student = heapq.heappop(priority_queue)
                student = priority_student.student
                
                # Get first available TA (could implement TA priority here)
                ta = available_tas.pop(0)
                
                # Calculate wait time
                wait_time = (datetime.now() - student.arrival_time).total_seconds() / 60
                
                # Assign student to TA
                student.assigned_ta_id = ta.id
                student.queue_type = QueueType.ASSIGNED
                
                ta.current_student_id = student.id
                ta.is_available = False
                ta.students_helped += 1
                ta.total_wait_time_minutes += int(wait_time)
                
                students_assigned += 1
        
        return students_assigned
    
    def complete_student_session(self, ta_id: str, student_id: str) -> bool:
        """
        Complete a student's help session with a TA
        
        Args:
            ta_id: TA identifier
            student_id: Student identifier
            
        Returns:
            True if session completed successfully
        """
        ta = self.get_ta(ta_id)
        student = self.get_student(student_id)
        
        if not ta or not student:
            return False
        
        if ta.current_student_id != student_id:
            return False
        
        # Free up the TA
        ta.current_student_id = None
        ta.is_available = True
        
        # Remove student from system
        self.remove_student(student_id)
        self.total_students_processed += 1
        
        return True
    
    # ========================================================================
    # TA Claim Operation
    # ========================================================================
    
    def ta_claim_student(self, ta_id: str, preferred_skill: Optional[str] = None) -> Optional[Student]:
        """
        Allow a TA to claim the highest priority student matching their skills
        
        Args:
            ta_id: TA identifier
            preferred_skill: Optional preferred skill set
            
        Returns:
            Claimed student or None if no match found
        """
        ta = self.get_ta(ta_id)
        if not ta or not ta.is_available:
            return None
        
        # Determine which skills to check (preferred or all)
        skills_to_check = [preferred_skill] if preferred_skill else ta.skills
        
        # Try to find a student matching any of the TA's skills
        for skill in skills_to_check:
            if skill in self.skill_queues and self.skill_queues[skill]:
                # Get highest priority student
                priority_student = heapq.heappop(self.skill_queues[skill])
                student = priority_student.student
                
                # Calculate wait time
                wait_time = (datetime.now() - student.arrival_time).total_seconds() / 60
                
                # Assign student to TA
                student.assigned_ta_id = ta.id
                student.queue_type = QueueType.ASSIGNED
                
                ta.current_student_id = student.id
                ta.is_available = False
                ta.students_helped += 1
                ta.total_wait_time_minutes += int(wait_time)
                
                return student
        
        return None
    
    # ========================================================================
    # Statistics and Reporting
    # ========================================================================
    
    def get_queue_size(self, skill_set: str) -> int:
        """Get the size of a specific skill queue"""
        return len(self.skill_queues.get(skill_set, []))
    
    def get_arrival_queue_size(self) -> int:
        """Get the size of the arrival queue"""
        return len(self.arrival_queue)
    
    def get_total_queue_size(self) -> int:
        """Get total number of students across all queues"""
        return len(self.students)

    def get_students_ahead(self, student_id: str) -> list[Student]:
        """Get students ahead of the specified student in their current queue"""
        student = self.get_student(student_id)
        if not student:
            return []

        if student.queue_type == QueueType.ARRIVAL:
            for index, queued_student in enumerate(self.arrival_queue):
                if queued_student.id == student_id:
                    return self.arrival_queue[:index]
            return []

        if student.queue_type == QueueType.SKILL_SET:
            priority_queue = self.skill_queues.get(student.skill_set, [])
            ordered_students = [priority_student.student for priority_student in sorted(priority_queue)]
            for index, queued_student in enumerate(ordered_students):
                if queued_student.id == student_id:
                    return ordered_students[:index]
            return []

        return []

    def get_ta_upcoming_students(self, ta_id: str) -> list[Student]:
        """Get students a TA is likely to help next based on TA skills"""
        ta = self.get_ta(ta_id)
        if not ta:
            return []

        upcoming_students: list[Student] = []

        if ta.current_student_id:
            current_student = self.get_student(ta.current_student_id)
            if current_student:
                upcoming_students.append(current_student)

        skill_candidates: list[Student] = []
        for skill in ta.skills:
            for priority_student in sorted(self.skill_queues.get(skill, [])):
                candidate = priority_student.student
                if candidate.id != ta.current_student_id:
                    skill_candidates.append(candidate)

        unique_candidates: list[Student] = []
        seen_student_ids: set[str] = {s.id for s in upcoming_students}
        for candidate in skill_candidates:
            if candidate.id not in seen_student_ids:
                unique_candidates.append(candidate)
                seen_student_ids.add(candidate.id)

        upcoming_students.extend(unique_candidates)
        return upcoming_students
    
    def get_system_statistics(self) -> SystemStatsResponse:
        """
        Generate comprehensive system statistics
        
        Returns:
            SystemStatsResponse with all relevant metrics
        """
        # Calculate TA statistics
        available_tas = sum(1 for ta in self.tas.values() if ta.is_available)
        busy_tas = len(self.tas) - available_tas
        
        # Calculate average wait time
        total_wait = sum(ta.total_wait_time_minutes for ta in self.tas.values())
        total_helped = sum(ta.students_helped for ta in self.tas.values())
        avg_wait_time = total_wait / total_helped if total_helped > 0 else 0.0
        
        # Skill queue sizes
        skill_queue_sizes = {
            skill: len(queue) 
            for skill, queue in self.skill_queues.items()
        }
        
        # Queue details
        queue_details = []
        
        # Arrival queue details
        if self.arrival_queue:
            arrival_students = [
                self._student_to_response(s) for s in self.arrival_queue
            ]
            queue_details.append(QueueStatsResponse(
                queue_type="Arrival",
                size=len(self.arrival_queue),
                students=arrival_students
            ))
        
        # Skill queue details
        for skill, priority_queue in self.skill_queues.items():
            if priority_queue:
                students = [
                    self._student_to_response(ps.student) 
                    for ps in sorted(priority_queue)
                ]
                queue_details.append(QueueStatsResponse(
                    queue_type=f"Skill: {skill}",
                    size=len(priority_queue),
                    students=students
                ))
        
        # Assigned students
        assigned_students = [
            s for s in self.students.values() 
            if s.queue_type == QueueType.ASSIGNED
        ]
        if assigned_students:
            assigned_responses = [
                self._student_to_response(s) for s in assigned_students
            ]
            queue_details.append(QueueStatsResponse(
                queue_type="Assigned to TAs",
                size=len(assigned_students),
                students=assigned_responses
            ))
        
        return SystemStatsResponse(
            current_time=datetime.now(),
            arrival_queue_size=len(self.arrival_queue),
            skill_queues=skill_queue_sizes,
            total_students_in_system=len(self.students),
            total_students_processed=self.total_students_processed,
            available_tas=available_tas,
            busy_tas=busy_tas,
            average_wait_time_minutes=avg_wait_time,
            queue_details=queue_details
        )
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _student_to_response(self, student: Student) -> StudentResponse:
        """Convert Student model to StudentResponse"""
        wait_time = (datetime.now() - student.arrival_time).total_seconds() / 60
        
        return StudentResponse(
            id=student.id,
            name=student.name,
            severity=student.severity,
            skill_set=student.skill_set,
            problem_description=student.problem_description,
            arrival_time=student.arrival_time,
            ticket_number=student.ticket_number or 0,
            queue_type=student.queue_type,
            assigned_ta_id=student.assigned_ta_id,
            wait_time_minutes=round(wait_time, 2)
        )
    
    def _ta_to_response(self, ta: TA) -> TAResponse:
        """Convert TA model to TAResponse"""
        current_student_name = None
        if ta.current_student_id:
            student = self.get_student(ta.current_student_id)
            current_student_name = student.name if student else None
        
        return TAResponse(
            id=ta.id,
            name=ta.name,
            skills=ta.skills,
            current_student_id=ta.current_student_id,
            current_student_name=current_student_name,
            is_available=ta.is_available,
            students_helped=ta.students_helped,
            average_wait_time=ta.calculate_average_wait_time()
        )


# Global service instance (singleton pattern for in-memory state)
office_hours_service = OfficeHoursService()
