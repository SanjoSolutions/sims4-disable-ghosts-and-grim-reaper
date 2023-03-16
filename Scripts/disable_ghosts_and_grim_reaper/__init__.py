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


class PhysicalBodyCreationData(CreationDataBase):

    def get_definition(*args, **kwargs):
        resolver = args[1]
        sim = resolver.get_participant(ParticipantType.Actor)
        logger.info('sim type: ' + str(type(sim)))
        return Ghost.URNSTONE_DEFINITION.get_definition(*args, **kwargs)

    def get_creation_params(*args, **kwargs):
        logger.info('get_creation_params')
        return ObjectCreationParams(Ghost.URNSTONE_DEFINITION.get_definition(*args, **kwargs), {})

    def setup_created_object(*args, **kwargs):
        logger.info('setup_created_object')
        return Ghost.URNSTONE_DEFINITION.setup_created_object(*args, **kwargs)

    def get_source_object(*args, **kwargs):
        logger.info('get_source_object')
        return Ghost.URNSTONE_DEFINITION.get_source_object(*args, **kwargs)


DeathSuperInteraction.INSTANCE_TUNABLES['death_element'].locked_args['creation_data'] = PhysicalBodyCreationData
