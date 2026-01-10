from app.db.models.reference_identifier import ReferenceIdentifier


def test_reference_identifier_nnt_is_uppercased_even_if_type_set_after_value():
    rid = ReferenceIdentifier()
    rid.value = "2019lysem032"
    rid.type = "nnt"
    assert rid.value == "2019LYSEM032"
