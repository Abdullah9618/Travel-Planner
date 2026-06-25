"""
spaCy-powered NLP query parser for travel planning.

This version uses spaCy tokenization, entity rulers, and matcher patterns to
extract intent, duration, budget, destination, and travel preferences in a way
that is much closer to a real NLP pipeline than the previous regex-only
implementation.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

import spacy
from spacy.matcher import Matcher


class QueryParser:
    """Parse natural language travel queries into structured parameters."""

    def __init__(self):
        self.intent_keywords = {
            "travel_planning": ["plan", "itinerary", "trip", "schedule", "generate", "arrange", "create"],
            "budget_check": ["budget", "under", "below", "within", "max", "maximum", "cost", "cheapest", "affordable"],
            "search": ["find", "show", "recommend", "suggest", "best", "top", "places", "destination"],
            "weather": ["weather", "climate", "temperature", "season", "seasonal"],
        }

        self.regions = {
            "northern": ["Gilgit Baltistan", "KPK", "AJK"],
            "north": ["Gilgit Baltistan", "KPK", "AJK"],
            "southern": ["Sindh", "Balochistan"],
            "south": ["Sindh", "Balochistan"],
            "punjab": ["Punjab"],
            "sindh": ["Sindh"],
            "balochistan": ["Balochistan"],
            "kpk": ["KPK"],
            "gilgit": ["Gilgit Baltistan"],
            "kashmir": ["AJK"],
            "azad kashmir": ["AJK"],
        }

        self.travel_types = {
            "adventure": "Adventure",
            "adventurous": "Adventure",
            "hiking": "Adventure",
            "trekking": "Adventure",
            "relaxation": "Relaxation",
            "relaxing": "Relaxation",
            "peaceful": "Relaxation",
            "beach": "Relaxation",
            "family": "Family",
            "family-friendly": "Family",
            "kids": "Family",
            "children": "Family",
            "cultural": "Cultural",
            "culture": "Cultural",
            "heritage": "Cultural",
            "historical": "Historical",
            "history": "Historical",
            "religious": "Religious",
            "spiritual": "Religious",
        }

        self.seasons = {
            "summer": "Summer",
            "winter": "Winter",
            "spring": "Spring",
            "autumn": "Autumn",
            "fall": "Autumn",
            "monsoon": "Monsoon",
        }

        self.activities = [
            "hiking",
            "trekking",
            "camping",
            "photography",
            "sightseeing",
            "swimming",
            "boating",
            "skiing",
            "shopping",
            "rafting",
            "paragliding",
            "rock climbing",
            "fishing",
            "bird watching",
        ]

        self.dest_map = {
            "hunza": "Hunza",
            "skardu": "Skardu",
            "sakardu": "Skardu",
            "fairy meadows": "Fairy Meadows",
            "naran": "Naran",
            "kaghan": "Kaghan",
            "swat": "Swat",
            "murree": "Murree",
            "nathia gali": "Nathia Gali",
            "lahore": "Lahore",
            "karachi": "Karachi",
            "gwadar": "Gwadar",
            "quetta": "Quetta",
            "neelum valley": "Neelum Valley",
            "neelam": "Neelum Valley",
            "malam jabba": "Malam Jabba",
            "taxila": "Taxila",
            "mohenjo daro": "Mohenjo Daro",
            "khunjerab": "Khunjerab",
            "deosai": "Deosai",
            "saif ul malook": "Saif Ul Malook",
            "attabad lake": "Attabad Lake",
            "shangrila": "Shangrila",
            "chitral": "Chitral",
            "islamabad": "Islamabad",
            "peshawar": "Peshawar",
        }

        self.region_tokens = {
            "pakistan",
            "north",
            "northern",
            "south",
            "southern",
            "east",
            "western",
            "punjab",
            "sindh",
            "balochistan",
            "kpk",
            "gilgit baltistan",
            "kashmir",
            "ajk",
            "azad kashmir",
            "islamabad",
            "capital territory",
        }

        self._nlp = self._build_pipeline()
        self._matcher = Matcher(self._nlp.vocab)
        self._configure_matcher()

    def _build_pipeline(self):
        try:
            nlp = spacy.load("en_core_web_sm")
        except Exception:
            nlp = spacy.blank("en")

        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer")

        if "entity_ruler" in nlp.pipe_names:
            nlp.remove_pipe("entity_ruler")

        ruler = nlp.add_pipe("entity_ruler", config={"overwrite_ents": True})

        def phrase_patterns(label: str, values: List[str]):
            return [{"label": label, "pattern": value} for value in values if value]

        destination_values = sorted(set(self.dest_map.values()))
        region_values = sorted({region for regions in self.regions.values() for region in regions} | {
            "Gilgit Baltistan",
            "KPK",
            "Punjab",
            "Sindh",
            "Balochistan",
            "AJK",
            "Islamabad Capital Territory",
        })

        patterns = []
        patterns.extend(phrase_patterns("DESTINATION", destination_values))
        patterns.extend(phrase_patterns("DESTINATION", sorted(self.dest_map.keys())))
        patterns.extend(phrase_patterns("REGION", region_values))
        patterns.extend(phrase_patterns("TRAVEL_TYPE", sorted(set(self.travel_types.values()))))
        patterns.extend(phrase_patterns("SEASON", sorted(set(self.seasons.values()))))
        patterns.extend(phrase_patterns("ACTIVITY", sorted({activity.title() for activity in self.activities})))
        ruler.add_patterns(patterns)

        return nlp

    def _configure_matcher(self):
        for intent, keywords in self.intent_keywords.items():
            self._matcher.add(
                intent.upper(),
                [[{"LOWER": keyword}] for keyword in keywords],
            )

        self._matcher.add(
            "DURATION",
            [
                [{"LIKE_NUM": True}, {"LOWER": {"IN": ["day", "days", "night", "nights"]}}],
                [{"LOWER": "weekend"}],
                [{"LOWER": "week"}],
                [{"LOWER": "a"}, {"LOWER": "week"}],
            ],
        )

        self._matcher.add(
            "BUDGET_HINT",
            [[{"LOWER": {"IN": ["under", "below", "within", "budget", "max", "maximum", "affordable", "cheapest"]}}]],
        )

    def parse(self, query: str) -> Dict:
        """Parse a natural language query and extract travel parameters."""
        query = query or ""
        doc = self._nlp(query)
        query_lower = query.lower()

        result = {
            "original_query": query,
            "intent": self._extract_intent(doc, query_lower),
            "days": self._extract_days(doc, query_lower),
            "budget": self._extract_budget(doc, query_lower),
            "region": self._extract_region(doc, query_lower),
            "type": self._extract_type(doc, query_lower),
            "season": self._extract_season(doc, query_lower),
            "activities": self._extract_activities(doc, query_lower),
            "destination": self._extract_destination(doc, query_lower),
            "entities": self._extract_entities(doc, query_lower),
        }

        result["confidence"] = self._estimate_confidence(result)
        return {k: v for k, v in result.items() if v is not None or k == "original_query"}

    def _extract_intent(self, doc, query: str) -> str:
        scores = {key: 0 for key in self.intent_keywords}

        for match_id, _, _ in self._matcher(doc):
            label = self._nlp.vocab.strings[match_id].lower()
            if label in scores:
                scores[label] += 1

        if scores["travel_planning"] and any(term in query for term in ["day", "days", "trip", "itinerary"]):
            scores["travel_planning"] += 1
        if scores["budget_check"] and any(term in query for term in ["pkr", "rs", "rupees", "k"]):
            scores["budget_check"] += 1

        best_intent = max(scores, key=scores.get)
        return best_intent if scores[best_intent] else "general_query"

    def _extract_days(self, doc, query: str) -> Optional[int]:
        patterns = [
            r"(\d+)\s*-?\s*days?",
            r"(\d+)\s*-?\s*nights?",
            r"for\s+(\d+)\s*days?",
        ]
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return int(match.group(1))

        token_numbers = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "weekend": 2,
        }
        for token in doc:
            value = token_numbers.get(token.lower_)
            if value:
                return value
        if "a week" in query:
            return 7
        return None

    def _extract_budget(self, doc, query: str) -> Optional[int]:
        patterns = [
            r"(?:under|below|within|budget\s+of?|less\s+than|max(?:imum)?)\s*(?:pkr|rs\.?)?\s*([\d,]+)\s*(?:pkr|rs\.?)?",
            r"([\d,]+)\s*(?:pkr|rs\.?|rupees?)",
            r"(?:pkr|rs\.?)\s*([\d,]+)",
            r"(\d+)\s*k\b",
        ]

        for index, pattern in enumerate(patterns):
            match = re.search(pattern, query)
            if not match:
                continue
            amount = match.group(1).replace(",", "")
            try:
                budget = int(amount)
                if index == 3:
                    budget *= 1000
                return budget
            except ValueError:
                continue
        return None

    def _extract_region(self, doc, query: str) -> Optional[str]:
        for ent in doc.ents:
            if ent.label_ == "REGION":
                return ent.text

        for keyword, regions in self.regions.items():
            if keyword in query:
                return regions[0]

        place_regions = {
            "hunza": "Gilgit Baltistan",
            "skardu": "Gilgit Baltistan",
            "sakardu": "Gilgit Baltistan",
            "naran": "KPK",
            "kaghan": "KPK",
            "swat": "KPK",
            "murree": "Punjab",
            "lahore": "Punjab",
            "islamabad": "Islamabad Capital Territory",
            "karachi": "Sindh",
            "gwadar": "Balochistan",
            "quetta": "Balochistan",
            "neelum": "AJK",
            "neelam": "AJK",
            "muzaffarabad": "AJK",
        }

        for place, region in place_regions.items():
            if place in query:
                return region

        return None

    def _extract_type(self, doc, query: str) -> Optional[str]:
        for ent in doc.ents:
            if ent.label_ == "TRAVEL_TYPE":
                return ent.text.title() if ent.text.lower() not in self.travel_types else self.travel_types[ent.text.lower()]

        for keyword, travel_type in self.travel_types.items():
            if keyword in query:
                return travel_type
        return None

    def _extract_season(self, doc, query: str) -> Optional[str]:
        for ent in doc.ents:
            if ent.label_ == "SEASON":
                return ent.text.title() if ent.text.lower() not in self.seasons else self.seasons[ent.text.lower()]

        for keyword, season in self.seasons.items():
            if keyword in query:
                return season
        return None

    def _extract_activities(self, doc, query: str) -> Optional[List[str]]:
        found = []
        for ent in doc.ents:
            if ent.label_ == "ACTIVITY":
                found.append(ent.text.title())

        query_lower = query.lower()
        for activity in self.activities:
            if activity in query_lower:
                found.append(activity.title())

        for pattern in [
            r"\bfor\s+([a-zA-Z\s]+?)(?:\s+(?:under|in|to)|\s*$)",
            r"\bwant\s+to\s+([a-zA-Z\s]+?)(?:\s+(?:under|in)|\s*$)",
            r"\blike\s+to\s+([a-zA-Z\s]+?)(?:\s+(?:under|in)|\s*$)",
            r"\benjoy\s+([a-zA-Z\s]+?)(?:\s+(?:under|in)|\s*$)",
        ]:
            match = re.search(pattern, query_lower)
            if match:
                potential_activity = match.group(1).strip()
                for activity in self.activities:
                    if activity in potential_activity:
                        found.append(activity.title())

        unique = sorted(set(found))
        return unique or None

    def _extract_destination(self, doc, query: str) -> Optional[str]:
        for ent in doc.ents:
            if ent.label_ == "DESTINATION":
                return ent.text

        for key, actual_name in sorted(self.dest_map.items(), key=lambda item: len(item[0]), reverse=True):
            if re.search(rf"\b{re.escape(key)}\b", query):
                return actual_name

        destination_patterns = [
            r"\bto\s+([a-zA-Z\s]+?)(?:\s+(?:under|for|with|in)|\s*$)",
            r"\bin\s+([a-zA-Z\s]+?)(?:\s+(?:under|for|with)|\s*$)",
            r"\bvisit\s+([a-zA-Z\s]+?)(?:\s+(?:under|for|with)|\s*$)",
            r"\bnear\s+([a-zA-Z\s]+?)(?:\s+(?:under|for|with)|\s*$)",
            r"\baround\s+([a-zA-Z\s]+?)(?:\s+(?:under|for|with)|\s*$)",
            r"\btrip\s+to\s+([a-zA-Z\s]+?)(?:\s+(?:under|for|with)|\s*$)",
        ]

        for pattern in destination_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if not match:
                continue
            potential_dest = match.group(1).strip().lower()
            if any(token in potential_dest for token in self.region_tokens):
                continue
            for key, actual_name in self.dest_map.items():
                if key in potential_dest or potential_dest in key:
                    return actual_name

        return None

    def _extract_entities(self, doc, query: str) -> Dict[str, object]:
        return {
            "destination_candidates": sorted({ent.text for ent in doc.ents if ent.label_ == "DESTINATION"}),
            "region_candidates": sorted({ent.text for ent in doc.ents if ent.label_ == "REGION"}),
            "travel_style_mentions": sorted({ent.text for ent in doc.ents if ent.label_ == "TRAVEL_TYPE"}),
            "season_mentions": sorted({ent.text for ent in doc.ents if ent.label_ == "SEASON"}),
            "activity_mentions": self._extract_activities(doc, query) or [],
        }

    def _estimate_confidence(self, result: Dict) -> float:
        matches = 0.0
        total_signals = 6.0

        for key in ["intent", "days", "budget", "region", "type", "destination"]:
            if result.get(key):
                matches += 1.0

        activities = result.get("activities") or []
        if activities:
            matches += 0.5
            total_signals += 0.5

        entities = result.get("entities") or {}
        for key in ["destination_candidates", "region_candidates", "travel_style_mentions", "season_mentions"]:
            if entities.get(key):
                matches += 0.25
                total_signals += 0.25

        confidence = matches / total_signals if total_signals else 0.0
        return round(min(confidence, 1.0), 2)


if __name__ == "__main__":
    parser = QueryParser()
    test_queries = [
        "Plan a 3-day trip to northern Pakistan under 25,000 PKR",
        "Looking for adventure spots with budget 15k",
        "Family trip to Murree for weekend",
        "Best places for hiking in Gilgit under 30000 rupees",
        "Relaxing beach vacation in Gwadar for 5 days",
        "Cultural tour of Lahore under Rs. 20,000",
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        result = parser.parse(query)
        for key, value in result.items():
            if key != "original_query":
                print(f"  {key}: {value}")
