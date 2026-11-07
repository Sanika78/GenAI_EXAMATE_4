from app.models import Record

article = Record(
    article_no="14",
    title="Equality before law",
    part="Part III",
    text="The State shall not deny any person equality before the law.",
    amended_by=[],
    source_page=5
)

print(article)