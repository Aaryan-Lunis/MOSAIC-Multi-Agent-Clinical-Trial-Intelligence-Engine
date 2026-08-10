import asyncpg
from datetime import datetime
from typing import Any
from config.settings import settings
from config.logging_config import setup_logging

logger = setup_logging(__name__)
# __name__ here = "memory.semantic_store"


class SemanticStore:
    """
    Manages the sponsor knowledge base — credibility profiles
    built up over time as MOSAIC analyses more studies.

    Each sponsor gets ONE profile row in the sponsor_profiles table.
    That row is updated (never replaced) every time new information
    about that sponsor is discovered during an analysis run.

    Think of it as a living document about each sponsor —
    it grows richer with every analysis, never starts from scratch.

    Usage:
        store = SemanticStore()

        # Get what we know about a sponsor
        profile = await store.get_sponsor_profile("Novo Nordisk")

        # Update after analysing a study
        await store.update_sponsor_knowledge(
            sponsor="Novo Nordisk",
            results_posted=True,
            had_broken_promise=False,
            delay_days=5
        )
    """

    def __init__(self):
        logger.info("SemanticStore initialised")

    # PRIVATE HELPER: _ensure_pool

    async def _ensure_pool(self) -> None:
        """
        Creates the connection pool if it does not exist yet.
        Called at the start of every public method.
        Same pattern as EpisodicStore and ProceduralStore.
        """

        if self._pool is not None:
            # Pool already open — nothing to do.
            return

        self._pool = await asyncpg.create_pool(
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,

            min_size=1,
            max_size=5,
        )

        logger.info("SemanticStore pool created")

    # CORE METHOD: get_sponsor_profile

    async def get_sponsor_profile(
        self,
        sponsor: str,

    ) -> dict[str, Any] | None:
        """
        Retrieves everything we know about a specific sponsor.

        WHAT IS RETURNED:
        A dictionary containing the sponsor's full profile:
          - sponsor           → the sponsor's name
          - credibility_score → 0.0 (worst) to 1.0 (best)
          - total_studies     → how many studies we have analysed
          - results_posted    → how many times they posted results on time
          - results_missing   → how many times results were NOT posted
          - broken_promises   → how many outcome switches detected
          - avg_delay_days    → average days late on timeline
          - last_updated      → when this profile was last modified

        HOW THE CREDIBILITY SCORE IS CALCULATED:
        It is not a simple average — it weights different factors:
          70% → results compliance rate (posted / total studies)
          30% → promise keeping (reduced per broken promise)
        Range: 0.0 to 1.0. Below 0.6 triggers a LOW_CREDIBILITY signal.

        Args:
            sponsor: The sponsor name to look up.

        Returns:
            Dictionary with all profile fields, or None if not found.
        """

        await self._ensure_pool()

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    sponsor,
                    credibility_score,
                    total_studies,
                    results_posted,
                    results_missing,
                    broken_promises,
                    avg_delay_days,
                    last_updated
                FROM sponsor_profiles
                WHERE sponsor = $1
                """,
                sponsor,
                # $1 — the sponsor name to filter by.
            )

        if row is None:
            logger.info(
                f"No profile found for sponsor | sponsor={sponsor}"
            )
            return None

        return {
            "sponsor":           row["sponsor"],
            # The sponsor name — same string we searched for.

            "credibility_score": float(row["credibility_score"] or 0.0),

            "total_studies":     int(row["total_studies"] or 0),

            "results_posted":    int(row["results_posted"] or 0),

            "results_missing":   int(row["results_missing"] or 0),

            "broken_promises":   int(row["broken_promises"] or 0),

            "avg_delay_days":    float(row["avg_delay_days"] or 0.0),

            "last_updated":      str(row["last_updated"]),
        }

    # CORE METHOD: update_sponsor_knowledge

    async def update_sponsor_knowledge(
        self,
        sponsor: str,

        results_posted: bool = False,

        had_broken_promise: bool = False,

        delay_days: int = 0,

    ) -> None:
        """
        Updates a sponsor's profile with new information from one study.

        USES THE UPSERT PATTERN:
        "UPSERT" = INSERT if the sponsor does not exist,
                   UPDATE if they already do.
        PostgreSQL does this in one statement using:
        INSERT ... ON CONFLICT ... DO UPDATE

        This is more efficient and safer than checking first with
        SELECT, then deciding whether to INSERT or UPDATE.
        The two-step approach has a "race condition" — two agents
        running in parallel could both check, both see "not exists",
        and both try to INSERT, causing a duplicate key error.
        UPSERT handles this atomically — it is thread-safe.

        HOW THE CREDIBILITY SCORE IS RECALCULATED:
        After updating the counts, we recalculate credibility:
          compliance_rate = results_posted_count / total_studies
          promise_penalty = broken_promises * 0.1
          credibility = (compliance_rate * 0.7) - promise_penalty
          credibility = max(0.0, min(1.0, credibility))
          (clamped between 0.0 and 1.0 — cannot go negative or above 1)

        Args:
            sponsor:            The sponsor name.
            results_posted:     Whether results were posted for this study.
            had_broken_promise: Whether outcome switching was detected.
            delay_days:         How many days late this study was.
        """

        await self._ensure_pool()

        async with self._pool.acquire() as conn:

            # ── STEP 1: UPSERT THE SPONSOR PROFILE ────────────
            await conn.execute(
                """
                INSERT INTO sponsor_profiles (
                    sponsor,
                    credibility_score,
                    total_studies,
                    results_posted,
                    results_missing,
                    broken_promises,
                    avg_delay_days,
                    last_updated
                )
                VALUES ($1, 0.5, 1, $2, $3, $4, $5, NOW())
                ON CONFLICT (sponsor) DO UPDATE SET
                    total_studies   = sponsor_profiles.total_studies + 1,
                    results_posted  = sponsor_profiles.results_posted + $2,
                    results_missing = sponsor_profiles.results_missing + $3,
                    broken_promises = sponsor_profiles.broken_promises + $4,
                    avg_delay_days  = (
                        (sponsor_profiles.avg_delay_days *
                         sponsor_profiles.total_studies) + $5
                    ) / (sponsor_profiles.total_studies + 1),
                    last_updated    = NOW()
                """,
                sponsor,

                int(results_posted),

                int(not results_posted),

                int(had_broken_promise),

                float(delay_days),
            )


            await conn.execute(
                """
                UPDATE sponsor_profiles
                SET credibility_score = GREATEST(0.0, LEAST(1.0,
                    (
                        CASE
                            WHEN total_studies = 0 THEN 0.5
                            ELSE (results_posted::float / total_studies) * 0.7
                        END
                    ) - (broken_promises * 0.1)
                ))
                WHERE sponsor = $1
                """,
                sponsor,
            )

        logger.info(
            f"Sponsor knowledge updated | "
            f"sponsor={sponsor} | "
            f"results_posted={results_posted} | "
            f"broken_promise={had_broken_promise} | "
            f"delay_days={delay_days}"
        )

    # UTILITY METHOD: get_low_credibility_sponsors

    async def get_low_credibility_sponsors(
        self,
        threshold: float = 0.6,

        min_studies: int = 3,

    ) -> list[dict]:
        """
        Returns all sponsors whose credibility is below the threshold.

        Used by:
        1. The Track Record agent — to quickly identify problematic sponsors
        2. The Pattern Finder agent — to check if a sponsor is a repeat offender
        3. The API endpoint GET /api/v1/sponsors — for analyst dashboards

        Args:
            threshold:   Credibility below this score qualifies as "low".
            min_studies: Minimum studies needed before flagging a sponsor.

        Returns:
            List of sponsor profile dicts ordered by credibility ascending.
            Lowest credibility (worst) sponsors appear first.
        """

        await self._ensure_pool()

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    sponsor,
                    credibility_score,
                    total_studies,
                    results_posted,
                    results_missing,
                    broken_promises,
                    avg_delay_days,
                    last_updated
                FROM sponsor_profiles
                WHERE credibility_score < $1
                  AND total_studies >= $2
                ORDER BY credibility_score ASC
                """,
                threshold,

                min_studies,
            )

        sponsors = [
            {
                "sponsor":           row["sponsor"],
                "credibility_score": float(row["credibility_score"] or 0.0),
                "total_studies":     int(row["total_studies"] or 0),
                "results_posted":    int(row["results_posted"] or 0),
                "results_missing":   int(row["results_missing"] or 0),
                "broken_promises":   int(row["broken_promises"] or 0),
                "avg_delay_days":    float(row["avg_delay_days"] or 0.0),
                "last_updated":      str(row["last_updated"]),
            }
            for row in rows
        ]

        logger.info(
            f"Low credibility sponsors found | "
            f"count={len(sponsors)} | "
            f"threshold={threshold} | "
            f"min_studies={min_studies}"
        )

        return sponsors

    # UTILITY METHOD: get_all_sponsor_profiles

    async def get_all_sponsor_profiles(
        self,
        limit: int = 50,

    ) -> list[dict]:
        """
        Returns all sponsor profiles ordered by credibility.

        Used by the API for analytics dashboards — showing analysts
        the full picture of every sponsor we have knowledge about.

        Args:
            limit: Maximum profiles to return.

        Returns:
            List of all sponsor profiles, lowest credibility first.
        """

        await self._ensure_pool()

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    sponsor,
                    credibility_score,
                    total_studies,
                    results_posted,
                    results_missing,
                    broken_promises,
                    avg_delay_days,
                    last_updated
                FROM sponsor_profiles
                ORDER BY credibility_score ASC
                LIMIT $1
                """,
                limit,
            )

        return [
            {
                "sponsor":           row["sponsor"],
                "credibility_score": float(row["credibility_score"] or 0.0),
                "total_studies":     int(row["total_studies"] or 0),
                "results_posted":    int(row["results_posted"] or 0),
                "results_missing":   int(row["results_missing"] or 0),
                "broken_promises":   int(row["broken_promises"] or 0),
                "avg_delay_days":    float(row["avg_delay_days"] or 0.0),
                "last_updated":      str(row["last_updated"]),
            }
            for row in rows
        ]

    # UTILITY METHOD: sponsor_exists

    async def sponsor_exists(self, sponsor: str) -> bool:
        """
        Checks if a sponsor profile already exists in the database.

        Used before creating a new profile — avoids duplicate entries.
        Also used by agents to decide whether to load a profile or
        note that "we have never seen this sponsor before."

        Args:
            sponsor: The sponsor name to check.

        Returns:
            True if a profile exists, False if this is a new sponsor.
        """

        await self._ensure_pool()

        async with self._pool.acquire() as conn:
            count = await conn.fetchval(

                "SELECT COUNT(*) FROM sponsor_profiles WHERE sponsor = $1",
                sponsor,
            )

        return (count or 0) > 0

    # CLEANUP METHOD: close

    async def close(self) -> None:
        """
        Closes the connection pool gracefully.
        Call this when the application shuts down.
        """

        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("SemanticStore pool closed")