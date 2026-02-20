import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Original activities data for reset
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball team for students of all skill levels",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["james@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Learn tennis techniques and participate in friendly matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["alex@mergington.edu", "mia@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and mixed media techniques",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["isabella@mergington.edu"]
    },
    "Music Ensemble": {
        "description": "Perform and collaborate with other student musicians",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["noah@mergington.edu", "ava@mergington.edu"]
    },
    "Debate Club": {
        "description": "Develop argumentation and public speaking skills through competitive debate",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["lucas@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific discoveries",
        "schedule": "Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 22,
        "participants": ["ethan@mergington.edu", "grace@mergington.edu"]
    }
}

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities data before each test."""
    activities.clear()
    activities.update(ORIGINAL_ACTIVITIES)

@pytest.fixture
def client():
    """Provide a TestClient instance for the FastAPI app."""
    return TestClient(app)

def test_root_redirect(client):
    """Test GET / redirects to /static/index.html."""
    # Arrange: No special setup needed
    
    # Act: Make GET request to root
    response = client.get("/")
    
    # Assert: Check redirect response
    assert response.status_code == 200  # TestClient follows redirects by default
    assert "/static/index.html" in str(response.url)

def test_get_activities(client):
    """Test GET /activities returns all activities."""
    # Arrange: Activities are already set up via fixture
    
    # Act: Make GET request to activities endpoint
    response = client.get("/activities")
    
    # Assert: Check response structure and data
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Number of activities
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "schedule" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]
    assert "participants" in data["Chess Club"]
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]

def test_signup_success(client):
    """Test successful POST signup for an activity."""
    # Arrange: Choose an activity and new email
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    initial_count = len(activities[activity_name]["participants"])
    
    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Check success response and data update
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_count + 1

def test_signup_activity_not_found(client):
    """Test POST signup for non-existent activity returns 404."""
    # Arrange: Use invalid activity name
    activity_name = "NonExistent Activity"
    email = "test@mergington.edu"
    
    # Act: Make POST request
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Check error response
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_signup_already_signed_up(client):
    """Test POST signup when student is already signed up returns 400."""
    # Arrange: Use email already in participants
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    initial_participants = activities[activity_name]["participants"].copy()
    
    # Act: Make POST request
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Check error response and no data change
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"] == initial_participants

def test_unregister_success(client):
    """Test successful DELETE unregister from an activity."""
    # Arrange: Choose activity and existing participant
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    initial_count = len(activities[activity_name]["participants"])
    
    # Act: Make DELETE request
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Check success response and data update
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_count - 1

def test_unregister_activity_not_found(client):
    """Test DELETE unregister for non-existent activity returns 404."""
    # Arrange: Use invalid activity name
    activity_name = "NonExistent Activity"
    email = "test@mergington.edu"
    
    # Act: Make DELETE request
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Check error response
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_unregister_not_signed_up(client):
    """Test DELETE unregister when student is not signed up returns 400."""
    # Arrange: Use email not in participants
    activity_name = "Chess Club"
    email = "notsigned@mergington.edu"
    initial_participants = activities[activity_name]["participants"].copy()
    
    # Act: Make DELETE request
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Check error response and no data change
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student not signed up for this activity"
    assert activities[activity_name]["participants"] == initial_participants