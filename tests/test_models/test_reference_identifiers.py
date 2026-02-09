from app.db.models.reference_identifier import ReferenceIdentifier


def test_reference_identifier_nnt_is_uppercased_even_if_type_set_after_value():
    rid = ReferenceIdentifier()
    rid.value = "2019lysem032"
    rid.type = "nnt"
    assert rid.value == "2019LYSEM032"


def test_reference_identifier_sudoc_ppn_trailing_x_is_uppercased():
    rid1 = ReferenceIdentifier()
    rid1.value = "258403519x"
    rid1.type = "ppn"
    assert rid1.value == "258403519X"

    rid2 = ReferenceIdentifier()
    rid2.value = "258403519X"
    rid2.type = "ppn"
    assert rid2.value == rid1.value
