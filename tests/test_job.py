from backend.models.job import Job


def test_job_parsing():
    raw_text = """
    We are hiring a Machine Learning Scientist at Zalando in Berlin.
    The role was posted on 2024-05-20.
    Responsibilities include building scalable ML models and working with big data technologies.
    """
    
    job = Job(raw_text, source="test_zalando.txt")
    job.populate_from_llm()

    print("Parsed Job Object:", job)
    print("Keywords:", job.keywords)

    assert job.company_name is not None
    assert job.title is not None
    assert job.keywords
