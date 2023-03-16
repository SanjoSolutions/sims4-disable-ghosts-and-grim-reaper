import sims4.log
from interactions import ParticipantType
from interactions.base.super_interaction import SuperInteraction
from interactions.interaction_finisher import FinishingType
from interactions.utils.death import DEATH_INTERACTION_MARKER_ATTRIBUTE
from interactions.utils.death_interactions import DeathSuperInteraction
from interactions.utils.outcome_enums import OutcomeResult
from objects.object_creation import CreationDataBase, ObjectCreationParams
from sims.ghost import Ghost

logger = sims4.log.Logger('DisableGhostsAndGrimReaper', default_owner='Sanjo')
logger.info('loaded')


def on_added_to_queue(self, *args, **kwargs):
    logger.info('on_added_to_queue')
    setattr(self.sim, DEATH_INTERACTION_MARKER_ATTRIBUTE, self)
    return SuperInteraction.on_added_to_queue(self, *args, **kwargs)


DeathSuperInteraction.on_added_to_queue = on_added_to_queue


def _exited_pipeline(self, *args, **kwargs):
    try:
        should_die_on_transition_failure = self.should_die_on_transition_failure
        SuperInteraction._exited_pipeline(self, *args, **kwargs)
    finally:
        try:
            if self.finishing_type == FinishingType.TRANSITION_FAILURE or self.finishing_type == FinishingType.USER_CANCEL or self.finishing_type == FinishingType.FAILED_TESTS:
                if not should_die_on_transition_failure:
                    return
            if self.global_outcome_result != OutcomeResult.SUCCESS:
                self.run_death_behavior(from_reset=True)
        finally:
            delattr(self.sim, DEATH_INTERACTION_MARKER_ATTRIBUTE)


DeathSuperInteraction._exited_pipeline = _exited_pipeline
