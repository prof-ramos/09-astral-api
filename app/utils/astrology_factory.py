"""
Optimized astrology calculation factory with caching and async support
"""

import asyncio
from typing import Optional, Dict, Any
from kerykeion import AstrologicalSubject
from .async_helpers import run_in_thread_pool, async_cached
from ..middleware.caching import cache_result


class OptimizedAstrologicalSubjectFactory:
    """Factory for creating AstrologicalSubject instances with caching and validation"""

    @staticmethod
    def _validate_subject_data(subject_data) -> Dict[str, Any]:
        """Validate and clean subject data"""
        required_fields = ["name", "year", "month", "day", "hour", "minute", "city", "nation"]

        for field in required_fields:
            if not hasattr(subject_data, field) or getattr(subject_data, field) is None:
                raise ValueError(f"Missing required field: {field}")

        return {
            "name": subject_data.name,
            "year": subject_data.year,
            "month": subject_data.month,
            "day": subject_data.day,
            "hour": subject_data.hour,
            "minute": subject_data.minute,
            "city": subject_data.city,
            "nation": subject_data.nation,
            "lat": subject_data.latitude,
            "lng": subject_data.longitude,
            "tz_str": subject_data.timezone,
            "zodiac_type": getattr(subject_data, "zodiac_type", "Tropical"),
            "sidereal_mode": getattr(subject_data, "sidereal_mode", "LAHIRI"),
            "houses_system_identifier": getattr(subject_data, "houses_system_identifier", "P"),
            "perspective_type": getattr(subject_data, "perspective_type", "geocentric"),
            "geonames_username": getattr(subject_data, "geonames_username", None),
            "online": bool(getattr(subject_data, "geonames_username", None)),
        }

    @staticmethod
    @cache_result(ttl=600)  # Cache for 10 minutes
    def _create_astrological_subject_sync(subject_params: Dict[str, Any]) -> AstrologicalSubject:
        """Create AstrologicalSubject synchronously (to be run in thread pool)"""
        return AstrologicalSubject(**subject_params)

    @classmethod
    async def create_astrological_subject(cls, subject_data) -> AstrologicalSubject:
        """Create AstrologicalSubject asynchronously with caching"""
        # Validate and prepare data
        subject_params = cls._validate_subject_data(subject_data)

        # Create subject in thread pool to avoid blocking
        return await run_in_thread_pool(cls._create_astrological_subject_sync, subject_params)

    @classmethod
    async def create_multiple_subjects(cls, subjects_data: list) -> list[AstrologicalSubject]:
        """Create multiple AstrologicalSubject instances concurrently"""
        tasks = [cls.create_astrological_subject(subject) for subject in subjects_data]
        return await asyncio.gather(*tasks)


class ChartGenerationFactory:
    """Factory for generating charts with performance optimizations"""

    @staticmethod
    @cache_result(ttl=600)  # Cache charts for 10 minutes
    def _generate_chart_sync(subject: AstrologicalSubject, chart_params: Dict[str, Any]) -> str:
        """Generate chart synchronously (to be run in thread pool)"""
        from kerykeion import KerykeionChartSVG
        from kerykeion.settings.config_constants import DEFAULT_ACTIVE_POINTS, DEFAULT_ACTIVE_ASPECTS

        chart = KerykeionChartSVG(
            subject,
            second_obj=chart_params.get("second_obj"),
            chart_type=chart_params.get("chart_type", "Natal"),
            theme=chart_params.get("theme", "classic"),
            chart_language=chart_params.get("language", "EN"),
            active_points=chart_params.get("active_points", DEFAULT_ACTIVE_POINTS),
            active_aspects=chart_params.get("active_aspects", DEFAULT_ACTIVE_ASPECTS),
        )

        if chart_params.get("wheel_only", False):
            return chart.makeWheelOnlyTemplate(minify=True)
        else:
            return chart.makeTemplate(minify=True)

    @classmethod
    async def generate_chart(cls, subject: AstrologicalSubject, **kwargs) -> str:
        """Generate chart asynchronously"""
        chart_params = {
            "second_obj": kwargs.get("second_obj"),
            "chart_type": kwargs.get("chart_type", "Natal"),
            "theme": kwargs.get("theme", "classic"),
            "language": kwargs.get("language", "EN"),
            "active_points": kwargs.get("active_points"),
            "active_aspects": kwargs.get("active_aspects"),
            "wheel_only": kwargs.get("wheel_only", False),
        }

        return await run_in_thread_pool(cls._generate_chart_sync, subject, chart_params)


