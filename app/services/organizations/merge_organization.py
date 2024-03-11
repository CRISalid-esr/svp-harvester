from app.db.models.organization import Organization


def merge_organization(organization: Organization, organization_to_merge: Organization):
    """
    Merge two organizations into one

    :param organization: the organization to merge into
    :param organization_to_merge: the organization to merge
    :return: the merged organization
    """
    organization.identifiers = list(
        set(organization.identifiers + organization_to_merge.identifiers)
    )
    return organization
