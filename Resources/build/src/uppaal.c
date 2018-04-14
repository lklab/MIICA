#include "os.h"

#include "uppaal_types.h"
#include "model.h"

static int committed_location_processing();
static int normal_location_processing();

static int take_valid_transition(Template* process);

static int check_and_take_broadcast_channel(Template* send_process, Transition* send_transition);
static int find_sending_broadcast_and_take(Template* receive_process, Transition* receive_transition);
static int check_and_take_normal_channel(Template* send_process, Transition* send_transition);
static int check_invariant_and_take_if_true(Template* process, Transition* transition);

static int backup_context_and_take_update(Template* process, Transition* transition, int backup_program_context);
static int restore_context(Template* process, Transition* transition, int restore_program_context);

static int check_guard(Template* process, Transition* transition);
static int check_validation_for_next_period();

int uppaal_init(void)
{
	return 0;
}

int uppaal_step(void)
{
	userPeriodicFunc();

	/* dataExchanged channel processing */
	if(!check_and_take_broadcast_channel(NULL, NULL))
		return 1; /* deadlock condition */

	/* 
	 * Normal and urgent locations are semantically identical
	 * according to the non-determinism implementation policy
	 */
	do
	{
		/* Process all committed locations first */
		if(!committed_location_processing())
			return 1; /* deadlock condition */
	}
	/*
	 * If one of the processed processes exists,
	 * the committed location is checked and processed again
	 */
	while(normal_location_processing());

	if(!check_validation_for_next_period())
		return 1; /* deadlock condition */

	program.program_clock++;

	return 0;
}

int uppaal_cleanup(void)
{
	return 0;
}

static int committed_location_processing()
{
	int i;
	int state_changed = 0;
	int all_committed_proceeded = 1;

	Template* process;

	do
	{
		state_changed = 0;
		all_committed_proceeded = 1;

		for(i = 0; program.process_list[i] != NULL; i++)
		{
			process = program.process_list[i];

			if(process -> current -> mode == LOCATION_COMMITTED)
			{
				state_changed |= take_valid_transition(process);
				all_committed_proceeded = 0;
			}
		}

		if(!state_changed && !all_committed_proceeded)
			return 0; /* deadlock condition */
	}
	while(!all_committed_proceeded);

	return 1;
}

static int normal_location_processing()
{
	int i;

	for(i = 0; program.process_list[i] != NULL; i++)
	{
		if(take_valid_transition(program.process_list[i]))
			return 1;
	}

	return 0;
}

/*
 * Take a valid transition of outgoing transitions
 * of the current location for the current process
 *
 * Returns 1 if the transition has been taken
 * Returns 0 if there is no taken transition since there are no valid transitions
 */
static int take_valid_transition(Template* process)
{
	int i;

	Transition** transitions = process -> current -> transitions;
	Transition* transition;

	for(i = 0; transitions[i] != NULL; i++)
	{
		transition = transitions[i];

		if(!check_guard(process, transition))
			continue;

		if(transition -> chan_in != NULL)
		{
			switch(transition -> chan_in -> mode)
			{
				/* 
				 * Normal and urgent channels are semantically identical
				 * according to the non-determinism implementation policy
				 */
				case CHANNEL_NORMAL :
				case CHANNEL_URGENT :
					if(check_and_take_normal_channel(process, transition))
						return 1;
					break;
				case CHANNEL_BROADCAST :
					if(find_sending_broadcast_and_take(process, transition))
						return 1;
					break;
				default :
					break;
			}
			continue;
		}

		if(transition -> chan_out != NULL)
		{
			switch(transition -> chan_out -> mode)
			{
				case CHANNEL_NORMAL :
				case CHANNEL_URGENT :
					if(check_and_take_normal_channel(process, transition))
						return 1;
					break;
				case CHANNEL_BROADCAST :
					if(check_and_take_broadcast_channel(process, transition))
						return 1;
					break;
				default :
					break;
			}
			continue;
		}

		if(check_invariant_and_take_if_true(process, transition))
			return 1;
		else
			continue;
	}

	return 0;
}

