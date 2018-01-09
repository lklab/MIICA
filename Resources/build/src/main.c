#include "os.h"
#include "io.h"

#include "uppaal.h"
#include "model.h"

#ifndef PERIOD
#define PERIOD 10000000LL // 10ms
#endif

static void task_proc(void);
static void interrupt_handler(void);
static void cleanup_and_exit(int value);

static os_task_t task;
static int init_level = 0;

int main(void)
{
	int ret;

	ret = io_init();
	if(ret != 0) cleanup_and_exit(ret);
	init_level = 1;

	ret = io_mapping(mapping_list, mapping_count);
	if(ret != 0) cleanup_and_exit(ret);

	ret = uppaal_init();
	if(ret != 0) cleanup_and_exit(ret);
	init_level = 2;

	ret = os_signal(interrupt_handler);
	if(ret != 0) cleanup_and_exit(ret);

	ret = os_task_init(&task, task_proc, PERIOD);
	if(ret != 0) cleanup_and_exit(ret);
	init_level = 3;

	ret = io_activate(PERIOD);
	if(ret != 0) cleanup_and_exit(ret);

	ret = os_task_start(&task);
	if(ret != 0) cleanup_and_exit(ret);

	return 0;
}

static void task_proc(void)
{
	int ret;

	ret = io_exchange();
	if(ret != 0) cleanup_and_exit(ret);

	ret = uppaal_step();
	if(ret != 0) cleanup_and_exit(ret);
}

static void interrupt_handler(void)
{
	cleanup_and_exit(0);
}

static void cleanup_and_exit(int value)
{
	if(init_level >= 3) os_task_stop(&task);
	if(init_level >= 2) uppaal_cleanup();
	if(init_level >= 1) io_cleanup();
	os_exit(value);
}
