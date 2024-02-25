import json
import re
from typing import List, Tuple
import aiohttp
from loguru import logger
from rdflib import Literal

from app.db.models.concept import Concept as DbConcept
from app.db.models.label import Label as DbLabel
from app.services.concepts.concept_informations import ConceptInformations
from app.services.concepts.concept_solver import ConceptSolver
from app.services.concepts.dereferencing_error import DereferencingError


class WikidataConceptSolver(ConceptSolver):
    """
    Wikidata concept solver
    """

    async def solve(self, concept_informations: ConceptInformations) -> DbConcept:
        """
        Solves a Wikidata concept from a concept id
        :param concept_informations: concept informations
        :return: Concept
        """

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=float(10))
            ) as session:
                async with session.get(concept_informations.url) as response:
                    if not 200 <= response.status < 300:
                        raise DereferencingError(
                            "Endpoint returned status "
                            f"{response.status} while dereferencing "
                            f"{concept_informations.uri} "
                            f"at url {concept_informations.url}"
                        )
                    json_response = await response.json()
                    concept_data: json = json_response["entities"][
                        concept_informations.code
                    ]
                    concept = DbConcept(uri=concept_informations.uri)
                    # _alt_labels : [[{'language': 'zh', 'value': '人文科學'}, {'language': 'zh', 'value': '人文學'}, {'language': 'zh', 'value': '人文'}, {'language': 'zh', 'value': '人文科学'}], [{'language': 'pl', 'value': 'humanistyka'}], [{'language': 'es', 'value': 'humanistica'}, {'language': 'es', 'value': 'letras humanas'}, {'language': 'es', 'value': 'saber humanístico'}, {'language': 'es', 'value': 'saberes humanísticos'}, {'language': 'es', 'value': 'ciencia humana'}, {'language': 'es', 'value': 'letras'}, {'language': 'es', 'value': 'ciencias humanas'}, {'language': 'es', 'value': 'saber humanistico'}, {'language': 'es', 'value': 'saberes humanisticos'}], [{'language': 'et', 'value': 'Humanitaarteadus'}, {'language': 'et', 'value': 'Humanitaaria'}], [{'language': 'sv', 'value': 'humanvetenskap'}, {'language': 'sv', 'value': 'humanoira'}], [{'language': 'nl', 'value': 'Geesteswetenschap'}, {'language': 'nl', 'value': 'Letteren en Wijsbegeerte'}], [{'language': 'ar', 'value': 'الإنسانيات'}, {'language': 'ar', 'value': 'العلوم الانسانية'}, {'language': 'ar', 'value': 'علوم إنسانية'}, {'language': 'ar', 'value': 'العلوم الإنسانية'}], [{'language': 'eo', 'value': 'homsciencoj'}, {'language': 'eo', 'value': 'homscienco'}, {'language': 'eo', 'value': 'homaj sciencoj'}, {'language': 'eo', 'value': 'socia scienco'}], [{'language': 'yi', 'value': 'מדעי הרוח'}, {'language': 'yi', 'value': 'הומענעטיס'}, {'language': 'yi', 'value': 'הומאנעטיס'}], [{'language': 'tr', 'value': 'beşeri bilim'}, {'language': 'tr', 'value': 'beşerî bilimler'}], [{'language': 'fi', 'value': 'humanistinen tiede'}, {'language': 'fi', 'value': 'humanistinen tutkimus'}, {'language': 'fi', 'value': 'humanistiset aineet'}], [{'language': 'tl', 'value': 'Mga araling pang-tao'}, {'language': 'tl', 'value': 'Pagiging tao'}, {'language': 'tl', 'value': 'Pantao'}, {'language': 'tl', 'value': 'Humanist'}, {'language': 'tl', 'value': 'Pang-tao'}, {'language': 'tl', 'value': 'Mga araling pantao'}, {'language': 'tl', 'value': 'Maka-pantao'}, {'language': 'tl', 'value': 'Mga humanidades'}, {'language': 'tl', 'value': 'Umanidades'}, {'language': 'tl', 'value': 'Humanismo'}, {'language': 'tl', 'value': 'Araling ukol sa tao'}, {'language': 'tl', 'value': 'Humanism'}, {'language': 'tl', 'value': 'Pantaong aralin'}, {'language': 'tl', 'value': 'Mga araling nauukol sa tao'}, {'language': 'tl', 'value': 'Pan-tao'}, {'language': 'tl', 'value': 'Pangtao'}, {'language': 'tl', 'value': 'Mga araling hinggil sa sangkatauhan'}, {'language': 'tl', 'value': 'Humanista'}, {'language': 'tl', 'value': 'Mga araling pangtao'}, {'language': 'tl', 'value': 'Umanista'}, {'language': 'tl', 'value': 'Mga pagkatao'}, {'language': 'tl', 'value': 'Araling nauukol sa tao'}, {'language': 'tl', 'value': 'Mga araling ukol sa tao'}, {'language': 'tl', 'value': 'Mga umanidades'}, {'language': 'tl', 'value': 'Humanists'}, {'language': 'tl', 'value': 'Makapangtao'}, {'language': 'tl', 'value': 'Makapantao'}, {'language': 'tl', 'value': 'The Humanities'}, {'language': 'tl', 'value': 'Umanismo'}, {'language': 'tl', 'value': 'Humanities'}, {'language': 'tl', 'value': 'Pag-aaral ng pagkatao'}, {'language': 'tl', 'value': 'Mga aralin hinggil sa sangkatauhan'}, {'language': 'tl', 'value': 'araling pantao'}], [{'language': 'da', 'value': 'humanvidenskab'}], [{'language': 'an', 'value': 'Umanidaz'}], [{'language': 'ko', 'value': '인문과학'}, {'language': 'ko', 'value': '인문학자'}, {'language': 'ko', 'value': '인문 과학'}, {'language': 'ko', 'value': '인문'}], [{'language': 'bar', 'value': 'Geisteswissenschaft'}], [{'language': 'it', 'value': 'lettere e filosofia'}, {'language': 'it', 'value': 'umanistica'}], [{'language': 'id', 'value': 'Ilmu Budaya'}], [{'language': 'ja', 'value': '人文'}, {'language': 'ja', 'value': '人文科学'}, {'language': 'ja', 'value': 'ヒューマニティクス'}, {'language': 'ja', 'value': 'アーテス・ウマニオレス'}], [{'language': 'vi', 'value': 'nhân văn'}], [{'language': 'sh', 'value': 'Humanističke nauke'}], [{'language': 'sk', 'value': 'Humanitné vedy'}, {'language': 'sk', 'value': 'Humanitná veda'}, {'language': 'sk', 'value': 'Duchovné vedy'}], [{'language': 'th', 'value': 'มนุษย์ศาสตร์'}, {'language': 'th', 'value': 'Humanities'}], [{'language': 'ca', 'value': 'filosofia i lletres'}, {'language': 'ca', 'value': 'lletres'}], [{'language': 'sl', 'value': 'humanistične vede'}], [{'language': 'cs', 'value': 'humanitní věda'}], [{'language': 'fa', 'value': 'علوم\u200cانسانی'}], [{'language': 'bg', 'value': 'Социалните науки'}, {'language': 'bg', 'value': 'Социална наука'}, {'language': 'bg', 'value': 'Хуманитарните науки'}, {'language': 'bg', 'value': 'Хуманитарна наука'}, {'language': 'bg', 'value': 'Хуманитаристика'}], [{'language': 'gv', 'value': 'Dooieaghtyn'}], [{'language': 'nb', 'value': 'humanistiske fag'}], [{'language': 'ru', 'value': 'гуманитарное знание'}, {'language': 'ru', 'value': 'гуманитарная сфера'}, {'language': 'ru', 'value': 'социальные науки'}, {'language': 'ru', 'value': 'гуманитарная наука'}, {'language': 'ru', 'value': 'социальная наука'}], [{'language': 'gl', 'value': 'humanistica'}], [{'language': 'tg', 'value': 'Илмҳои гуманитарӣ'}], [{'language': 'tt', 'value': 'гуманитар фәннәр'}], [{'language': 'tt-cyrl', 'value': 'гуманитар фәннәр'}], [{'language': 'ga', 'value': 'sruithléann'}], [{'language': 'ro', 'value': 'ştiinţe umaniste'}], [{'language': 'sq', 'value': 'Humanistika'}, {'language': 'sq', 'value': 'Shkencat humane'}], [{'language': 'fr', 'value': 'humanités'}], [{'language': 'de', 'value': 'Geisteswissenschaft'}], [{'language': 'cy', 'value': 'y dyniaethau'}], [{'language': 'en', 'value': 'arts and humanities'}], [{'language': 'sms', 'value': 'humaniistlaž tiõtti'}]]

                    self._add_labels(
                        concept=concept,
                        labels=[
                            Literal(pair["value"], lang=pair["language"])
                            for language_value_pairs in self._alt_labels(
                                concept_data
                            ).values()
                            for pair in language_value_pairs
                        ],
                        preferred=False,
                    )
                    self._add_labels(
                        concept=concept,
                        labels=[
                            Literal(pair["value"], lang=pair["language"])
                            for pair in self._pref_labels(concept_data).values()
                        ],
                        preferred=True,
                    )
                    return concept

        except aiohttp.ClientError as error:
            logger.error(
                f"Endpoint failure while dereferencing {concept_informations.uri}"
                f"at url {concept_informations.url} with message {error}"
            )
            raise DereferencingError(
                f"Endpoint failure while dereferencing {concept_informations.uri}"
                f"at url {concept_informations.url} with message {error}"
            ) from error
        except Exception as error:
            logger.error(
                f"Exception failure dereferencing {concept_informations.uri}"
                f"at url {concept_informations.url} with message {error}"
            )
            raise DereferencingError(
                f"Unknown error while dereferencing {wikidata_uri} with message {error}"
            ) from error

    def _alt_labels(self, concept_data: json) -> List[str]:
        return concept_data.get("aliases", {})

    # pylint: disable=unused-argument
    def _pref_labels(self, concept_data: json) -> List[str]:
        return concept_data.get("labels", {})

    def _add_labels(self, concept: DbConcept, labels: dict, preferred: bool = True):
        def interesting_labels(label_language):
            a = (
                label_language in self.settings.concept_languages
                or label_language is None
            )
            return a

        if len(labels) == 0:
            return
        if preferred:
            preferred_labels = [
                labels[label_language]
                for label_language in labels
                if interesting_labels(label_language)
            ]
            for label in preferred_labels:
                self._add_label(concept, label, preferred)

        else:
            alt_labels = [
                labels[label_language][0]
                for label_language in labels
                if interesting_labels(label_language)
            ]
            for label in alt_labels:
                self._add_label(concept, label, preferred)

    def _add_label(self, concept, label, preferred):
        concept.labels.append(
            DbLabel(
                value=label["value"],
                language=label["language"],
                preferred=preferred,
            )
        )

    def complete_information(
        self,
        concept_informations: ConceptInformations,
    ) -> None:
        """
        Ensure uri/code consistency and set URL
        :param concept_informations: concept informations
        :return: None
        """
        if concept_informations.code is None and concept_informations.uri is None:
            raise DereferencingError(
                f"Neither code nor uri provided for {concept_informations}"
            )
        if concept_informations.uri is not None:
            concept_informations.code = re.sub(
                r"https?://www.wikidata.org/(wiki|entity)/",
                "",
                concept_informations.uri,
            )
        if concept_informations.code is not None:
            concept_informations.uri = (
                f"http://www.wikidata.org/entity/{concept_informations.code}"
            )
        assert (
            concept_informations.uri is not None
        ), "Concept URI should not be None at this point"
        assert (
            concept_informations.code is not None
        ), "Concept code should not be None at this point"
        concept_informations.url = f"https://www.wikidata.org/wiki/Special:EntityData/{concept_informations.code}.json"