class AspectsCalculationFactory:
    """Factory for calculating aspects with performance optimizations"""

    @staticmethod
    @cache_result(ttl=600)  # Cache aspects for 10 minutes
    def _calculate_natal_aspects_sync(subject: AstrologicalSubject, aspects_params: Dict[str, Any]) -> list:
        """Calculate natal aspects synchronously"""
        from kerykeion import NatalAspects
        from kerykeion.settings.config_constants import DEFAULT_ACTIVE_POINTS, DEFAULT_ACTIVE_ASPECTS

        aspects = NatalAspects(
            subject,
            active_points=aspects_params.get("active_points", DEFAULT_ACTIVE_POINTS),
            active_aspects=aspects_params.get("active_aspects", DEFAULT_ACTIVE_ASPECTS),
        )
        return aspects.relevant_aspects

    @staticmethod
    @cache_result(ttl=600)
    def _calculate_synastry_aspects_sync(first_subject: AstrologicalSubject,
                                       second_subject: AstrologicalSubject,
                                       aspects_params: Dict[str, Any]) -> list:
        """Calculate synastry aspects synchronously"""
        from kerykeion import SynastryAspects
        from kerykeion.settings.config_constants import DEFAULT_ACTIVE_POINTS, DEFAULT_ACTIVE_ASPECTS

        aspects = SynastryAspects(
            first_subject,
            second_subject,
            active_points=aspects_params.get("active_points", DEFAULT_ACTIVE_POINTS),
            active_aspects=aspects_params.get("active_aspects", DEFAULT_ACTIVE_ASPECTS),
        )
        return aspects.relevant_aspects

    @classmethod
    async def calculate_natal_aspects(cls, subject: AstrologicalSubject, **kwargs) -> list:
        """Calculate natal aspects asynchronously"""
        aspects_params = {
            "active_points": kwargs.get("active_points"),
            "active_aspects": kwargs.get("active_aspects"),
        }
        return await run_in_thread_pool(cls._calculate_natal_aspects_sync, subject, aspects_params)

    @classmethod
    async def calculate_synastry_aspects(cls, first_subject: AstrologicalSubject,
                                       second_subject: AstrologicalSubject, **kwargs) -> list:
        """Calculate synastry aspects asynchronously"""
        aspects_params = {
            "active_points": kwargs.get("active_points"),
            "active_aspects": kwargs.get("active_aspects"),
        }
        return await run_in_thread_pool(
            cls._calculate_synastry_aspects_sync,
            first_subject,
            second_subject,
            aspects_params
        )


class RelationshipScoreFactory:
    """Factory for calculating relationship scores with caching"""

    @staticmethod
    @cache_result(ttl=600)
    def _calculate_relationship_score_sync(first_subject: AstrologicalSubject,
                                         second_subject: AstrologicalSubject) -> Dict[str, Any]:
        """Calculate relationship score synchronously"""
        from kerykeion import RelationshipScoreFactory as KerykeionScoreFactory

        score_factory = KerykeionScoreFactory(first_subject, second_subject)
        score_model = score_factory.get_relationship_score()

        return {
            "score_value": score_model.score_value,
            "score_description": score_model.score_description,
            "is_destiny_sign": score_model.is_destiny_sign,
            "aspects": [aspect.model_dump() for aspect in score_model.aspects],
        }

    @classmethod
    async def calculate_relationship_score(cls, first_subject: AstrologicalSubject,
                                         second_subject: AstrologicalSubject) -> Dict[str, Any]:
        """Calculate relationship score asynchronously"""
        return await run_in_thread_pool(
            cls._calculate_relationship_score_sync,
            first_subject,
            second_subject
        )


class CompositeFactory:
    """Factory for creating composite charts with caching"""

    @staticmethod
    @cache_result(ttl=600)
    def _create_composite_subject_sync(first_subject: AstrologicalSubject,
                                     second_subject: AstrologicalSubject):
        """Create composite subject synchronously"""
        from kerykeion import CompositeSubjectFactory

        composite_factory = CompositeSubjectFactory(first_subject, second_subject)
        return composite_factory.get_midpoint_composite_subject_model()

    @classmethod
    async def create_composite_subject(cls, first_subject: AstrologicalSubject,
                                     second_subject: AstrologicalSubject):
        """Create composite subject asynchronously"""
        return await run_in_thread_pool(
            cls._create_composite_subject_sync,
            first_subject,
            second_subject
        )