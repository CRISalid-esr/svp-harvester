# Prefix HAL contributor identifiers — Issue #910

## Context

HAL contributors are identified in `HalReferencesConverter._add_contributions` from the
`authFullNameFormIDPersonIDIDHal_fs` facet, whose format is:

```
<full name>_FacetSep_<formId>-<idHal numeric>_FacetSep_<idHal string>
```

The current code picks the numeric idHal when present, and silently falls back to the author-form ID
when the contributor has no idHal (`id_hal == "0"`):

```python
identifier=id_hal if id_hal != "0" else form_id,
```

**This is a design flaw.** Form IDs and numeric idHals are two independent HAL namespaces that both
produce plain integers. Contributors are deduplicated by the unique index on
`(source, source_identifier)` in the `contributors` table, so a contributor whose numeric idHal is
`12345` and a *different* contributor whose form ID is `12345` collide into a single `Contributor`
row — their name variants, external identifiers and contributions get merged.

A second latent bug follows from the same ambiguity: `_add_organization` matches affiliations by
comparing `contributor.source_identifier` to the idHal parsed from `authIdHasPrimaryStructure_fs`.
For form-based contributors the comparison is `form_id != "0"` — never true — so contributors
without an idHal currently get **no affiliations** (or, worse, someone else's on a numeric
collision).

## Decision

Prefix **both** namespaces so the value spaces are disjoint and self-describing
(option 2 of the analysis). The deployment includes a **full database wipe**, so there is no
migration and no harvester version bump: all references are re-harvested from scratch.

## New identifier scheme

`Contributor.source_identifier` for `source = "hal"` becomes:

| Case | Old value | New value |
|---|---|---|
| Contributor has a numeric idHal | `12345` | `idhal:12345` |
| No idHal (`id_hal == "0"`), form ID fallback | `829106` | `form:829106` |

- The separator is `:` — it cannot appear in either numeric value, so parsing is unambiguous.
- The bare `id_hal == "0"` sentinel keeps its current meaning ("no idHal"); `idhal:0` must never be
  produced.
- The prefixes are HAL-internal namespaces for `source_identifier` only. They are **not** ecosystem
  identifier keys from `identifiers.yml`; the typed identifiers in `contributor.identifiers`
  (`ContributorIdentifier`, e.g. type `idhali`) keep their bare, unprefixed values.

Define the two prefixes as constants on `HalReferencesConverter` (e.g. `IDHAL_PREFIX = "idhal:"`,
`FORM_PREFIX = "form:"`) — no magic strings at the three usage sites.

## Code changes

All changes are in `app/harvesters/hal/hal_references_converter.py` unless noted.

### 1. `_add_contributions`

```python
identifier=f"idhal:{id_hal}" if id_hal != "0" else f"form:{form_id}",
```

The *raw* `id_hal` keeps being passed to `tei_decoder.get_identifiers(id_hal)` — the TEI XPath in
`hal_tei_interface.py` matches `idno[@type='idhal'][@notation='numeric']` text content, which is
unprefixed in the TEI payload. Do not prefix that call.

### 2. `_organizations_from_contributor`

The method receives `contribution.contributor.source_identifier` (now prefixed) via
`AbstractReferencesConverter._add_organization` and matches it against
`authIdHasPrimaryStructure_fs` entries of format:

```
<formId>-<idHal>_FacetSep_<name>_JoinSep_<orgId>_FacetSep_<orgName>
```

Update the matching to parse **both** `form_id` and `id_hal` from the facet and compare on the
right namespace:

- `idhal:<n>` → match when the facet's idHal equals `<n>`
- `form:<n>` → match when the facet's formId equals `<n>` (and the facet's idHal is `0`)

This fixes affiliation resolution for contributors without an idHal, which never matched before.

### 3. Sanity guard (optional but recommended)

If the `ids` segment of `authFullNameFormIDPersonIDIDHal_fs` does not split into exactly two parts,
raise `UnexpectedFormatException` (today a malformed value would raise a bare `ValueError` from
tuple unpacking).

## What does NOT change

- `ContributorIdentifier` rows (typed identifiers from TEI: orcid, idref, idhali…) — bare values.
- `ReferenceIdentifier`s of the reference itself (`halId_s`, `doiId_s`, …).
- `hash_keys` — the facet field is already included; hashing is on raw payload, not on the derived
  identifier.
- Other harvesters (scanr, openalex, scopus, idref) — their contributor namespaces are scoped by
  their own `source` value and are single-namespace; out of scope.
- No Alembic migration, no `harvesters.yml` version bump: the database is wiped at deployment.

## Downstream impact (coordination required)

`Contributor.source_identifier` is exposed in outbound `event.references.reference.*` messages and
in the REST/history API. Consumers that match HAL contributors on a bare numeric idHal
(crisalid-ikg researcher matching) must be adapted to either:

- parse the `idhal:` prefix from `contributor.source_identifier`, or
- preferably, match on the typed `identifiers` list (type `idhali`), which is unaffected.

This spec only covers svp-harvester; the crisalid-ikg change ships separately and must be deployed
together with the DB wipe.

## Tests

Update / add in `tests/test_harvesters/test_hal/`:

1. **Prefixing** — a payload with an idHal contributor yields `source_identifier == "idhal:<n>"`; a
   payload with `-0` yields `source_identifier == "form:<formId>"`.
2. **Collision regression test** — one reference where contributor A has idHal `N` and contributor B
   has form ID `N` (idHal `0`): two distinct `Contributor` rows must be created.
3. **Affiliations via idHal** — existing affiliation tests updated for the prefixed comparison.
4. **Affiliations via form ID** — a no-idHal contributor whose `authIdHasPrimaryStructure_fs` entry
   carries the matching form ID gets its affiliation (previously silently dropped).
5. Existing HAL fixtures: expected contributor identifiers updated to the prefixed form.