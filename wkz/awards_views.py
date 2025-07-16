from typing import Dict, List, Union

from django.shortcuts import render

from wkz import configuration as cfg
from wkz import models
from wkz.views import WKZView

awards_info_texts = {
    "general": (
        f"This page lists the top {cfg.rank_limit} activities in the respective category. Both individual "
        "activities and entire sports can be disabled for awards."
    ),
    "fastest": (
        "The fastest sections are determined by computing the average velocity over the given section distance."
    ),
    "climb": (
        "The best climb sections are determined by computing the accumulated evelation gain per minute over the "
        "given section distance."
    ),
    "ascent": ("The total ascent equals the aggregated sum of all uphill meters gained during one activity."),
}


class AwardsViews(WKZView):
    template_name = "awards/awards.html"

    def get(self, request):
        context = self.get_context_data()
        context["page_name"] = "Awards"

        # get fastest awards
        top_fastest_awards = get_top_awards_for_all_sports(request.user, top_score=cfg.rank_limit, kinds=["fastest"])
        context["top_fastest_awards"] = top_fastest_awards

        # get climb awards
        top_climb_awards = get_top_awards_for_all_sports(request.user, top_score=cfg.rank_limit, kinds=["climb"])
        context["top_climb_awards"] = top_climb_awards

        # get ascent awards
        top_ascent_awards = _get_top_ascent_awards_for_all_sports(request.user)
        context["top_ascent_awards"] = top_ascent_awards

        # get info text for hover over question mark
        context["info_text"] = awards_info_texts

        return render(request, template_name=self.template_name, context=context)


def _get_top_ascent_awards_for_all_sports(user) -> Dict[models.Sport, list]:
    top_awards = {}
    sports_filter = {"evaluates_for_awards": True, "user": user}
    for sport in models.Sport.objects.filter(**sports_filter).exclude(name="unknown").order_by("name"):
        top_awards[sport] = _get_top_ascent_awards_for_one_sport(sport, user)
    return top_awards


def get_ascent_ranking_of_activity(activity: models.Activity) -> Union[int, None]:
    list_of_ascent_awards = _get_top_ascent_awards_for_one_sport(activity.sport, activity.user)
    if activity in list_of_ascent_awards:
        return list_of_ascent_awards.index(activity) + 1
    else:
        return None


def _get_top_ascent_awards_for_one_sport(sport: models.Sport, user) -> list:
    return list(
        (
            models.Activity.objects.filter(
                sport=sport,
                user=user,
                evaluates_for_awards=True,
            )
            .exclude(trace_file__total_ascent=None)
            .order_by("-trace_file__total_ascent")[: cfg.rank_limit]
        )
    )


def _get_best_sections_of_sport_and_distance(
    sport: models.Sport, user, distance: int, top_score: int, kinds: List[str]
) -> List[models.BestSection]:
    awards_per_distance = list(
        models.BestSection.objects.filter(
            activity__sport=sport,
            activity__user=user,
            activity__evaluates_for_awards=True,
            distance=distance,
            kind__in=kinds,
        ).order_by("-max_value")[:top_score]
    )
    return awards_per_distance


def get_top_awards_for_one_sport(sport: models.Sport, user, top_score: int, kinds: List[str]) -> List[models.BestSection]:
    awards = []
    for bs in cfg.best_sections:
        if bs.kind in kinds:
            for distance in bs.distances:
                awards_per_distance = _get_best_sections_of_sport_and_distance(sport, user, distance, top_score, kinds)
                for rank, section in enumerate(awards_per_distance):
                    setattr(section, "rank", rank + 1)
                if awards_per_distance:
                    awards += awards_per_distance
    return awards


def get_top_awards_for_all_sports(user, top_score: int, kinds: List[str]) -> Dict[models.Sport, List[models.BestSection]]:
    top_awards = {}
    sports_filter = {"evaluates_for_awards": True, "user": user}
    for sport in models.Sport.objects.filter(**sports_filter).exclude(name="unknown").order_by("name"):
        awards = get_top_awards_for_one_sport(sport, user, top_score, kinds)
        if awards:
            top_awards[sport] = awards
    return top_awards