static int check_and_take_broadcast_channel(Template* send_process, Transition* send_transition)
{
	/* 
	 * WARNING : Current code may behave differently than UPPAAL.
	 * This happens when there are two or more transitions receiving
	 * broadcast channels at the current location, and the outcome of any
	 * invariant in the system depends on which transition is selected.
	 *
	 * Avoid receiving the same broadcast channel for two or more
	 * transitions where the execution condition is not exclusively
	 * determined by the guard at any position.
	 */

	int i, j;
	int result = 1;
	int is_data_exchanged;

	Template* process;
	Transition* transition;
	Channel* send_channel;

	finvariant_t invariant;

	if(send_process == NULL || send_transition == NULL)
	{
		send_channel = data_exchanged;
		is_data_exchanged = 1;
	}
	else
	{
		send_channel = send_transition -> chan_out;
		is_data_exchanged = 0;
	}

	if(send_channel == NULL)
		return 0;

	/* 1st step : check guard */
	if(!is_data_exchanged)
	{
		if(!check_guard(send_process, send_transition))
			return 0;
	}
	for(i = 0; program.process_list[i] != NULL; i++)
	{
		process = program.process_list[i];
		process -> ready = NULL;
		if(process == send_process)
			continue;

		for(j = 0; process -> current -> transitions[j] != NULL; j++)
		{
			transition = process -> current -> transitions[j];
			if(transition -> chan_in == send_channel)
			{
				if(check_guard(process, transition))
				{
					process -> ready = transition;
					break;
				}
			}
		}
	}

	/* 2nd step : backup context and take update for invariant check */
	os_memcpy(program.context_backup, program.context, program.context_size);
	if(!is_data_exchanged)
		backup_context_and_take_update(send_process, send_transition, 0);
	for(i = 0; program.process_list[i] != NULL; i++)
	{
		process = program.process_list[i];
		if(process -> ready == NULL)
			continue;
		backup_context_and_take_update(process, process -> ready, 0);
	}

	/* 3rd step : check invariant */
	for(i = 0; program.process_list[i] != NULL; i++)
	{
		process = program.process_list[i];

		if(process -> ready != NULL)
			invariant = process -> ready -> target -> invariant;
		else
		{
			if(!is_data_exchanged && (process == send_process))
				invariant = send_transition -> target -> invariant;
			else
				invariant = process -> current -> invariant;
		}

		if(invariant != NULL && !invariant(process -> context, 0))
		{
			result = 0;
			break;
		}
	}

	/* 4th step */
	if(result) /* take transtion if invariant is true */
	{
		if(!is_data_exchanged)
			send_process -> current = send_transition -> target;

		for(i = 0; program.process_list[i] != NULL; i++)
		{
			process = program.process_list[i];
			if(process -> ready != NULL)
				process -> current = process -> ready -> target;
		}
	}
	else /* restore context if invariant is false */
	{
		os_memcpy(program.context, program.context_backup, program.context_size);
		if(!is_data_exchanged)
			restore_context(send_process, send_transition, 0);
		for(i = 0; program.process_list[i] != NULL; i++)
		{
			process = program.process_list[i];
			if(process -> ready != NULL)
				restore_context(process, process -> ready, 0);
		}
	}

	return result;
}

static int find_sending_broadcast_and_take(Template* receive_process, Transition* receive_transition)
{
	int i, j;

	Template* process;
	Transition* transition;
	Channel* receive_channel;

	if(!check_guard(receive_process, receive_transition))
		return 0;
	receive_channel = receive_transition -> chan_in;
	if(receive_channel == NULL)
		return 0;

	for(i = 0; program.process_list[i] != NULL; i++)
	{
		process = program.process_list[i];
		if(process == receive_process)
			continue;

		for(j = 0; process -> current -> transitions[j] != NULL; j++)
		{
			transition = process -> current -> transitions[j];
			if(transition -> chan_out == receive_channel)
			{
				if(check_and_take_broadcast_channel(process, transition))
					return 1;
				else
					continue;
			}
		}
	}

	return 0;
}

