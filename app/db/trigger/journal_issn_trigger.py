CHECK_ISSN_OVERLAP = """
    CREATE OR REPLACE FUNCTION check_issn_overlap() RETURNS TRIGGER AS $$
    BEGIN
        -- Check for any existing entry with an overlapping issn
        IF EXISTS (SELECT 1 FROM journals WHERE issn && NEW.issn) THEN
            RAISE EXCEPTION 'ISSN overlap detected';
        END IF;
        -- Check for any existing entry with an overlapping eissn
        IF EXISTS (SELECT 1 FROM journals WHERE eissn && NEW.eissn) THEN
            RAISE EXCEPTION 'EISSN overlap detected';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """

CREATE_TRIGGER_JOURNAL_ISSN = """
    CREATE TRIGGER check_issn_before_insert
        BEFORE INSERT ON journals
        FOR EACH ROW EXECUTE FUNCTION check_issn_overlap();
    """

DROP_TRIGGER_JOURNAL_ISSN = """
    DROP TRIGGER IF EXISTS check_issn_before_insert ON journal;
    DROP FUNCTION IF EXISTS check_issn_overlap;
    """
