"""
Example test client for the Office Hours API
Demonstrates complete workflow from student request to completion
"""
import requests
from time import sleep
from typing import Optional


class OfficeHoursAPIClient:
    """Client wrapper for Office Hours API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.role: Optional[str] = None
    
    def _headers(self) -> dict:
        """Get authorization headers"""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    def login(self, username: str, password: str) -> dict:
        """Login and store token"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["access_token"]
        self.role = data["role"]
        print(f"✅ Logged in as {username} (role: {self.role})")
        return data
    
    def student_request(self, name: str, severity: int, skill_set: str, 
                       problem_description: str) -> dict:
        """Student submits help request"""
        response = requests.post(
            f"{self.base_url}/student/request",
            json={
                "name": name,
                "severity": severity,
                "skill_set": skill_set,
                "problem_description": problem_description
            }
        )
        response.raise_for_status()
        data = response.json()
        print(f"✅ Student {name} added (ticket #{data['ticket_number']})")
        return data
    
    def add_ta(self, name: str, skills: list[str], username: str, 
               password: str) -> dict:
        """Staff adds a TA"""
        response = requests.post(
            f"{self.base_url}/staff/ta",
            headers=self._headers(),
            json={
                "name": name,
                "skills": skills,
                "username": username,
                "password": password
            }
        )
        response.raise_for_status()
        data = response.json()
        print(f"✅ TA {name} added with skills: {', '.join(skills)}")
        return data
    
    def triage(self) -> dict:
        """Staff processes triage"""
        response = requests.get(
            f"{self.base_url}/staff/triage",
            headers=self._headers()
        )
        response.raise_for_status()
        data = response.json()
        print(f"✅ Triage: {data['students_moved']} moved, {data['students_assigned']} assigned")
        return data
    
    def ta_claim(self, ta_id: str, preferred_skill: Optional[str] = None) -> dict:
        """TA claims a student"""
        response = requests.post(
            f"{self.base_url}/ta/claim",
            headers=self._headers(),
            json={
                "ta_id": ta_id,
                "preferred_skill": preferred_skill
            }
        )
        response.raise_for_status()
        data = response.json()
        print(f"✅ TA claimed student: {data['name']} (severity: {data['severity']})")
        return data
    
    def complete_student(self, ta_id: str, student_id: str) -> dict:
        """TA completes student session"""
        response = requests.post(
            f"{self.base_url}/ta/complete",
            headers=self._headers(),
            json={
                "ta_id": ta_id,
                "student_id": student_id
            }
        )
        response.raise_for_status()
        data = response.json()
        print(f"✅ Student session completed")
        return data
    
    def get_stats(self) -> dict:
        """Get system statistics"""
        response = requests.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()
    
    def print_stats(self):
        """Print formatted statistics"""
        stats = self.get_stats()
        print("\n" + "="*60)
        print("📊 SYSTEM STATISTICS")
        print("="*60)
        print(f"Students in system: {stats['total_students_in_system']}")
        print(f"Students processed: {stats['total_students_processed']}")
        print(f"Arrival queue: {stats['arrival_queue_size']}")
        print(f"Available TAs: {stats['available_tas']}")
        print(f"Busy TAs: {stats['busy_tas']}")
        print(f"Avg wait time: {stats['average_wait_time_minutes']:.1f} min")
        
        if stats['skill_queues']:
            print("\nSkill Queues:")
            for skill, count in stats['skill_queues'].items():
                print(f"  - {skill}: {count} students")
        
        print("="*60 + "\n")


def demo_workflow():
    """Demonstrate complete workflow"""
    print("\n" + "="*60)
    print("🎓 Office Hours API - Complete Workflow Demo")
    print("="*60 + "\n")
    
    client = OfficeHoursAPIClient()
    
    try:
        # 1. Staff logs in
        print("1️⃣ Staff Login")
        print("-" * 60)
        client.login("admin", "admin123")
        print()
        
        # 2. Add TAs
        print("2️⃣ Adding TAs")
        print("-" * 60)
        client.add_ta(
            name="Bob Smith",
            skills=["Python", "Java", "Data Structures"],
            username="ta_bob",
            password="SecurePass123!"
        )
        client.add_ta(
            name="Carol White",
            skills=["C++", "Algorithms"],
            username="ta_carol",
            password="SecurePass456!"
        )
        print()
        
        # 3. Students request help
        print("3️⃣ Students Requesting Help")
        print("-" * 60)
        students = [
            client.student_request("Alice Johnson", 5, "Python", "Stack overflow in recursion"),
            client.student_request("David Lee", 3, "Java", "Null pointer exception"),
            client.student_request("Emma Davis", 4, "C++", "Segmentation fault"),
            client.student_request("Frank Brown", 2, "Python", "Syntax error in loop"),
        ]
        print()
        
        # 4. View stats before triage
        print("4️⃣ Before Triage")
        print("-" * 60)
        client.print_stats()
        
        # 5. Staff runs triage
        print("5️⃣ Running Triage")
        print("-" * 60)
        client.triage()
        print()
        
        # 6. View stats after triage
        print("6️⃣ After Triage")
        print("-" * 60)
        client.print_stats()
        
        # 7. TA Bob logs in and claims a student
        print("7️⃣ TA Claims Student")
        print("-" * 60)
        ta_bob_client = OfficeHoursAPIClient()
        ta_bob_client.login("ta_bob", "SecurePass123!")
        
        claimed = ta_bob_client.ta_claim("ta_ta_bob", "Python")
        print()
        
        # 8. TA completes the student
        print("8️⃣ TA Completes Student Session")
        print("-" * 60)
        sleep(1)  # Simulate helping time
        ta_bob_client.complete_student("ta_ta_bob", claimed["id"])
        print()
        
        # 9. Final statistics
        print("9️⃣ Final System State")
        print("-" * 60)
        client.print_stats()
        
        print("✅ Demo completed successfully!\n")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API server")
        print("   Make sure the server is running at http://localhost:8000")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   {e.response.json()}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    demo_workflow()