static int check_and_take_normal_channel(Template* ref_process, Transition* ref_transition)
{
	int i, j, k;
	int invariant_result;
	int ref_invariant_result = 1;
	int find_send;

	Template* process;
	Transition* transition;
	Template** send_process;
	Transition** send_transition;
	Template** receive_process;
	Transition** receive_transition;
	Channel* ref_channel;

	finvariant_t invariant;

	if(!check_guard(ref_process, ref_transition))
		return 0;

	if(ref_transition -> chan_in != NULL)
	{
		ref_channel = ref_transition -> chan_in;
		send_process = &process;
		send_transition = &transition;
		receive_process = &ref_process;
		receive_transition = &ref_transition;
		find_send = 1;
	}
	else if(ref_transition -> chan_out != NULL)
	{
		ref_channel = ref_transition -> chan_out;
		send_process = &ref_process;
		send_transition = &ref_transition;
		receive_process = &process;
		receive_transition = &transition;
		find_send = 0;
	}
	else
		return 0;

	if(ref_transition -> update == NULL)
	{
		invariant = ref_transition -> target -> invariant;
		if(invariant != NULL && !invariant(ref_process -> context, 0))
			ref_invariant_result = 0;
	}

	for(i = 0; program.process_list[i] != NULL; i++)
	{
		process = program.process_list[i];
		if(process == ref_process)
			continue;

		for(j = 0; process -> current -> transitions[j] != NULL; j++)
		{
			transition = process -> current -> transitions[j];

			if((find_send && (transition -> chan_out == ref_channel)) ||
				(!find_send && (transition -> chan_in == ref_channel)))
			{
				/* guard check */
				if(!check_guard(process, transition))
					continue;

				/* if there is no update, check only invariant in the next location */
				if(!ref_invariant_result && transition -> update == NULL)
				{
					invariant = transition -> target -> invariant;
					if(invariant != NULL && !invariant(process -> context, 0))
						continue;
				}

				/* backup context and take update for invariant check*/
				os_memcpy(program.context_backup, program.context, program.context_size);
				backup_context_and_take_update(*send_process, *send_transition, 0);
				backup_context_and_take_update(*receive_process, *receive_transition, 0);

				/* invariant check */
				invariant_result = 1;
				for(k = 0; program.process_list[k] != NULL; k++)
				{
					if(program.process_list[k] == ref_process)
						invariant = ref_transition -> target -> invariant;
					else if(program.process_list[k] == process)
						invariant = transition -> target -> invariant;
					else
						invariant = program.process_list[k] -> current -> invariant;

					if(invariant != NULL && !invariant(program.process_list[k] -> context, 0))
					{
						invariant_result = 0;
						break;
					}
				}

				if(invariant_result) /* take transtion if invariant is true */
				{
					ref_process -> current = ref_transition -> target;
					process -> current = transition -> target;
					return 1;
				}
				else /* restore context if invariant is false */
				{
					os_memcpy(program.context, program.context_backup, program.context_size);
					restore_context(*send_process, *send_transition, 0);
					restore_context(*receive_process, *receive_transition, 0);
					continue;
				}
			}
		}
	}

	return 0;
}

static int check_invariant_and_take_if_true(Template* process, Transition* transition)
{
	int i;

	finvariant_t invariant;

	if(backup_context_and_take_update(process, transition, 1))
	{
		/* check all invariants */
		for(i = 0; program.process_list[i] != NULL; i++)
		{
			if(program.process_list[i] == process)
				invariant = transition -> target -> invariant;
			else
				invariant = program.process_list[i] -> current -> invariant;

			if(invariant != NULL && !invariant(program.process_list[i] -> context, 0))
			{
				restore_context(process, transition, 1);
				return 0;
			}
		}

		process -> current = transition -> target;
		return 1;
	}
	else
	{
		/* if there is no update, check only invariant in the next location */
		invariant = transition -> target -> invariant;
		if(invariant == NULL || invariant(process -> context, 0))
		{
			process -> current = transition -> target;
			return 1;
		}
		else
			return 0;
	}
}

static int backup_context_and_take_update(Template* process, Transition* transition, int backup_program_context)
{
	if(transition -> update != NULL)
	{
		if(backup_program_context)
			os_memcpy(program.context_backup, program.context, program.context_size);
		os_memcpy(process -> context_backup, process -> context, process -> context_size);
		transition -> update(process -> context);
		return 1;
	}
	return 0;
}

static int restore_context(Template* process, Transition* transition, int restore_program_context)
{
	if(transition -> update != NULL)
	{
		if(restore_program_context)
			os_memcpy(program.context, program.context_backup, program.context_size);
		os_memcpy(process -> context, process -> context_backup, process -> context_size);
		return 1;
	}
	return 0;
}

static int check_guard(Template* process, Transition* transition)
{
	fguard_t guard = transition -> guard;

	if(guard == NULL || guard(process -> context))
		return 1;
	else
		return 0;
}

static int check_validation_for_next_period()
{
	int i;
	Template* process;

	for(i = 0; program.process_list[i] != NULL; i++)
	{
		process = program.process_list[i];
		if(process -> current -> mode == LOCATION_COMMITTED ||
			process -> current -> mode == LOCATION_URGENT)
			return 0;

		if(process -> current -> invariant != NULL)
		{
			if(!(process -> current -> invariant(process -> context, 1)))
				return 0;
		}
	}

	return 1;
}
