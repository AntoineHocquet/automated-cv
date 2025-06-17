from backend.models.letter import LetterSpec

letter = LetterSpec(
    ad_language="french",
    introduction="Dear Hiring Manager,",
    body="This is the body of the letter. I am passionate about machine learning and data science.",
    closing="Sincerely, Antoine Hocquet"
)

letter.translate_to_ad_language()

print("=== Translated Introduction ===\n", letter.introduction)
print("\n=== Translated Body ===\n", letter.body)
print("\n=== Translated Closing ===\n", letter.closing)
