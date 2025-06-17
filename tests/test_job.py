from backend.models.job import Job

def test_job_parsing():
    raw_text = """
    We are hiring a Machine Learning Scientist at Zalando in Berlin.
    The role was posted at an unknown date.
    Responsibilities include building scalable ML models and working with big data technologies.
    """

    print("Raw text:", raw_text)

    # ✅ use the class method to parse and build the Job
    job = Job.populate_from_llm(raw_text=raw_text, source="Linkedin")

    print("\nParsed job:")
    print("Source:", job.source)
    print("Language:", job.language)
    print("Job title:", job.title)
    print("Company name:", job.company_name)
    print("Keywords:", job.keywords)

    assert job.company_name is not None
    assert job.source is not None
    assert job.language is not None
    assert job.post_date is not None
    assert job.title is not None
    assert job.keywords
