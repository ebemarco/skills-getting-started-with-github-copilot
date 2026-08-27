def test_root_redirect(client):
    """
    Test che verifica il reindirizzamento dalla root (/) alla pagina statica index.html.
    """
    # Arrange
    # (Il client di test viene iniettato come fixture)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """
    Test che verifica la corretta restituzione dell'elenco delle attivita'.
    """
    # Arrange
    expected_clubs = ["Chess Club", "Programming Class", "Gym Class", "Basketball Team"]

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(data, dict)
    for club in expected_clubs:
        assert club in data
        assert "description" in data[club]
        assert "schedule" in data[club]
        assert "max_participants" in data[club]
        assert "participants" in data[club]


def test_signup_success(client):
    """
    Test di successo per l'iscrizione di uno studente a un'attivita'.
    """
    # Arrange
    activity_name = "Basketball Team"
    student_email = "new_student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": student_email})
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["message"] == f"Signed up {student_email} for {activity_name}"
    
    # Verifica che lo stato sia persistito nell'in-memory db
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert student_email in activities_data[activity_name]["participants"]


def test_signup_duplicate_student_error(client):
    """
    Test di errore quando uno studente prova a iscriversi due volte alla stessa attivita'.
    """
    # Arrange
    activity_name = "Chess Club"
    student_email = "michael@mergington.edu"  # Già presente nello stato iniziale

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": student_email})
    data = response.json()

    # Assert
    assert response.status_code == 400
    assert data["detail"] == "Student already signed up for this activity"


def test_signup_activity_not_found_error(client):
    """
    Test di errore quando si prova a iscriversi a un'attivita' inesistente.
    """
    # Arrange
    activity_name = "Non Existing Club"
    student_email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": student_email})
    data = response.json()

    # Assert
    assert response.status_code == 404
    assert data["detail"] == "Activity not found"


def test_unregister_success(client):
    """
    Test di successo per la disiscrizione di uno studente da un'attivita'.
    """
    # Arrange
    activity_name = "Chess Club"
    student_email = "michael@mergington.edu"  # Presente nello stato iniziale

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": student_email})
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["message"] == f"Unregistered {student_email} from {activity_name}"
    
    # Verifica che lo studente sia stato effettivamente rimosso
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert student_email not in activities_data[activity_name]["participants"]


def test_unregister_not_signed_up_error(client):
    """
    Test di errore quando si prova a disiscrivere uno studente non iscritto all'attivita'.
    """
    # Arrange
    activity_name = "Chess Club"
    student_email = "not_signed_up@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": student_email})
    data = response.json()

    # Assert
    assert response.status_code == 400
    assert data["detail"] == "Student is not signed up for this activity"


def test_unregister_activity_not_found_error(client):
    """
    Test di errore quando si prova a disiscrivere uno studente da un'attivita' inesistente.
    """
    # Arrange
    activity_name = "Non Existing Club"
    student_email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": student_email})
    data = response.json()

    # Assert
    assert response.status_code == 404
    assert data["detail"] == "Activity not found"
