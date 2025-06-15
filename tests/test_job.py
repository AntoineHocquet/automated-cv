from backend.models.job import Job

def test_job_parsing():
    raw_text = """
    We are hiring a Machine Learning Scientist at Zalando in Berlin.
    The role was posted at an unknown date.
    Responsibilities include building scalable ML models and working with big data technologies.
    """

    # ✅ use the class method to parse and build the Job
    job = Job.populate_from_llm(raw_text=raw_text, source="test_zalando.txt")

    print("\n","Parsed Job Object:","\n", job, "\n")
    print("Keywords:", job.keywords)

    assert job.company_name is not None
    assert job.title is not None
    assert job.keywords
