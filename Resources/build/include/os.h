#ifndef _OS_H
#define _OS_H

typedef void (*os_proc_t)(void);
typedef void (*os_func_t)(void);

typedef struct
{
	os_proc_t proc;
	unsigned long long period;
	int alive;
} task_t;

int os_task_init(task_t* task, os_proc_t proc, unsigned long long period);
int os_task_start(task_t* task);
int os_task_stop(task_t* task);

int os_register_interrupt_handler(os_func_t handler);
void os_exit_process(int value);
void* os_memcpy(void *s1, const void *s2, unsigned int n);
void* os_malloc(unsigned int size);
void os_free(void *ptr);

#endif
