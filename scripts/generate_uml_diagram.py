# may require `apt install graphviz` on linux terminals
import os
import sys

if os.path.basename(os.getcwd()) != "scripts":
    print("Please execute this script from the scripts directory")
    sys.exit(1)
sys.path.append("..")
os.environ["APP_ENV"] = "DEV"

from app.db.session import Base
from app.db.models import (
    abstract,
    affiliations,
    concept,
    contribution,
    contributor,
    document_type,
    entity,
    harvesting,
    harvesting_error,
    identifier,
    label,
    reference_literal_field,
    organization,
    person,
    reference,
    reference_event,
    references_document_type,
    references_subject,
    retrieval,
    subtitle,
    title,
    versioned_record,
)
from sqlalchemy_schemadisplay import create_uml_graph

graph = create_uml_graph(
    Base.registry.mappers,
    show_operations=False,
    show_multiplicity_one=True,
)
graph.write_png("../img/sql_alchemy_entities.png")
