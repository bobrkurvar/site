from domain import Category, Collection, Image


def test_collection_merges_only_unique_categories():
    collection = Collection(
        name="Marble", categories=Category(name="cat1"), image=Image(image_path="asdf")
    )
    new_categories = [Category(name="cat1"), Category(name="cat2")]

    collection.merge_categories(new_categories)

    assert len(collection.categories) == 2
    assert {"cat1", "cat2"} == {cat.name for cat in collection.categories}
